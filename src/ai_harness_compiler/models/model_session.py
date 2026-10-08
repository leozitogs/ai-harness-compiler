"""Bounded generation sessions; execution evidence never establishes semantic quality."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.grounded_analysis import (
    GroundedAnalysisSpec,
    GroundedRepairInput,
    GroundingDiagnostic,
)
from ai_harness_compiler.models.semantic_eval import (
    UnderstandingEvalCase,
    UnderstandingEvalReport,
    UnderstandingRubric,
)
from ai_harness_compiler.models.understanding import (
    ProjectUnderstandingSpec,
    UnderstandingProposal,
    UnderstandingRequest,
)


class ProviderObservation(Contract):
    returned_model: Text | None = None
    response_sha256: Digest
    total_duration_ns: int | None = Field(default=None, ge=0)
    load_duration_ns: int | None = Field(default=None, ge=0)
    prompt_tokens: int | None = Field(default=None, ge=0)
    output_tokens: int | None = Field(default=None, ge=0)
    prompt_duration_ns: int | None = Field(default=None, ge=0)
    generation_duration_ns: int | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def consistent_durations(self) -> Self:
        if self.total_duration_ns is not None and any(
            value is not None and value > self.total_duration_ns
            for value in (
                self.load_duration_ns,
                self.prompt_duration_ns,
                self.generation_duration_ns,
            )
        ):
            raise ValueError("Provider component duration exceeds total duration")
        return self


class ObservedProposal(Contract):
    proposal: UnderstandingProposal
    observation: ProviderObservation


class SessionSettings(Contract):
    model: Text = Field(max_length=200)
    analysis_mode: Literal["baseline", "grounded"] = "baseline"
    repeats: int = Field(default=1, ge=1, le=3)
    max_attempts: int = Field(default=30, ge=1, le=30)
    session_seconds: int = Field(default=3600, ge=1, le=3600)
    call_timeout_seconds: int = Field(default=180, ge=1, le=300)
    context_tokens: int = Field(default=8192, ge=512, le=32768)
    max_output_tokens: int = Field(default=4096, ge=1, le=16384)
    temperature: Literal[0] = 0
    thinking: Literal[False] = False
    execution: Literal["sequential-isolated-process-no-retries"] = (
        "sequential-isolated-process-no-retries"
    )
    expected_model_sha256: Digest | None = None


class SessionPlan(Contract):
    schema_version: Literal["UnderstandingSessionPlan/v1"] = "UnderstandingSessionPlan/v1"
    settings: SessionSettings
    split: Literal["development", "holdout"] = "development"
    cases: list[UnderstandingEvalCase] = Field(min_length=1, max_length=64)
    rubric: UnderstandingRubric
    corpus_sha256: Digest
    prompt_sha256: Digest
    declared_candidate_sha256: Digest | None = None

    def candidate_digest(self) -> str:
        program = {} if self.settings.analysis_mode == "baseline" else {"analysis_mode": "grounded"}
        return canonical_project_digest(
            {
                **program,
                "model": self.settings.model,
                "model_sha256": self.settings.expected_model_sha256,
                "prompt_sha256": self.prompt_sha256,
                "context_tokens": self.settings.context_tokens,
                "output_tokens": self.settings.max_output_tokens,
                "temperature": 0,
                "thinking": False,
            }
        )

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if len({case.id for case in self.cases}) != len(self.cases):
            raise ValueError("Session case IDs must be unique")
        if self.split == "holdout" and (
            not self.rubric.approval
            or not self.settings.expected_model_sha256
            or self.declared_candidate_sha256 != self.candidate_digest()
        ):
            raise ValueError("Holdout requires reviewed rubric and matching frozen model/program")
        return self


class ModelIdentity(Contract):
    requested_model: Text
    model_sha256: Digest
    parameters_sha256: Digest
    quantization: Text
    family: Text
    model_size_bytes: int = Field(gt=0)
    provider_version: Text
    compiler_version: Text
    compiler_source_sha256: Digest
    python_version: Text
    platform_system: Text
    observed_at: Text
    prompt_sha256: Digest
    provenance: Literal["observed-local-ollama-api-not-authenticated"] = (
        "observed-local-ollama-api-not-authenticated"
    )


class WorkerRequest(Contract):
    settings: SessionSettings
    request: UnderstandingRequest
    prompt_sha256: Digest
    repair_feedback: GroundingDiagnostic | None = None

    @model_validator(mode="after")
    def validate_feedback(self) -> Self:
        if self.repair_feedback:
            from ai_harness_compiler.grounding import extract_grounding

            if self.settings.analysis_mode != "grounded":
                raise ValueError("Repair is only supported for grounded analysis")
            extraction = extract_grounding(self.request.original_input)
            if extraction.request != self.request:
                raise ValueError("Repair requires canonical input reference inventory")
            GroundedRepairInput(extraction=extraction, feedback=self.repair_feedback)
        return self


class WorkerResult(Contract):
    status: Literal["completed", "error"]
    identity: ModelIdentity | None = None
    settings: SessionSettings | None = None
    understanding: ProjectUnderstandingSpec | None = None
    grounded_analysis: GroundedAnalysisSpec | None = None
    observation: ProviderObservation | None = None
    error_code: Identifier | None = None
    failure_diagnostic: GroundingDiagnostic | None = None

    @model_validator(mode="after")
    def consistent_result(self) -> Self:
        if self.status == "completed":
            if self.failure_diagnostic is not None:
                raise ValueError("Completed generation cannot claim a failure diagnostic")
            if (
                not all((self.identity, self.settings, self.understanding, self.observation))
                or self.error_code
            ):
                raise ValueError("Completed generation requires identity, observation and proposal")
            assert self.identity and self.observation and self.understanding
            assert self.settings
            if self.identity.requested_model != self.settings.model:
                raise ValueError("Identity differs from requested settings")
            if self.observation.output_tokens is not None and (
                self.observation.output_tokens > self.settings.max_output_tokens
            ):
                raise ValueError("Provider exceeded requested output token budget")
            if self.observation.returned_model not in {
                self.identity.requested_model,
                self.identity.requested_model + ":latest",
            }:
                raise ValueError("Provider returned a different model name")
            if self.understanding.review is not None:
                raise ValueError("Generation cannot supply a human review")
            if self.settings.analysis_mode == "grounded":
                if (
                    not self.grounded_analysis
                    or self.grounded_analysis.understanding != self.understanding
                ):
                    raise ValueError("Grounded generation requires matching verified analysis")
            elif self.grounded_analysis is not None:
                raise ValueError("Baseline generation cannot claim grounded analysis")
        elif not self.error_code or any(
            (
                self.identity,
                self.settings,
                self.understanding,
                self.observation,
                self.grounded_analysis,
            )
        ):
            raise ValueError("Error generation cannot claim completed execution evidence")
        if self.failure_diagnostic and self.error_code != self.failure_diagnostic.error_code:
            raise ValueError("Failure diagnostic contradicts worker error code")
        return self


class SessionJob(Contract):
    index: int = Field(ge=1)
    case_id: Identifier
    repetition: int = Field(ge=1, le=3)
    state: Literal["completed", "error", "not-run"]
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    effective_timeout_seconds: float = Field(default=0, ge=0, allow_inf_nan=False)
    generation: WorkerResult | None = None
    evaluation: UnderstandingEvalReport | None = None
    error_code: Identifier | None = None

    @model_validator(mode="after")
    def consistent_job(self) -> Self:
        if self.state == "completed":
            if (
                not self.generation
                or self.generation.status != "completed"
                or not self.evaluation
                or self.error_code
            ):
                raise ValueError("Completed job needs generation and artifact evaluation")
        elif any((self.generation, self.evaluation)) or not self.error_code:
            raise ValueError("Uncompleted job cannot carry completed proposal/evaluation")
        if self.state == "not-run" and self.elapsed_seconds != 0:
            raise ValueError("Unexecuted job cannot claim elapsed generation time")
        if (self.state == "not-run") != (self.effective_timeout_seconds == 0):
            raise ValueError("Attempted jobs need an effective supervisor timeout")
        return self


class ModelSessionReport(Contract):
    schema_version: Literal["UnderstandingModelSession/v1"] = "UnderstandingModelSession/v1"
    plan: SessionPlan
    jobs: list[SessionJob] = Field(min_length=1, max_length=192)
    attempts_used: int = Field(ge=0, le=30)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    stop_reason: (
        Literal["attempt-limit", "time-limit", "worker-timeout", "model-changed"] | None
    ) = None
    run_status: Literal["completed", "limited", "stopped"]
    evaluation_status: Literal["not-run", "fail", "error"]
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def consistent_session(self) -> Self:
        expected = [
            (case, repeat)
            for case in self.plan.cases
            for repeat in range(1, self.plan.settings.repeats + 1)
        ]
        if len(self.jobs) != len(expected):
            raise ValueError("Session must account for every planned case/repetition")
        count = 0
        digests: set[str] = set()
        for index, (job, (case, repeat)) in enumerate(zip(self.jobs, expected, strict=True), 1):
            if (job.index, job.case_id, job.repetition) != (index, case.id, repeat):
                raise ValueError("Session jobs differ from planned sequence")
            count += job.state != "not-run"
            if job.state == "completed":
                assert job.generation and job.evaluation and job.generation.identity
                identity = job.generation.identity
                evaluation = job.evaluation
                digests.add(canonical_project_digest(identity.model_dump(exclude={"observed_at"})))
                if (
                    identity.requested_model != self.plan.settings.model
                    or job.generation.settings != self.plan.settings
                    or identity.prompt_sha256 != self.plan.prompt_sha256
                    or evaluation.case != case
                    or evaluation.rubric != self.plan.rubric
                    or evaluation.corpus_sha256 != self.plan.corpus_sha256
                    or evaluation.split != self.plan.split
                    or evaluation.review is not None
                    or evaluation.understanding != job.generation.understanding
                    or evaluation.declared_candidate_sha256 != self.plan.declared_candidate_sha256
                ):
                    raise ValueError("Generation/evaluation differs from session plan")
                if job.effective_timeout_seconds > self.plan.settings.call_timeout_seconds:
                    raise ValueError("Job supervisor timeout exceeds call budget")
                if self.plan.settings.expected_model_sha256 and (
                    identity.model_sha256 != self.plan.settings.expected_model_sha256
                ):
                    raise ValueError("Generated model differs from expected digest")
        if len(digests) > 1:
            raise ValueError("Model changed between completed jobs")
        if count != self.attempts_used or count > self.plan.settings.max_attempts:
            raise ValueError("Session attempt count contradicts jobs or budget")
        if self.elapsed_seconds < sum(job.elapsed_seconds for job in self.jobs):
            raise ValueError("Session elapsed time is shorter than job execution time")
        if self.stop_reason == "attempt-limit" and count != self.plan.settings.max_attempts:
            raise ValueError("Attempt stopping reason does not match exhausted budget")
        if (
            self.stop_reason == "time-limit"
            and self.elapsed_seconds < self.plan.settings.session_seconds
        ):
            raise ValueError("Time stopping reason does not match exhausted budget")
        skipped = any(job.state == "not-run" for job in self.jobs)
        stopped = False
        for job in self.jobs:
            if stopped and job.state != "not-run":
                raise ValueError("Session cannot attempt jobs after stopping")
            stopped = (
                stopped
                or job.state == "not-run"
                or job.error_code
                in {
                    "worker-timeout",
                    "model-changed",
                }
            )
        for cause in ("worker-timeout", "model-changed"):
            if (self.stop_reason == cause) != any(job.error_code == cause for job in self.jobs):
                raise ValueError("Stopping reason differs from observed error")
        expected_run = (
            "stopped"
            if self.stop_reason in {"worker-timeout", "model-changed"}
            else "limited"
            if self.stop_reason
            else "completed"
        )
        if self.run_status != expected_run or (skipped and self.stop_reason is None):
            raise ValueError("Session completion contradicts skipped jobs or stopping reason")
        expected_eval = (
            "error"
            if any(job.state == "error" for job in self.jobs)
            else "fail"
            if any(job.evaluation and job.evaluation.status == "fail" for job in self.jobs)
            else "not-run"
        )
        if self.evaluation_status != expected_eval:
            raise ValueError("Session evaluation contradicts job findings")
        return self
