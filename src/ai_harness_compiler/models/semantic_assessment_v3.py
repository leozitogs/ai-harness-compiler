"""Human assessment of component-bound analysis; no advisory-to-human conversion."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import BoundFindingV3, SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_eval import (
    CRITERIA,
    CriterionID,
    HumanDeclaration,
    SemanticCheck,
    UnderstandingRubric,
)


class FindingSupportV3(Contract):
    finding_id: Identifier
    finding_sha256: Digest
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=512)
    outcome: Literal["pass", "fail"]
    note: Text

    @model_validator(mode="after")
    def unique_atoms(self) -> Self:
        if len(set(self.source_atom_ids)) != len(self.source_atom_ids):
            raise ValueError("Support judgment cannot duplicate atom IDs")
        return self


class ObligationCoverage(Contract):
    obligation_id: Identifier
    finding_id: Identifier


class ComponentSupport(Contract):
    finding_id: Identifier
    component_name: Literal["condition", "outcome", "exception"]
    component_index: int | None = Field(default=None, ge=0)
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=32)
    outcome: Literal["pass", "fail"]
    note: Text

    @property
    def key(self) -> tuple[str, Literal["condition", "outcome", "exception"], int | None]:
        return self.finding_id, self.component_name, self.component_index

    @model_validator(mode="after")
    def exact_component_identity(self) -> Self:
        if (self.component_name == "exception") != (self.component_index is not None):
            raise ValueError("Only exception support has a component index")
        if len(set(self.source_atom_ids)) != len(self.source_atom_ids):
            raise ValueError("Component support cannot duplicate source atoms")
        return self


class SemanticHumanReviewV3(HumanDeclaration):
    schema_version: Literal["SemanticHumanReview/v3"] = "SemanticHumanReview/v3"
    case_sha256: Digest
    rubric_sha256: Digest
    analysis_sha256: Digest
    checks: list[SemanticCheck] = Field(min_length=6, max_length=6)
    coverage: list[ObligationCoverage] = Field(default_factory=list, max_length=64)
    finding_support: list[FindingSupportV3] = Field(default_factory=list, max_length=512)
    component_support: list[ComponentSupport] = Field(default_factory=list, max_length=5120)

    @model_validator(mode="after")
    def unique_complete_checks(self) -> Self:
        if {item.criterion for item in self.checks} != set(CRITERIA):
            raise ValueError("Human review must address all six criteria exactly once")
        if len({item.obligation_id for item in self.coverage}) != len(self.coverage):
            raise ValueError("Each obligation has at most one coverage mapping")
        if len({item.finding_id for item in self.finding_support}) != len(self.finding_support):
            raise ValueError("Each finding has at most one support judgment")
        if len({item.key for item in self.component_support}) != len(self.component_support):
            raise ValueError("Each component has at most one human support judgment")
        return self


MATERIAL_IMPACTS = {"rule", "authorization", "outcome", "precedence"}


def _derived_checks(
    case: AssessmentCase, analysis: SemanticAnalysisV3, review: SemanticHumanReviewV3 | None
) -> list[SemanticCheck]:
    failures: dict[CriterionID, str] = {}
    atoms = {atom.id: atom for atom in analysis.extraction.atoms}

    def pointers(finding: BoundFindingV3) -> set[str]:
        return {atoms[id_].pointer for id_ in finding.source_atom_ids}

    if analysis.disposition != case.expected_behavior:
        failures["project-understanding"] = "Analysis disposition differs from expected behavior"
    for obligation in case.obligations:
        kind = (
            "question" if obligation.disposition == "required-question" else obligation.disposition
        )
        matches = [
            finding
            for finding in analysis.findings
            if finding.kind == kind
            and obligation.source_pointer in pointers(finding)
            and (kind != "question" or finding.impact in MATERIAL_IMPACTS)
        ]
        if not matches:
            criterion: CriterionID = "uncertainty" if kind == "question" else "rule-coverage"
            failures[criterion] = "Required sourced finding absent from analysis"
    if case.requires_conflict and not any(
        finding.kind == "conflict"
        and set(case.conflict_source_pointers).issubset(pointers(finding))
        for finding in analysis.findings
    ):
        failures["conflict-validity"] = "Required conflict lacks the expected original sources"
    if case.refusal_source_pointers and not all(
        any(
            finding.kind == "rejection" and pointer in pointers(finding)
            for finding in analysis.findings
        )
        for pointer in case.refusal_source_pointers
    ):
        failures["project-understanding"] = "Required sourced refusal absent from analysis"
    judgments = {item.criterion: item for item in review.checks} if review else {}
    if review and any(item.outcome == "fail" for item in review.finding_support):
        failures["citation-support"] = "A human support judgment rejected a finding"
    if review and any(item.outcome == "fail" for item in review.component_support):
        failures["citation-support"] = "A human support judgment rejected a component"
    return [
        SemanticCheck(criterion=id_, outcome="fail", note=failures[id_])
        if id_ in failures
        else judgments.get(
            id_,
            SemanticCheck(
                criterion=id_, outcome="not-run", note="Independent human judgment required"
            ),
        )
        for id_ in CRITERIA
    ]


def _validate_review(
    case: AssessmentCase,
    rubric: UnderstandingRubric,
    analysis: SemanticAnalysisV3,
    review: SemanticHumanReviewV3,
) -> None:
    if (
        review.case_sha256 != case.snapshot_sha256
        or review.rubric_sha256 != canonical_project_digest(rubric.model_dump())
        or review.analysis_sha256 != analysis.snapshot_sha256
    ):
        raise ValueError("Human review belongs to another case, rubric or analysis snapshot")
    findings = {finding.id: finding for finding in analysis.findings}
    components = {
        (finding.id, component.name, component.index): component.source_atom_ids
        for finding in analysis.findings
        for component in finding.component_bindings
    }
    for component_support in review.component_support:
        if components.get(component_support.key) != component_support.source_atom_ids:
            raise ValueError("Human component support must bind exact component sources")
    rejected_findings = {
        item.finding_id for item in review.component_support if item.outcome == "fail"
    }
    if any(
        item.finding_id in rejected_findings and item.outcome == "pass"
        for item in review.finding_support
    ):
        raise ValueError("Positive finding support cannot override a negative component")
    atoms = {atom.id: atom for atom in analysis.extraction.atoms}
    obligations = {item.id: item for item in case.obligations}
    for support in review.finding_support:
        finding = findings.get(support.finding_id)
        if (
            finding is None
            or support.finding_sha256 != finding.sha256
            or support.source_atom_ids != finding.source_atom_ids
        ):
            raise ValueError("Support judgment must bind the exact finding and source inventory")
    for mapping in review.coverage:
        obligation = obligations.get(mapping.obligation_id)
        finding = findings.get(mapping.finding_id)
        if obligation is None or finding is None:
            raise ValueError("Coverage references an unknown obligation or finding")
        kind = (
            "question" if obligation.disposition == "required-question" else obligation.disposition
        )
        if (
            finding.kind != kind
            or obligation.source_pointer
            not in {atoms[id_].pointer for id_ in finding.source_atom_ids}
            or (kind == "question" and finding.impact not in MATERIAL_IMPACTS)
        ):
            raise ValueError("Coverage must bind the required finding kind and literal source")
    checks = {item.criterion: item.outcome for item in review.checks}
    if checks["rule-coverage"] == "pass" and {
        item.obligation_id for item in review.coverage
    } != set(obligations):
        raise ValueError("Passing coverage requires a mapping for every obligation")
    if checks["citation-support"] == "pass" and (
        {item.finding_id for item in review.finding_support} != set(findings)
        or any(item.outcome != "pass" for item in review.finding_support)
        or {item.key for item in review.component_support} != set(components)
        or any(item.outcome != "pass" for item in review.component_support)
    ):
        raise ValueError("Passing support requires exact positive judgments for every finding")


def _status(
    case: AssessmentCase,
    rubric: UnderstandingRubric,
    review: SemanticHumanReviewV3 | None,
    checks: list[SemanticCheck],
) -> Literal["pass", "fail", "not-run"]:
    if any(item.outcome == "fail" for item in checks):
        return "fail"
    if (
        review
        and case.expectations_approval
        and rubric.approval
        and all(item.outcome == "pass" for item in checks)
    ):
        return "pass"
    return "not-run"


class SemanticAssessmentV3(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["SemanticAssessment/v3"] = "SemanticAssessment/v3"
    case: AssessmentCase
    rubric: UnderstandingRubric
    analysis: SemanticAnalysisV3
    review: SemanticHumanReviewV3 | None = None
    checks: list[SemanticCheck] = Field(min_length=6, max_length=6)
    status: Literal["pass", "fail", "not-run"]
    input_sha256: Digest
    case_sha256: Digest
    rubric_sha256: Digest
    analysis_sha256: Digest
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def exhaustive_bindings(self) -> Self:
        case = AssessmentCase.model_validate(self.case.model_dump())
        rubric = UnderstandingRubric.model_validate(self.rubric.model_dump())
        analysis = SemanticAnalysisV3.model_validate(self.analysis.model_dump())
        review = (
            SemanticHumanReviewV3.model_validate(self.review.model_dump()) if self.review else None
        )
        if rubric.version != "v2":
            raise ValueError("Semantic v3 assessment requires the v2 rubric")
        if analysis.extraction.request.original_input != case.project:
            raise ValueError("Assessment analysis must belong to the exact case project")
        expected_hashes = (
            analysis.extraction.request.original_sha256,
            case.snapshot_sha256,
            canonical_project_digest(rubric.model_dump()),
            analysis.snapshot_sha256,
        )
        if (
            self.input_sha256,
            self.case_sha256,
            self.rubric_sha256,
            self.analysis_sha256,
        ) != expected_hashes:
            raise ValueError("Assessment snapshot hashes must match their complete artifacts")
        if review:
            _validate_review(case, rubric, analysis, review)
        checks = _derived_checks(case, analysis, review)
        if self.checks != checks or self.status != _status(case, rubric, review, checks):
            raise ValueError("Assessment checks and status must match their bound evidence")
        return self


def assess_v3(
    case: AssessmentCase,
    rubric: UnderstandingRubric,
    analysis: SemanticAnalysisV3,
    review: SemanticHumanReviewV3 | None = None,
) -> SemanticAssessmentV3:
    case = AssessmentCase.model_validate(case.model_dump())
    rubric = UnderstandingRubric.model_validate(rubric.model_dump())
    analysis = SemanticAnalysisV3.model_validate(analysis.model_dump())
    review = SemanticHumanReviewV3.model_validate(review.model_dump()) if review else None
    if review:
        _validate_review(case, rubric, analysis, review)
    checks = _derived_checks(case, analysis, review)
    return SemanticAssessmentV3(
        case=case,
        rubric=rubric,
        analysis=analysis,
        review=review,
        checks=checks,
        status=_status(case, rubric, review, checks),
        input_sha256=analysis.extraction.request.original_sha256,
        case_sha256=case.snapshot_sha256,
        rubric_sha256=canonical_project_digest(rubric.model_dump()),
        analysis_sha256=analysis.snapshot_sha256,
    )
