"""Evidence-bound QA contracts. Inspection, execution and acceptance stay distinct."""

import hashlib
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.scrum import SprintSnapshot, instant

Commit = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
CheckID = Literal["lint", "format", "typing", "tests", "schemas", "repo-policy", "sprint-plan"]
Facet = Literal[
    "code", "contracts", "provenance", "security", "regressions", "business", "artifacts"
]
FACETS: tuple[Facet, ...] = (
    "code",
    "contracts",
    "provenance",
    "security",
    "regressions",
    "business",
    "artifacts",
)


def default_checks() -> list[CheckID]:
    return ["lint", "format", "typing", "tests", "schemas"]


def safe_review_path(value: str) -> str:
    path = PurePosixPath(value)
    if (
        not path.parts
        or any(ord(c) < 32 for c in value)
        or "\\" in value
        or path.is_absolute()
        or str(path) != value
        or any(p in {".", ".."} for p in path.parts)
        or not (
            value in {"README.md", "AGENTS.md", "pyproject.toml"}
            or path.parts[0]
            in {"src", "tests", "docs", "planning", "schemas", "project-definition"}
        )
    ):
        raise ValueError("Review path is outside the source allowlist")
    if path.suffix not in {".py", ".json", ".yaml", ".yml", ".md", ".toml"}:
        raise ValueError("Review source is not an allowed text file")
    return value


class ReviewSource(Contract):
    path: Text = Field(max_length=512)
    content: str = Field(max_length=65536, repr=False)
    sha256: Digest

    @model_validator(mode="after")
    def valid_bytes(self) -> Self:
        safe_review_path(self.path)
        if (
            len(self.content.encode()) > 65536
            or hashlib.sha256(self.content.encode()).hexdigest() != self.sha256
        ):
            raise ValueError("Review source differs from bounded captured bytes")
        return self


