"""Single-case development repair with explicit attempts and verifiable budgets."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.evidence import Digest
from ai_harness_compiler.models.grounded_analysis import GroundedRepairInput
from ai_harness_compiler.models.model_session import SessionPlan, WorkerRequest, WorkerResult
from ai_harness_compiler.models.semantic_eval import UnderstandingEvalReport


class RepairPlan(Contract):
    schema_version: Literal["UnderstandingRepairPlan/v1"] = "UnderstandingRepairPlan/v1"
    session: SessionPlan
    max_repairs: int = Field(default=1, ge=0, le=2)
    repair_prompt_sha256: Digest

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if (
            self.session.split != "development"
            or len(self.session.cases) != 1
            or self.session.settings.repeats != 1
            or self.session.settings.analysis_mode != "grounded"
            or not self.session.settings.expected_model_sha256
        ):
            raise ValueError(
                "Repair requires one development case, one repetition and fixed grounded model"
            )
        from ai_harness_compiler.understanding import prepare_understanding

        prepare_understanding(self.session.cases[0].project)
        return self


class RepairAttempt(Contract):
    index: int = Field(ge=1, le=3)
    request: WorkerRequest
    result: WorkerResult
    started_after_seconds: float = Field(ge=0, allow_inf_nan=False)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    effective_timeout_seconds: float = Field(gt=0, le=300, allow_inf_nan=False)

    @model_validator(mode="after")
    def bind_result(self) -> Self:
        if self.result.status == "completed":
            assert self.result.identity and self.result.understanding
            if (
                self.result.settings != self.request.settings
                or self.result.identity.prompt_sha256 != self.request.prompt_sha256
                or self.result.understanding.request != self.request.request
                or self.result.identity.model_sha256 != self.request.settings.expected_model_sha256
            ):
                raise ValueError("Repair generation differs from attempted request")
        if self.result.failure_diagnostic:
            from ai_harness_compiler.grounding import extract_grounding

            GroundedRepairInput(
                extraction=extract_grounding(self.request.request.original_input),
                feedback=self.result.failure_diagnostic,
            )
        return self


class RepairReport(Contract):
    schema_version: Literal["UnderstandingRepairReport/v1"] = "UnderstandingRepairReport/v1"
    plan: RepairPlan
    attempts: list[RepairAttempt] = Field(max_length=3)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    termination: Literal[
        "completed",
        "repair-limit",
        "not-repairable",
        "attempt-limit",
        "time-limit",
        "worker-timeout",
        "model-changed",
    ]
    evaluation: UnderstandingEvalReport | None = None
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def verify_history(self) -> Self:
        session = self.plan.session
        settings = session.settings
        from ai_harness_compiler.understanding import prepare_understanding

        expected_request = prepare_understanding(session.cases[0].project)
        count = len(self.attempts)
        if count > min(settings.max_attempts, self.plan.max_repairs + 1):
            raise ValueError("Repair exceeds attempt or repair budget")
        previous: RepairAttempt | None = None
        for index, attempt in enumerate(self.attempts, 1):
            request = attempt.request
            if (
                attempt.index != index
                or request.settings != settings
                or request.request != expected_request
                or request.prompt_sha256
                != (session.prompt_sha256 if index == 1 else self.plan.repair_prompt_sha256)
            ):
                raise ValueError("Repair attempt differs from planned scope/sequence/program")
            if index == 1:
                if request.repair_feedback is not None:
                    raise ValueError("First attempt cannot claim prior feedback")
            elif (
                not previous
                or previous.result.status != "error"
                or not previous.result.failure_diagnostic
                or request.repair_feedback != previous.result.failure_diagnostic
            ):
                raise ValueError("Repair must use the preceding failure diagnostic exactly")
            if (
                previous
                and attempt.started_after_seconds
                < previous.started_after_seconds + previous.elapsed_seconds
            ):
                raise ValueError("Repair attempts cannot overlap")
            remaining = settings.session_seconds - attempt.started_after_seconds
            if attempt.effective_timeout_seconds > min(settings.call_timeout_seconds, remaining):
                raise ValueError("Repair timeout exceeds remaining session allowance")
            if self.elapsed_seconds < attempt.started_after_seconds + attempt.elapsed_seconds:
                raise ValueError("Repair elapsed time contradicts attempted work")
            previous = attempt
        last = previous.result if previous else None
        if last and last.status == "completed":
            if self.termination != "completed" or not self.evaluation:
                raise ValueError("Completed repair needs artifact evaluation")
            evaluation = self.evaluation
            if (
                evaluation.case != session.cases[0]
                or evaluation.rubric != session.rubric
                or evaluation.corpus_sha256 != session.corpus_sha256
                or evaluation.split != "development"
                or evaluation.review is not None
                or evaluation.understanding != last.understanding
                or evaluation.status not in {"fail", "not-run"}
                or evaluation.declared_candidate_sha256 != session.declared_candidate_sha256
            ):
                raise ValueError("Repair evaluation differs from actual generation or plan")
        else:
            if self.evaluation is not None or self.termination == "completed":
                raise ValueError("Rejected repair cannot claim completed evaluation")
            if not last and self.termination != "time-limit":
                raise ValueError("Unattempted repair must account for exhausted session time")
            if last and last.error_code not in {"worker-timeout", "model-changed"}:
                if last.failure_diagnostic is None and self.termination != "not-repairable":
                    raise ValueError("Nonrepairable result cannot imply a pending repair")
                if (
                    last.failure_diagnostic
                    and count == self.plan.max_repairs + 1
                    and self.termination != "repair-limit"
                ):
                    raise ValueError("Exhausted repairs cannot imply another pending attempt")
            if self.termination == "attempt-limit" and count != settings.max_attempts:
                raise ValueError("Attempt stopping reason contradicts exhausted budget")
            if self.termination == "time-limit" and self.elapsed_seconds < settings.session_seconds:
                raise ValueError("Time stopping reason contradicts exhausted budget")
            if self.termination == "repair-limit" and (
                count != self.plan.max_repairs + 1 or not last or not last.failure_diagnostic
            ):
                raise ValueError("Repair stopping reason contradicts eligible exhausted repairs")
            if self.termination == "not-repairable" and (
                not last
                or last.failure_diagnostic is not None
                or last.error_code in {"worker-timeout", "model-changed"}
            ):
                raise ValueError("Nonrepairable stopping reason contradicts last result")
            for cause in ("worker-timeout", "model-changed"):
                if (self.termination == cause) != bool(last and last.error_code == cause):
                    raise ValueError("Repair fatal stopping reason differs from result")
        return self
