"""Synthetic human fixtures exercise invariants; they are not project approvals."""

import copy

import pytest
from pydantic import ValidationError

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis import SemanticAnalysis
from ai_harness_compiler.models.semantic_assessment import (
    AssessmentCase,
    SemanticAssessment,
    SemanticHumanReview,
    assess,
)
from ai_harness_compiler.models.semantic_eval import CRITERIA, HumanDeclaration, UnderstandingRubric


def declaration():
    return HumanDeclaration(
        reviewer="synthetic-fixture-human", note="Contract fixture, no real PO approval"
    )


def rubric(approved=True):
    return UnderstandingRubric(
        id="semantic-v2",
        version="v2",
        criteria=[{"id": id_, "description": "Fixture semantic criterion"} for id_ in CRITERIA],
        approval=declaration() if approved else None,
    )


def fixtures(project, behavior="ready", approved=True, kind=None, impact=None):
    extraction = extract_grounding(project)
    atom = next(a for a in extraction.atoms if a.kind == "acceptance-criterion")
    kind = (
        kind or {"ready": "rule", "blocked": "question", "safely-rejected": "rejection"}[behavior]
    )
    criterion = {"kind": "requirement", "note": "Synthetic rationale, not semantic verification"}
    if kind == "rule":
        criterion.update(
            kind="business-rule", condition="Fixture condition", outcome="Fixture outcome"
        )
    if kind == "question":
        criterion.update(
            kind="needs-clarification",
            question={
                "text": "Synthetic material question",
                "impact": impact or "authorization",
                "rationale": "Synthetic material rationale",
            },
        )
    issues = []
    if kind == "rejection":
        index = next(i for i, a in enumerate(compact_context(extraction)) if a.id == atom.id)
        issues = [
            {
                "kind": "safe-rejection",
                "text": "Synthetic refusal",
                "rationale": "Fixture source refused",
                "context_indices": [index],
                "rejection_reason": "untrusted-instruction",
            }
        ]
    analysis = SemanticAnalysis.model_validate(
        {
            "extraction": extraction.model_dump(),
            "proposal": {
                "criteria": [
                    copy.deepcopy(criterion) | {"source_atom_id": a.id}
                    for a in extraction.atoms
                    if a.kind == "acceptance-criterion"
                ],
                "issues": issues,
            },
        }
    )
    case_data = {
        "id": "fixture-case",
        "project": project.model_dump(),
        "expected_behavior": behavior,
        "expectations_approval": declaration().model_dump() if approved else None,
    }
    if behavior == "safely-rejected":
        case_data["refusal_source_pointers"] = [atom.pointer]
    else:
        case_data["obligations"] = [
            {
                "id": "obligation-1",
                "source_pointer": atom.pointer,
                "quote": atom.quote,
                "disposition": "required-question" if behavior == "blocked" else "rule",
            }
        ]
    case = AssessmentCase.model_validate(case_data)
    return case, rubric(approved), analysis


def review(case, rubric, analysis):
    return SemanticHumanReview(
        **declaration().model_dump(),
        case_sha256=case.snapshot_sha256,
        rubric_sha256=canonical_project_digest(rubric.model_dump()),
        analysis_sha256=analysis.snapshot_sha256,
        checks=[
            {"criterion": id_, "outcome": "pass", "note": "Synthetic fixture judgment"}
            for id_ in CRITERIA
        ],
        coverage=[
            {"obligation_id": item.id, "finding_id": analysis.findings[0].id}
            for item in case.obligations
        ],
        finding_support=[
            {
                "finding_id": item.id,
                "finding_sha256": item.sha256,
                "source_atom_ids": item.source_atom_ids,
                "outcome": "pass",
                "note": "Synthetic support fixture",
            }
            for item in analysis.findings
        ],
    )


@pytest.mark.parametrize("behavior", ["ready", "blocked", "safely-rejected"])
def test_no_human_review_cannot_pass_even_when_disposition_matches(project, behavior):
    case, criteria, analysis = fixtures(project, behavior)
    report = assess(case, criteria, analysis)
    assert report.status == "not-run"
    assert report.compilation_eligibility == "not-authorized"
    assert report.model_qualification == "not-established"
    assert all(item.outcome == "not-run" for item in report.checks)


