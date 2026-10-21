"""Explicit reserved execution contracts; no provider calls or filesystem access."""

import hashlib
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import AfterValidator, Field, FiniteFloat, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.reserved_evaluation import (
    ReservedEvaluationProtocol,
    reserved_preparation_gates,
)
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_assessment_v3 import (
    SemanticAssessmentV3,
    SemanticHumanReviewV3,
    assess_v3,
)
from ai_harness_compiler.models.semantic_eval import HumanDeclaration, UnderstandingRubric


def relative_file(value: str) -> str:
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or path.as_posix() != value
        or any(part in {"..", "."} for part in path.parts)
        or any(char in value for char in "\\:\x00")
        or value == "."
    ):
        raise ValueError("Reserved paths must be normalized repository-relative POSIX paths")
    return value


RelativeFile = Annotated[Text, AfterValidator(relative_file)]


class ReservedSource(Contract):
    path: RelativeFile
    sha256: Digest


class ReservedCodeFreeze(Contract):
    files: list[ReservedSource] = Field(min_length=1, max_length=64)
    scope: Text
    source_commit: Text

    @model_validator(mode="after")
    def unique_paths(self) -> Self:
        if len({s.path for s in self.files}) != len(self.files):
            raise ValueError("Frozen source paths must be unique")
        return self


class ReservedRequestedProfile(Contract):
    format: Literal["reserved-requested-profile-freeze/v1"]
    provider: Literal["codex-cli-chatgpt-subscription"]
    requested_model: Text = Field(pattern=r"^[A-Za-z0-9][\w.:-]{0,199}$")
    adapter_version: Text
    overrides: list[Text] = Field(min_length=1, max_length=32)
    timeout_seconds: int = Field(ge=1, le=300)
    observed_immutable_model: None
    observed_sampling_parameters: None
    scope: Text


class ReservedRunRequest(Contract):
    schema_version: Literal["ReservedRunRequest/v1"] = "ReservedRunRequest/v1"
    id: Identifier
    protocol: ReservedEvaluationProtocol
    profile: ReservedRequestedProfile
    candidate_code: ReservedCodeFreeze
    runner_sources: list[ReservedSource] = Field(min_length=1, max_length=64)
    rubric_path: RelativeFile
    output_path: RelativeFile
    error_policy: Literal["stop-on-first-error-no-resume"] = "stop-on-first-error-no-resume"
    model_payload: Literal["project-sources-only-never-expectations"] = (
        "project-sources-only-never-expectations"
    )
    cleanup_grace_seconds: Literal[20] = 20
    max_prompt_bytes: Literal[262144] = 262144
    max_response_bytes: Literal[2097152] = 2097152
    max_corpus_bytes: Literal[33554432] = 33554432
    semantic_status: Literal["not-established"] = "not-established"

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def exact_frozen_request(self) -> Self:
        protocol = ReservedEvaluationProtocol.model_validate(self.protocol.model_dump())
        if reserved_preparation_gates(protocol):
            raise ValueError("Reserved preparation gates must be satisfied before proposing a run")
        assert protocol.candidate and protocol.budget
        if protocol.budget.max_session_seconds < (
            protocol.budget.max_call_seconds + self.cleanup_grace_seconds
        ):
            raise ValueError("Session budget must allow at least one call and cleanup")
        if (
            canonical_project_digest(self.profile.model_dump()) != protocol.candidate.profile_sha256
            or canonical_project_digest(self.candidate_code.model_dump())
            != protocol.candidate.code_sha256
            or self.candidate_code.source_commit != protocol.candidate.source_commit
            or self.profile.timeout_seconds != protocol.budget.max_call_seconds
        ):
            raise ValueError(
                "Requested profile and selected sources must match the frozen candidate"
            )
        if not self.output_path.startswith(".factory/reserved-v2-executions/"):
            raise ValueError("Reserved run outputs must remain in the private execution directory")
        for case in protocol.reserved:
            relative_file(case.artifact_path)
            if not case.artifact_path.startswith(".factory/"):
                raise ValueError("Reserved raw cases must remain private")
        sources = self.candidate_code.files + self.runner_sources
        if any(not source.path.startswith("src/ai_harness_compiler/") for source in sources):
            raise ValueError("Only package sources can be frozen for execution")
        if len({s.path for s in self.runner_sources}) != len(self.runner_sources):
            raise ValueError("Runner source paths must be unique")
        if len({s.path for s in sources}) != len(sources):
            raise ValueError("Candidate and runner source inventories must be disjoint")
        if len(self.model_dump_json().encode()) > 256 * 1024:
            raise ValueError("Reserved execution request exceeds 256 KiB metadata budget")
        return self


