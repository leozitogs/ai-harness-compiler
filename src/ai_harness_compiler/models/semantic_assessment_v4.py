"""Independent snapshot-bound human review of v4; all concurrent failures are retained."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import BoundFindingV3
from ai_harness_compiler.models.semantic_analysis_v4 import (
    ContentRejectionV4,
    RequirementV4,
    SemanticAnalysisV4,
)
from ai_harness_compiler.models.semantic_assessment import ObligationCoverage
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_eval import (
    CRITERIA,
    CriterionID,
    HumanDeclaration,
    SemanticCheck,
    UnderstandingRubric,
)
from ai_harness_compiler.models.semantic_inventory_v4 import (
    ComponentIdentityV4,
    FindingIdentityV4,
    component_inventory_v4,
    coverage_source_ids,
)


class FindingSupportV4(FindingIdentityV4):
    outcome: Literal["pass", "fail"]
    materiality: Literal["appropriate", "inappropriate", "not-applicable"]
    note: Text


class ComponentSupportV4(ComponentIdentityV4):
    outcome: Literal["pass", "fail"]
    note: Text


class SemanticHumanReviewV4(HumanDeclaration):
    schema_version: Literal["SemanticHumanReview/v4"] = "SemanticHumanReview/v4"
    case_sha256: Digest
    rubric_sha256: Digest
    analysis_sha256: Digest
    checks: list[SemanticCheck] = Field(min_length=6, max_length=6)
    coverage: list[ObligationCoverage] = Field(default_factory=list, max_length=64)
    finding_support: list[FindingSupportV4] = Field(default_factory=list, max_length=1024)
    component_support: list[ComponentSupportV4] = Field(default_factory=list, max_length=8192)

    @model_validator(mode="after")
    def unique_review_inventory(self) -> Self:
        if {c.criterion for c in self.checks} != set(CRITERIA):
            raise ValueError("Human review must judge all six criteria exactly once")
        for keys in (
            [o.obligation_id for o in self.coverage],
            [f.finding_id for f in self.finding_support],
            [c.key for c in self.component_support],
        ):
            if len(set(keys)) != len(keys):
                raise ValueError("Human review identities must be unique")
        return self


class AssessmentFailureV4(Contract):
    criterion: CriterionID
    code: Literal[
        "disposition-mismatch",
        "obligation-missing",
        "conflict-missing",
        "content-rejection-missing",
        "project-rejection-missing",
        "finding-support-fail",
        "component-support-fail",
        "inappropriate-question",
    ]
    reference: Text | None = None


def _matching(case: AssessmentCaseV3, analysis: SemanticAnalysisV4) -> dict[str, list[str]]:
    atoms = {a.id: a.pointer for a in analysis.extraction.atoms}
    return {
        o.id: [
            f.id
            for f in analysis.findings
            if f.kind == ("question" if o.disposition == "required-question" else o.disposition)
            and o.source_pointer in {atoms[id_] for id_ in coverage_source_ids(f)}
            and (
                not isinstance(f, BoundFindingV3)
                or f.kind != "question"
                or f.impact != "implementation-detail"
            )
        ]
        for o in case.obligations
    }


def _validate_review(
    case: AssessmentCaseV3,
    rubric: UnderstandingRubric,
    analysis: SemanticAnalysisV4,
    review: SemanticHumanReviewV4,
) -> None:
    if (review.case_sha256, review.rubric_sha256, review.analysis_sha256) != (
        case.snapshot_sha256,
        canonical_project_digest(rubric.model_dump()),
        analysis.snapshot_sha256,
    ):
        raise ValueError("Human review belongs to different snapshots")
    findings = {f.id: f for f in analysis.findings}
    components = {c.identity.key: c.identity for c in component_inventory_v4(analysis)}
    negative = set()
    for c in review.component_support:
        if (
            c.key not in components
            or ComponentIdentityV4.model_validate(
                c.model_dump(include=set(ComponentIdentityV4.model_fields))
            )
            != components[c.key]
        ):
            raise ValueError("Human component judgment must bind exact text digest and sources")
        if c.outcome == "fail":
            negative.add(c.finding_id)
    for item in review.finding_support:
        f = findings.get(item.finding_id)
        if (
            f is None
            or item.finding_sha256 != f.sha256
            or item.source_atom_ids != f.source_atom_ids
        ):
            raise ValueError("Human finding support must bind exact evidence")
        if (item.materiality == "not-applicable") == (
            isinstance(f, BoundFindingV3) and f.kind == "question"
        ):
            raise ValueError("Human materiality applies exactly to questions")
        if item.finding_id in negative and item.outcome == "pass":
            raise ValueError("Positive finding cannot override negative component")
    matches = _matching(case, analysis)
    for mapping in review.coverage:
        if mapping.finding_id not in matches.get(mapping.obligation_id, []):
            raise ValueError(
                "Coverage must bind required kind and content source, not applicability"
            )
    checks = {c.criterion: c.outcome for c in review.checks}
    if checks["rule-coverage"] == "pass" and {c.obligation_id for c in review.coverage} != set(
        matches
    ):
        raise ValueError("Passing coverage requires every obligation mapping")
    if checks["citation-support"] == "pass" and (
        {f.finding_id for f in review.finding_support} != set(findings)
        or any(f.outcome != "pass" for f in review.finding_support)
        or {c.key for c in review.component_support} != set(components)
        or any(c.outcome != "pass" for c in review.component_support)
    ):
        raise ValueError("Passing support requires every exact positive finding/component judgment")


def _failures(
    case: AssessmentCaseV3, analysis: SemanticAnalysisV4, review: SemanticHumanReviewV4 | None
) -> list[AssessmentFailureV4]:
    failures = []

    def add(criterion: CriterionID, code: str, reference: str | None = None) -> None:
        failures.append(
            AssessmentFailureV4.model_validate(
                dict(criterion=criterion, code=code, reference=reference)
            )
        )

    if case.expected_behavior != analysis.disposition:
        add("project-understanding", "disposition-mismatch")
    matches = _matching(case, analysis)
    for o in case.obligations:
        if not matches[o.id]:
            add(
                "uncertainty" if o.disposition == "required-question" else "rule-coverage",
                "obligation-missing",
                o.id,
            )
    atoms = {a.id: a.pointer for a in analysis.extraction.atoms}

    def pointers(f: BoundFindingV3 | RequirementV4 | ContentRejectionV4) -> set[str]:
        return {atoms[id_] for id_ in f.source_atom_ids}

    if case.requires_conflict and not any(
        f.kind == "conflict" and set(case.conflict_source_pointers).issubset(pointers(f))
        for f in analysis.findings
    ):
        add("conflict-validity", "conflict-missing")
    for field, kind, code in [
        (
            case.required_content_rejection_pointers,
            "content-rejection",
            "content-rejection-missing",
        ),
        (case.required_project_rejection_pointers, "rejection", "project-rejection-missing"),
    ]:
        for pointer in field:
            if not any(f.kind == kind and pointer in pointers(f) for f in analysis.findings):
                add("project-understanding", code, pointer)
    if review:
        for f in review.finding_support:
            if f.outcome == "fail":
                add("citation-support", "finding-support-fail", f.finding_id)
            if f.materiality == "inappropriate":
                add("uncertainty", "inappropriate-question", f.finding_id)
        for c in review.component_support:
            if c.outcome == "fail":
                add(
                    "citation-support",
                    "component-support-fail",
                    f"{c.finding_id}.{c.component_name}.{c.component_index}",
                )
    return failures


def _checks(
    failures: list[AssessmentFailureV4], review: SemanticHumanReviewV4 | None
) -> list[SemanticCheck]:
    human = {c.criterion: c for c in review.checks} if review else {}
    return [
        SemanticCheck(
            criterion=id_,
            outcome="fail",
            note="; ".join(
                f"{f.code}: {f.reference or 'project'}" for f in failures if f.criterion == id_
            ),
        )
        if any(f.criterion == id_ for f in failures)
        else human.get(
            id_,
            SemanticCheck(
                criterion=id_, outcome="not-run", note="Independent human judgment required"
            ),
        )
        for id_ in CRITERIA
    ]


def _status(
    case: AssessmentCaseV3,
    rubric: UnderstandingRubric,
    review: SemanticHumanReviewV4 | None,
    checks: list[SemanticCheck],
) -> Literal["pass", "fail", "not-run"]:
    if any(c.outcome == "fail" for c in checks):
        return "fail"
    return (
        "pass"
        if review
        and case.expectations_approval
        and rubric.approval
        and all(c.outcome == "pass" for c in checks)
        else "not-run"
    )


class SemanticAssessmentV4(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["SemanticAssessment/v4"] = "SemanticAssessment/v4"
    case: AssessmentCaseV3
    rubric: UnderstandingRubric
    analysis: SemanticAnalysisV4
    review: SemanticHumanReviewV4 | None = None
    failures: list[AssessmentFailureV4] = Field(max_length=10000)
    checks: list[SemanticCheck] = Field(min_length=6, max_length=6)
    status: Literal["pass", "fail", "not-run"]
    case_sha256: Digest
    rubric_sha256: Digest
    analysis_sha256: Digest
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def bound_assessment(self) -> Self:
        case = AssessmentCaseV3.model_validate(self.case.model_dump())
        rubric = UnderstandingRubric.model_validate(self.rubric.model_dump())
        analysis = SemanticAnalysisV4.model_validate(self.analysis.model_dump())
        review = (
            SemanticHumanReviewV4.model_validate(self.review.model_dump()) if self.review else None
        )
        if rubric.version != "v2" or case.project != analysis.extraction.request.original_input:
            raise ValueError("Assessment requires v2 rubric and exact original case project")
        if (self.case_sha256, self.rubric_sha256, self.analysis_sha256) != (
            case.snapshot_sha256,
            canonical_project_digest(rubric.model_dump()),
            analysis.snapshot_sha256,
        ):
            raise ValueError("Assessment snapshot identity differs")
        if review:
            _validate_review(case, rubric, analysis, review)
        failures = _failures(case, analysis, review)
        checks = _checks(failures, review)
        if (
            self.failures != failures
            or self.checks != checks
            or self.status != _status(case, rubric, review, checks)
        ):
            raise ValueError("Assessment observations/status must match every bound artifact")
        return self


def assess_v4(
    case: AssessmentCaseV3,
    rubric: UnderstandingRubric,
    analysis: SemanticAnalysisV4,
    review: SemanticHumanReviewV4 | None = None,
) -> SemanticAssessmentV4:
    case = AssessmentCaseV3.model_validate(case.model_dump())
    rubric = UnderstandingRubric.model_validate(rubric.model_dump())
    analysis = SemanticAnalysisV4.model_validate(analysis.model_dump())
    review = SemanticHumanReviewV4.model_validate(review.model_dump()) if review else None
    if review:
        _validate_review(case, rubric, analysis, review)
    failures = _failures(case, analysis, review)
    checks = _checks(failures, review)
    return SemanticAssessmentV4(
        case=case,
        rubric=rubric,
        analysis=analysis,
        review=review,
        failures=failures,
        checks=checks,
        status=_status(case, rubric, review, checks),
        case_sha256=case.snapshot_sha256,
        rubric_sha256=canonical_project_digest(rubric.model_dump()),
        analysis_sha256=analysis.snapshot_sha256,
    )