class QAReviewRequest(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["QAReviewRequest/v1"] = "QAReviewRequest/v1"
    snapshot: SprintSnapshot
    base_commit: Commit
    head_commit: Commit
    author: Identifier
    reviewer: Literal["vera"] = "vera"
    captured_at: Text
    sources: list[ReviewSource] = Field(min_length=1, max_length=32)
    diff: str = Field(default="", max_length=65536, repr=False)
    diff_sha256: Digest = hashlib.sha256(b"").hexdigest()
    excluded_paths: list[Text] = Field(default_factory=list, max_length=256)
    max_age_seconds: int = Field(default=3600, ge=60, le=3600)
    check_ids: list[CheckID] = Field(default_factory=default_checks)
    check_timeout_seconds: int = Field(default=120, ge=1, le=300)
    total_check_seconds: int = Field(default=300, ge=1, le=600)

    @property
    def request_sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def bounded_request(self) -> Self:
        SprintSnapshot.model_validate(self.snapshot.model_dump())
        if not self.snapshot.stories:
            raise ValueError("QA requires an identified, nonempty sprint scope")
        if self.author == self.reviewer:
            raise ValueError("Review author and reviewer must be separate roles")
        if instant(self.captured_at) < instant(self.snapshot.observation.observed_at):
            raise ValueError("Review capture predates its sprint observation")
        if len({s.path for s in self.sources}) != len(self.sources) or len(
            set(self.check_ids)
        ) != len(self.check_ids):
            raise ValueError("Review sources and checks must be unique")
        sources = [ReviewSource.model_validate(s.model_dump()) for s in self.sources]
        if (
            len(self.diff.encode()) > 65536
            or hashlib.sha256(self.diff.encode()).hexdigest() != self.diff_sha256
        ):
            raise ValueError("Review diff differs from bounded captured bytes")
        if sum(len(s.content.encode()) for s in sources) + len(self.diff.encode()) > 256 * 1024:
            raise ValueError("Review source budget exceeds 256 KiB")
        return self


class QACitation(Contract):
    path: Text
    line: int = Field(ge=1)
    quote: Text = Field(max_length=1000)


class QAInspectionFinding(Contract):
    id: Identifier
    severity: Literal["P0", "P1", "P2", "P3"]
    facet: Facet
    story_id: Identifier
    criterion_index: int = Field(ge=0)
    title: Text = Field(max_length=200)
    impact: Text = Field(max_length=2000)
    recommendation: Text = Field(max_length=2000)
    citations: list[QACitation] = Field(min_length=1, max_length=8)
    reproduction: Text = Field(max_length=2000)
    verification: Literal["not-executed"] = "not-executed"


class QAInspection(Contract):
    """A model or analyst proposes findings, never check success or closure."""

    schema_version: Literal["QAInspection/v1"] = "QAInspection/v1"
    findings: list[QAInspectionFinding] = Field(default_factory=list, max_length=32)
    inspected_facets: list[Facet] = Field(default_factory=list, max_length=7)
    limitations: list[Text] = Field(min_length=1, max_length=32)


class QACheckResult(Contract):
    id: CheckID
    request_sha256: Digest
    head_commit: Commit
    status: Literal["passed", "failed", "timed-out", "not-run", "output-limit"]
    exit_code: int | None = None
    started_at: Text
    finished_at: Text
    output: str = Field(default="", max_length=32768, repr=False)
    output_sha256: Digest

    @model_validator(mode="after")
    def observed_execution(self) -> Self:
        if instant(self.finished_at) < instant(self.started_at):
            raise ValueError("Check finishes before starting")
        if (
            len(self.output.encode()) > 32768
            or hashlib.sha256(self.output.encode()).hexdigest() != self.output_sha256
        ):
            raise ValueError("Check output differs from captured bytes")
        if (
            (self.status == "passed" and self.exit_code != 0)
            or (self.status == "failed" and (self.exit_code is None or self.exit_code == 0))
            or (self.status == "not-run" and (self.exit_code is not None or self.output))
        ):
            raise ValueError("Check outcome contradicts exit code or execution evidence")
        return self


class QACriterionResult(Contract):
    story_id: Identifier
    criterion_index: int = Field(ge=0)
    criterion: Text
    finding_ids: list[Identifier] = Field(max_length=32)
    verification: Literal["not-established"] = "not-established"


class QAReviewReport(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["QAReviewReport/v1"] = "QAReviewReport/v1"
    request: QAReviewRequest
    request_sha256: Digest
    engine: Literal["local", "codex-cli", "ollama", "provided-inspection"]
    model: str | None = None
    inspection_status: Literal["completed", "not-requested", "rejected"] = "not-requested"
    model_attempts: int = Field(default=0, ge=0, le=1)
    model_calls: int | None = Field(default=0, ge=0, le=1)
    inspection: QAInspection
    checks: list[QACheckResult] = Field(max_length=7)
    recommendation: Literal["changes-required", "inconclusive", "ready-for-po"]
    missing_facets: list[Facet]
    criterion_count: int = Field(ge=0)
    criterion_matrix: list[QACriterionResult] = Field(max_length=4096)
    acceptance: Literal["not-established"] = "not-established"
    authority: Literal["advisory-only"] = "advisory-only"

    @property
    def report_sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def grounded_report(self) -> Self:
        from ai_harness_compiler.qa import report_facts, validate_inspection

        request = QAReviewRequest.model_validate(self.request.model_dump())
        if self.request_sha256 != request.request_sha256:
            raise ValueError("QA report belongs to another request")
        validate_inspection(request, self.inspection)
        if self.engine in {"codex-cli", "ollama"} and not self.model:
            raise ValueError("Model-assisted review requires an explicit model")
        remote = self.engine in {"codex-cli", "ollama"}
        if self.model_attempts != (1 if remote else 0):
            raise ValueError("QA model-call accounting differs from engine")
        expected_calls = (1 if self.inspection_status == "completed" else None) if remote else 0
        if self.model_calls != expected_calls or (
            remote and self.inspection_status == "not-requested"
        ):
            raise ValueError("QA call certainty differs from the observed inspection outcome")
        if self.inspection_status != "completed" and (
            self.inspection.findings or self.inspection.inspected_facets
        ):
            raise ValueError("Unavailable inspection cannot supply findings or coverage")
        checks = [QACheckResult.model_validate(c.model_dump()) for c in self.checks]
        if [c.id for c in checks] != request.check_ids:
            raise ValueError("QA checks must account for each requested check in order")
        for check in checks:
            if (
                check.request_sha256 != self.request_sha256
                or check.head_commit != request.head_commit
            ):
                raise ValueError("Check evidence belongs to another revision")
            if instant(check.started_at) < instant(request.captured_at):
                raise ValueError("Check predates its request")
        if (
            self.recommendation,
            self.missing_facets,
            self.criterion_count,
            self.criterion_matrix,
        ) != report_facts(request, self.inspection, checks):
            raise ValueError("QA report conclusions differ from captured evidence")
        return self


class SprintClosureAssessment(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["SprintClosureAssessment/v1"] = "SprintClosureAssessment/v1"
    qa: QAReviewReport
    qa_sha256: Digest
    sprint_goal: Text
    blocking_findings: list[Identifier]
    carryover: list[Identifier]
    check_failures: list[CheckID]
    conclusion: Literal["changes-required", "inconclusive", "ready-for-po"]
    full_delivery_established: Literal[False] = False
    human_decision_required: Literal[True] = True
    sprint_closed: Literal[False] = False
    completion_authority: Literal["none"] = "none"

    @model_validator(mode="after")
    def derived_closure(self) -> Self:
        from ai_harness_compiler.qa import closure_facts

        qa = QAReviewReport.model_validate(self.qa.model_dump())
        if self.qa_sha256 != qa.report_sha256:
            raise ValueError("Closure assessment refers to another QA report")
        if (
            self.sprint_goal,
            self.blocking_findings,
            self.carryover,
            self.check_failures,
            self.conclusion,
        ) != closure_facts(qa):
            raise ValueError("Closure assessment differs from QA evidence")
        return self


class QAReviewComparison(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["QAReviewComparison/v1"] = "QAReviewComparison/v1"
    previous: QAReviewReport
    current: QAReviewReport
    cleared_check_failures: list[CheckID]
    pending_previous_findings: list[Identifier]
    semantic_resolution: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def observed_changes_only(self) -> Self:
        from ai_harness_compiler.qa import comparison_facts

        previous = QAReviewReport.model_validate(self.previous.model_dump())
        current = QAReviewReport.model_validate(self.current.model_dump())
        if (self.cleared_check_failures, self.pending_previous_findings) != comparison_facts(
            previous, current
        ):
            raise ValueError("QA comparison differs from observed checks and open findings")
        return self


class QAIncidentCandidate(Contract):
    schema_version: Literal["QAIncidentCandidate/v1"] = "QAIncidentCandidate/v1"
    qa_sha256: Digest
    head_commit: Commit
    check_id: CheckID
    observed_status: Literal["failed", "timed-out", "output-limit"]
    output_sha256: Digest
    root_cause: Literal["not-established"] = "not-established"
    resolution: Literal["not-established"] = "not-established"
    memory_promotion: Literal["human-review-required"] = "human-review-required"