class ReservedRunAuthorization(HumanDeclaration):
    schema_version: Literal["ReservedRunAuthorization/v1"] = "ReservedRunAuthorization/v1"
    request_sha256: Digest
    authorized: Literal[True]
    scope: Literal["read-listed-cases-run-budget-store-private-results"] = (
        "read-listed-cases-run-budget-store-private-results"
    )


def validate_run_authorization(
    request: ReservedRunRequest, authorization: ReservedRunAuthorization
) -> None:
    if authorization.request_sha256 != request.sha256:
        raise ValueError("RESERVED_AUTHORIZATION_STALE")
    if authorization.reviewer in {
        request.protocol.candidate_designer,
        request.protocol.curator,
        request.profile.requested_model,
    }:
        raise ValueError("RESERVED_AUTHORIZATION_REQUIRES_HUMAN_DECLARATION")


class ReservedRunJob(Contract):
    case_id: Identifier
    repetition: int = Field(ge=1, le=10)
    stage: Literal["analysis", "audit"]
    state: Literal["completed", "error", "not-run"]
    invocation_charged: bool
    elapsed_seconds: FiniteFloat = Field(ge=0)
    response_sha256: Digest | None = None
    artifact_sha256: Digest | None = None
    analysis_sha256: Digest | None = None
    error_code: Text | None = None

    @model_validator(mode="after")
    def consistent_state(self) -> Self:
        if self.invocation_charged != (self.state != "not-run"):
            raise ValueError("Every attempted stage must be charged, including failures")
        if self.state == "completed":
            if not all((self.response_sha256, self.artifact_sha256, self.analysis_sha256)) or (
                self.error_code is not None
            ):
                raise ValueError(
                    "Completed stage requires exact response, artifact and analysis hashes"
                )
        elif not self.error_code or self.artifact_sha256 is not None:
            raise ValueError("Incomplete stages require a reason and cannot claim a valid artifact")
        if self.state == "not-run" and (
            self.elapsed_seconds != 0 or self.response_sha256 or self.analysis_sha256
        ):
            raise ValueError("Unexecuted stages cannot claim observations")
        return self


Stage = Literal["analysis", "audit"]


def reserved_job_keys(request: ReservedRunRequest) -> list[tuple[str, int, Stage]]:
    assert request.protocol.budget
    stages: tuple[Stage, ...] = ("analysis", "audit")
    return [
        (case.case_id, repetition, stage)
        for case in request.protocol.reserved
        for repetition in range(1, request.protocol.budget.repetitions + 1)
        for stage in stages
    ]


class ReservedRunReport(Contract):
    schema_version: Literal["ReservedRunReport/v1"] = "ReservedRunReport/v1"
    request: ReservedRunRequest
    authorization: ReservedRunAuthorization
    request_sha256: Digest
    started_at: Text
    finished_at: Text
    jobs: list[ReservedRunJob] = Field(min_length=1, max_length=1280)
    model_invocations_charged: int = Field(ge=0, le=1280)
    provider_calls_observed: None = None
    elapsed_seconds: FiniteFloat = Field(ge=0)
    state: Literal["completed", "stopped"]
    stop_reason: Text | None = None
    payload_validation: Literal["exact-bytes-and-contracts"] = "exact-bytes-and-contracts"
    identity_authentication: Literal["not-established"] = "not-established"
    semantic_status: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"

    @model_validator(mode="after")
    def bound_terminal_state(self) -> Self:
        request = ReservedRunRequest.model_validate(self.request.model_dump())
        authorization = ReservedRunAuthorization.model_validate(self.authorization.model_dump())
        validate_run_authorization(request, authorization)
        if self.request_sha256 != request.sha256:
            raise ValueError("Reserved run report belongs to another request")
        keys = [(j.case_id, j.repetition, j.stage) for j in self.jobs]
        if keys != reserved_job_keys(request):
            raise ValueError("Reserved run must preserve every planned stage exactly once in order")
        charged = sum(j.invocation_charged for j in self.jobs)
        assert request.protocol.budget
        if charged != self.model_invocations_charged or charged > request.protocol.budget.max_calls:
            raise ValueError("Reserved run accounting contradicts charged invocations")
        stopped = False
        for i, job in enumerate(self.jobs):
            if stopped and job.state != "not-run":
                raise ValueError("Execution cannot continue or resume after a stopped stage")
            if job.stage == "audit" and job.state != "not-run":
                analysis = self.jobs[i - 1]
                if analysis.state != "completed" or analysis.analysis_sha256 != job.analysis_sha256:
                    raise ValueError("Audit must bind the exact completed analysis")
            stopped |= job.state != "completed"
        if self.state != ("stopped" if stopped else "completed") or (
            bool(self.stop_reason) != stopped
        ):
            raise ValueError("Terminal state must match all job observations")
        if stopped:
            first = next(job for job in self.jobs if job.state != "completed")
            if self.stop_reason != first.error_code or any(
                job.state == "not-run" and job.error_code != self.stop_reason for job in self.jobs
            ):
                raise ValueError("Stop reason must match the first failure and remaining stages")
        if self.elapsed_seconds < sum(job.elapsed_seconds for job in self.jobs):
            raise ValueError("Session duration cannot be shorter than sequential calls")
        if not stopped and any(
            job.elapsed_seconds > request.protocol.budget.max_call_seconds for job in self.jobs
        ):
            raise ValueError("Over-budget calls cannot claim successful completion")
        if not stopped and self.elapsed_seconds > request.protocol.budget.max_session_seconds:
            raise ValueError("Over-budget session cannot claim successful completion")
        return self


