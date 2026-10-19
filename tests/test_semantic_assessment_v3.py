"""Synthetic human declarations test gates; no real model output is approved here."""

import copy
import json

import pytest
from pydantic import ValidationError
from test_semantic_analysis_v3 import fixture_analysis
from test_semantic_assessment import declaration, fixtures

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment_v3 import (
    SemanticAssessmentV3,
    SemanticHumanReviewV3,
    assess_v3,
)


def inputs(project):
    case, rubric, _ = fixtures(project)
    analysis = fixture_analysis(project)
    review = SemanticHumanReviewV3(
        **declaration().model_dump(),
        case_sha256=case.snapshot_sha256,
        rubric_sha256=canonical_project_digest(rubric.model_dump()),
        analysis_sha256=analysis.snapshot_sha256,
        checks=[
            {"criterion": c.id, "outcome": "pass", "note": "Synthetic judgment"}
            for c in rubric.criteria
        ],
        coverage=[
            {"obligation_id": o.id, "finding_id": analysis.findings[0].id} for o in case.obligations
        ],
        finding_support=[
            {
                "finding_id": f.id,
                "finding_sha256": f.sha256,
                "source_atom_ids": f.source_atom_ids,
                "outcome": "pass",
                "note": "Synthetic finding judgment",
            }
            for f in analysis.findings
        ],
        component_support=[
            {
                "finding_id": f.id,
                "component_name": b.name,
                "component_index": b.index,
                "source_atom_ids": b.source_atom_ids,
                "outcome": "pass",
                "note": "Synthetic component judgment",
            }
            for f in analysis.findings
            for b in f.component_bindings
        ],
    )
    return case, rubric, analysis, review


def test_component_human_review_roundtrip_and_authority(project):
    case, rubric, analysis, review = inputs(project)
    report = assess_v3(case, rubric, analysis, review)
    assert report.status == "pass"
    assert report.compilation_eligibility == "not-authorized"
    assert report.model_qualification == "not-established"
    assert SemanticAssessmentV3.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize("missing", ["review", "case-approval", "rubric-approval"])
def test_no_implicit_approval(project, missing):
    case, rubric, analysis, review = inputs(project)
    if missing == "review":
        review = None
    elif missing == "case-approval":
        case.expectations_approval = None
        review.case_sha256 = case.snapshot_sha256
    else:
        rubric.approval = None
        review.rubric_sha256 = canonical_project_digest(rubric.model_dump())
    assert assess_v3(case, rubric, analysis, review).status == "not-run"


@pytest.mark.parametrize("field", ["finding_support", "component_support", "coverage"])
def test_incomplete_positive_review_rejected(project, field):
    case, rubric, analysis, review = inputs(project)
    setattr(review, field, [])
    with pytest.raises(ValueError):
        assess_v3(case, rubric, analysis, review)


@pytest.mark.parametrize("mutation", ["duplicate", "source", "finding", "name", "index"])
def test_component_identity_rejected(project, mutation):
    case, rubric, analysis, review = inputs(project)
    data = review.model_dump()
    component = data["component_support"][0]
    if mutation == "duplicate":
        data["component_support"].append(copy.deepcopy(component))
    elif mutation == "source":
        component["source_atom_ids"] = ["atom-unknown"]
    elif mutation == "finding":
        component["finding_id"] = "missing-finding"
    elif mutation == "name":
        component["component_name"] = "exception"
        component["component_index"] = 0
    else:
        component["component_index"] = 0
    with pytest.raises(ValueError):
        assess_v3(case, rubric, analysis, SemanticHumanReviewV3.model_validate(data))


def test_negative_component_cannot_be_hidden_in_positive_finding(project):
    case, rubric, analysis, review = inputs(project)
    review.component_support[0].outcome = "fail"
    with pytest.raises(ValueError, match="negative component"):
        assess_v3(case, rubric, analysis, review)
    review.finding_support[0].outcome = "fail"
    for check in review.checks:
        check.outcome = "not-run"
    assert assess_v3(case, rubric, analysis, review).status == "fail"


@pytest.mark.parametrize("mutation", ["analysis", "case", "rubric", "guard-target"])
def test_stale_review_and_tampered_assessment_rejected(project, mutation):
    case, rubric, analysis, review = inputs(project)
    if mutation == "analysis":
        review.analysis_sha256 = "0" * 64
    elif mutation == "case":
        review.case_sha256 = "0" * 64
    elif mutation == "rubric":
        review.rubric_sha256 = "0" * 64
    else:
        data = analysis.model_dump()
        data["proposal"]["guards"][0]["target_scope"] = "project"
        data["proposal"]["guards"][0]["target_criterion_atom_ids"] = []
        analysis = SemanticAnalysisV3.model_validate(data)
    with pytest.raises(ValueError):
        assess_v3(case, rubric, analysis, review)


def test_report_revalidates_derived_status(project):
    case, rubric, analysis, _ = inputs(project)
    data = assess_v3(case, rubric, analysis).model_dump()
    data["status"] = "pass"
    with pytest.raises(ValidationError):
        SemanticAssessmentV3.model_validate(data)


def test_cli_offline_pending_review_and_existing_output(project, tmp_path):
    case, rubric, analysis, _ = inputs(project)
    for name, value in [("case", case), ("rubric", rubric), ("analysis", analysis)]:
        (tmp_path / f"{name}.json").write_text(value.model_dump_json(), encoding="utf-8")
    output = tmp_path / "assessment.json"
    args = [
        "assess-analysis-v3",
        str(tmp_path / "analysis.json"),
        "--case",
        str(tmp_path / "case.json"),
        "--rubric",
        str(tmp_path / "rubric.json"),
        "--output",
        str(output),
    ]
    assert main(args) == 1
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "not-run"
    original = output.read_bytes()
    assert main(args) != 0
    assert output.read_bytes() == original