@pytest.mark.parametrize("behavior", ["ready", "blocked", "safely-rejected"])
def test_complete_bound_synthetic_review_can_pass_without_authorizing_compile(project, behavior):
    case, criteria, analysis = fixtures(project, behavior)
    report = assess(case, criteria, analysis, review(case, criteria, analysis))
    assert report.status == "pass"
    assert report.compilation_eligibility == "not-authorized"
    assert report.model_qualification == "not-established"
    assert SemanticAssessment.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("unapproved", ["case", "rubric"])
def test_review_is_pending_without_approved_expectations_and_rubric(project, unapproved):
    case, criteria, analysis = fixtures(project)
    if unapproved == "case":
        case.expectations_approval = None
    else:
        criteria.approval = None
    report = assess(case, criteria, analysis, review(case, criteria, analysis))
    assert report.status == "not-run"


@pytest.mark.parametrize("incomplete", ["coverage", "support"])
def test_passing_aggregate_requires_complete_finding_support_and_obligation_mapping(
    project, incomplete
):
    case, criteria, analysis = fixtures(project)
    data = review(case, criteria, analysis).model_dump()
    data["coverage" if incomplete == "coverage" else "finding_support"] = []
    with pytest.raises(ValueError):
        assess(case, criteria, analysis, SemanticHumanReview.model_validate(data))


def test_partial_review_never_passes(project):
    case, criteria, analysis = fixtures(project)
    data = review(case, criteria, analysis).model_dump()
    data["coverage"] = []
    data["finding_support"] = []
    for item in data["checks"]:
        item["outcome"] = "not-run"
    report = assess(case, criteria, analysis, SemanticHumanReview.model_validate(data))
    assert report.status == "not-run"


def test_negative_support_forces_failure_even_with_pending_aggregate(project):
    case, criteria, analysis = fixtures(project)
    data = review(case, criteria, analysis).model_dump()
    data["finding_support"][0]["outcome"] = "fail"
    next(item for item in data["checks"] if item["criterion"] == "citation-support")["outcome"] = (
        "not-run"
    )
    report = assess(case, criteria, analysis, SemanticHumanReview.model_validate(data))
    assert report.status == "fail"
    assert (
        next(item for item in report.checks if item.criterion == "citation-support").outcome
        == "fail"
    )


@pytest.mark.parametrize("tamper", ["case", "rubric", "analysis", "finding", "atoms", "mapping"])
def test_stale_or_incompatible_human_judgments_are_rejected(project, tamper):
    case, criteria, analysis = fixtures(project)
    data = review(case, criteria, analysis).model_dump()
    if tamper in {"case", "rubric", "analysis"}:
        data[tamper + "_sha256"] = "0" * 64
    elif tamper == "finding":
        data["finding_support"][0]["finding_sha256"] = "0" * 64
    elif tamper == "atoms":
        data["finding_support"][0]["source_atom_ids"] = ["unknown-atom"]
    else:
        data["coverage"][0]["obligation_id"] = "unknown-obligation"
    with pytest.raises(ValueError):
        assess(case, criteria, analysis, SemanticHumanReview.model_validate(data))


@pytest.mark.parametrize(
    "tamper",
    ["status", "input", "case", "rubric", "analysis", "checks", "compile", "qualification"],
)
def test_report_rejects_contradictory_metrics_and_promotion(project, tamper):
    case, criteria, analysis = fixtures(project)
    report = assess(case, criteria, analysis)
    data = report.model_dump()
    if tamper == "status":
        data["status"] = "pass"
    elif tamper in {"input", "case", "rubric", "analysis"}:
        data[tamper + "_sha256"] = "0" * 64
    elif tamper == "checks":
        data["checks"][0]["outcome"] = "pass"
    elif tamper == "compile":
        data["compilation_eligibility"] = "authorized"
    else:
        data["model_qualification"] = "qualified"
    with pytest.raises(ValidationError):
        SemanticAssessment.model_validate(data)