class ReservedSemanticAssessment(Contract):
    """Resolve external expectation approval without mutating the original case or v3 report."""

    schema_version: Literal["ReservedSemanticAssessment/v1"] = "ReservedSemanticAssessment/v1"
    protocol: ReservedEvaluationProtocol
    original_assessment: SemanticAssessmentV3
    rubric_json: str = Field(min_length=1, max_length=2097152)
    rubric_artifact_sha256: Digest
    status: Literal["pass", "fail", "not-run"]
    expectation_authority: Literal["external-human-review-bound-to-original-corpus"] = (
        "external-human-review-bound-to-original-corpus"
    )
    identity_authentication: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"

    @model_validator(mode="after")
    def original_case_and_explicit_review(self) -> Self:
        protocol = ReservedEvaluationProtocol.model_validate(self.protocol.model_dump())
        base = SemanticAssessmentV3.model_validate(self.original_assessment.model_dump())
        if (
            hashlib.sha256(self.rubric_json.encode("utf-8")).hexdigest()
            != self.rubric_artifact_sha256
            or UnderstandingRubric.model_validate_json(self.rubric_json) != base.rubric
        ):
            raise ValueError(
                "Reserved assessment rubric bytes contradict its parsed content or digest"
            )
        if set(reserved_preparation_gates(protocol)) - {
            "execution-budget-not-proposed",
            "execution-budget-does-not-match-generation-and-audit",
        }:
            raise ValueError("Reserved assessment requires reviewed original corpus metadata")
        binding = next((c for c in protocol.reserved if c.case_id == base.case.id), None)
        if (
            not binding
            or binding.case_sha256 != base.case_sha256
            or binding.input_sha256 != base.input_sha256
            or binding.project_id != base.case.project.id
            or self.rubric_artifact_sha256 != protocol.rubric_sha256
        ):
            raise ValueError("Reserved assessment must bind the original case and rubric metadata")
        valid_approval = bool(
            protocol.review
            and protocol.review.corpus_sha256 == protocol.corpus_sha256
            and protocol.review.reviewer not in {protocol.candidate_designer, protocol.curator}
        )
        if base.review and base.review.reviewer in {protocol.candidate_designer, protocol.curator}:
            raise ValueError("Candidate designer or curator cannot approve model output")
        expected = (
            "fail"
            if any(c.outcome == "fail" for c in base.checks)
            else "pass"
            if valid_approval
            and base.review
            and base.rubric.approval
            and all(c.outcome == "pass" for c in base.checks)
            else "not-run"
        )
        if self.status != expected:
            raise ValueError("Reserved assessment status must match explicit independent judgments")
        return self


def assess_reserved(
    protocol: ReservedEvaluationProtocol,
    case: AssessmentCase,
    rubric: UnderstandingRubric,
    analysis: SemanticAnalysisV3,
    rubric_raw: bytes,
    review: SemanticHumanReviewV3 | None = None,
) -> ReservedSemanticAssessment:
    base = assess_v3(case, rubric, analysis, review)
    status: Literal["pass", "fail", "not-run"] = (
        "fail"
        if any(c.outcome == "fail" for c in base.checks)
        else "pass"
        if base.review and base.rubric.approval and all(c.outcome == "pass" for c in base.checks)
        else "not-run"
    )
    return ReservedSemanticAssessment(
        protocol=protocol,
        original_assessment=base,
        rubric_json=rubric_raw.decode("utf-8"),
        rubric_artifact_sha256=hashlib.sha256(rubric_raw).hexdigest(),
        status=status,
    )
