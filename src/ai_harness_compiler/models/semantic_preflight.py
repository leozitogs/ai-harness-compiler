"""Provider-free structural representability before any model construction or budget use."""

from typing import Annotated, Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3

AnalysisVersion = Literal["SemanticAnalysis/v3", "SemanticAnalysis/v4"]
CaseVersion = Annotated[AssessmentCase | AssessmentCaseV3, Field(discriminator="schema_version")]


class RepresentabilityIssue(Contract):
    code: Literal[
        "requirement-source-unrepresentable",
        "content-rejection-channel-unavailable",
        "explicit-case-migration-required",
    ]
    obligation_id: Identifier | None = None
    source_pointer: Text | None = None


def representability_issues(
    case: AssessmentCase | AssessmentCaseV3, target: AnalysisVersion
) -> list[RepresentabilityIssue]:
    if target not in {"SemanticAnalysis/v3", "SemanticAnalysis/v4"}:
        raise ValueError("Unknown analysis version")
    issues = []
    if target == "SemanticAnalysis/v4" and isinstance(case, AssessmentCase):
        # Do not guess whether an old refusal meant a fragment or the project.
        issues.append(RepresentabilityIssue(code="explicit-case-migration-required"))
    if target == "SemanticAnalysis/v3":
        criteria = {
            a.pointer
            for a in extract_grounding(case.project).atoms
            if a.kind == "acceptance-criterion"
        }
        issues.extend(
            RepresentabilityIssue(
                code="requirement-source-unrepresentable",
                obligation_id=o.id,
                source_pointer=o.source_pointer,
            )
            for o in case.obligations
            if o.disposition == "requirement" and o.source_pointer not in criteria
        )
        if isinstance(case, AssessmentCaseV3):
            issues.extend(
                RepresentabilityIssue(
                    code="content-rejection-channel-unavailable", source_pointer=pointer
                )
                for pointer in case.required_content_rejection_pointers
            )
    return issues


class SemanticPreflightReport(Contract):
    schema_version: Literal["SemanticPreflightReport/v1"] = "SemanticPreflightReport/v1"
    case: CaseVersion
    target_analysis_version: AnalysisVersion
    case_sha256: Digest
    input_sha256: Digest
    issues: list[RepresentabilityIssue] = Field(max_length=128)
    status: Literal["compatible", "incompatible"]
    execution_authorized: Literal[False] = False
    semantic_status: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"

    @model_validator(mode="after")
    def exact_observations(self) -> Self:
        case = type(self.case).model_validate(self.case.model_dump())
        expected = representability_issues(case, self.target_analysis_version)
        if (
            self.case_sha256 != case.snapshot_sha256
            or self.input_sha256 != canonical_project_digest(case.project.model_dump())
            or self.issues != expected
            or self.status != ("incompatible" if expected else "compatible")
        ):
            raise ValueError("Preflight observations must match the exact case and target version")
        return self


def preflight_case(
    case: AssessmentCase | AssessmentCaseV3, target: AnalysisVersion
) -> SemanticPreflightReport:
    case = type(case).model_validate(case.model_dump())
    issues = representability_issues(case, target)
    return SemanticPreflightReport(
        case=case,
        target_analysis_version=target,
        case_sha256=case.snapshot_sha256,
        input_sha256=canonical_project_digest(case.project.model_dump()),
        issues=issues,
        status="incompatible" if issues else "compatible",
    )