@pytest.mark.parametrize(
    "tamper",
    ["quote", "ready-empty", "blocked-empty", "reject-empty", "asset", "conflict-one-source"],
)
def test_cases_require_observable_grounded_expectations(project, tamper):
    case, _, _ = fixtures(project)
    data = copy.deepcopy(case.model_dump())
    if tamper == "quote":
        data["obligations"][0]["quote"] = "Invented quote"
    elif tamper == "asset":
        data["obligations"][0]["source_pointer"] = "/assets/0"
    elif tamper == "conflict-one-source":
        data["expected_behavior"] = "blocked"
        data["requires_conflict"] = True
        data["conflict_source_pointers"] = [data["obligations"][0]["source_pointer"]]
    else:
        data["obligations"] = []
        data["expected_behavior"] = {
            "ready-empty": "ready",
            "blocked-empty": "blocked",
            "reject-empty": "safely-rejected",
        }[tamper]
    with pytest.raises(ValidationError):
        AssessmentCase.model_validate(data)


def test_mutable_child_revalidation_prevents_silent_expectation_change(project):
    case, criteria, analysis = fixtures(project)
    case.obligations[0].__dict__["quote"] = "Invented after validation"
    with pytest.raises(ValidationError):
        assess(case, criteria, analysis)


def test_implementation_detail_question_does_not_satisfy_material_obligation(project):
    case, criteria, analysis = fixtures(project, "blocked")
    data = analysis.model_dump()
    for item in data["proposal"]["criteria"]:
        item["kind"] = "requirement"
        item["question"] = None
        item["uncertainties"] = [
            {
                "text": "Which internal variable name?",
                "impact": "implementation-detail",
                "rationale": "Fixture detail has no business consequence",
            }
        ]
    detail = SemanticAnalysis.model_validate(data)
    report = assess(case, criteria, detail)
    assert detail.disposition == "ready"
    assert report.status == "fail"
    assert next(item for item in report.checks if item.criterion == "uncertainty").outcome == "fail"


def test_coverage_cannot_map_rule_obligation_to_requirement_with_same_quote(project):
    case, criteria, analysis = fixtures(project, kind="requirement")
    with pytest.raises(ValueError, match="required finding kind"):
        assess(case, criteria, analysis, review(case, criteria, analysis))


def test_required_conflict_must_cover_both_expected_source_pointers(project):
    case, criteria, analysis = fixtures(project)
    context = compact_context(analysis.extraction)
    pointers = [context[0].pointer, context[1].pointer]
    data = case.model_dump()
    data.update(
        expected_behavior="blocked", requires_conflict=True, conflict_source_pointers=pointers
    )
    conflict_case = AssessmentCase.model_validate(data)
    proposal = analysis.model_dump()
    proposal["proposal"]["issues"] = [
        {
            "kind": "conflict",
            "text": "Synthetic conflict",
            "context_indices": [0, 1],
            "rationale": "Two fixture sources require reconciliation",
        }
    ]
    conflict_analysis = SemanticAnalysis.model_validate(proposal)
    judgment = review(conflict_case, criteria, conflict_analysis)
    assert assess(conflict_case, criteria, conflict_analysis, judgment).status == "pass"
    proposal["proposal"]["issues"][0]["context_indices"] = [0, 2]
    wrong = SemanticAnalysis.model_validate(proposal)
    report = assess(conflict_case, criteria, wrong)
    assert report.status == "fail"
    assert (
        next(item for item in report.checks if item.criterion == "conflict-validity").outcome
        == "fail"
    )


def test_rejected_case_cannot_pass_with_only_an_unrelated_refusal(project):
    case, criteria, analysis = fixtures(project, "safely-rejected")
    data = analysis.model_dump()
    data["proposal"]["issues"][0]["context_indices"] = [0]
    wrong = SemanticAnalysis.model_validate(data)
    report = assess(case, criteria, wrong)
    assert wrong.disposition == "safely-rejected"
    assert report.status == "fail"
