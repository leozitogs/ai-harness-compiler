"""Replay scoped PO judgments without qualifying the model or changing history."""

import hashlib
import json
from pathlib import Path

import pytest

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.semantic_assessment_v3 import SemanticAssessmentV3, assess_v3


def test_scoped_development_rejection_replays_through_offline_cli(tmp_path):
    root = Path(__file__).resolve().parents[1]
    historical = root / "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-ambiguous"
    decisions = root / "docs/evidence/sprint-2-6-human-judgments-20261020"
    output = tmp_path / "assessment.json"
    assert (
        main(
            [
                "assess-analysis-v3",
                str(historical / "analysis.json"),
                "--case",
                str(root / "evals/understanding/v2/development-draft/dev-ambiguous.json"),
                "--rubric",
                str(root / "evals/understanding/v2/rubric.json"),
                "--review",
                str(decisions / "dev-ambiguous-review.json"),
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assessment = SemanticAssessmentV3.model_validate_json(output.read_bytes())
    saved = SemanticAssessmentV3.model_validate_json(
        (decisions / "dev-ambiguous-assessment.json").read_bytes()
    )
    assert assessment == saved
    assert assessment.status == "fail"
    assert {c.criterion: c.outcome for c in assessment.checks} == {
        "citation-support": "fail",
        "rule-coverage": "not-run",
        "conflict-validity": "not-run",
        "asset-bounds": "not-run",
        "uncertainty": "not-run",
        "project-understanding": "not-run",
    }
    assert assessment.compilation_eligibility == "not-authorized"
    assert assessment.model_qualification == "not-established"
    # A nonblocking diagnostic is not a complete human criterion judgment.
    diagnostic = json.loads((decisions / "decisions.json").read_text(encoding="utf-8"))
    assert diagnostic["decisions"][1]["review"] is None
    assert diagnostic["decisions"][1]["assessment_status"] == "not-run"


def test_recovered_response_acceptance_requires_its_complete_bound_review(tmp_path):
    root = Path(__file__).resolve().parents[1]
    folder = root / "docs/evidence/sprint-2-6-human-judgments-20261020"
    receipt = json.loads((folder / "compatible-acceptance.json").read_text(encoding="utf-8"))
    output = tmp_path / "accepted.json"
    assert (
        main(
            [
                "assess-analysis-v3",
                str(root / receipt["sources"][1]["path"]),
                "--case",
                str(root / receipt["sources"][0]["path"]),
                "--rubric",
                str(root / "evals/understanding/v2/rubric.json"),
                "--review",
                str(folder / receipt["review"]),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assessment = SemanticAssessmentV3.model_validate_json(output.read_bytes())
    assert assessment == SemanticAssessmentV3.model_validate_json(
        (folder / receipt["assessment"]).read_bytes()
    )
    assert assessment.status == "pass"
    assert receipt["original_generation"] == "error"
    assert receipt["selected_attempt"] == "schema-v31-recovery"
    assert assessment.compilation_eligibility == "not-authorized"
    assert assessment.model_qualification == "not-established"
    assert assess_v3(assessment.case, assessment.rubric, assessment.analysis).status == "not-run"


@pytest.mark.parametrize(
    ("case_id", "status"),
    [
        ("dev-adversarial", "pass"),
        ("dev-ambiguous", "fail"),
        ("dev-branding-conflict", "fail"),
        ("dev-compatible-rules", "pass"),
        ("dev-new-domain", "pass"),
        ("dev-rules-a", "pass"),
        ("dev-rules-b", "fail"),
        ("dev-unread-assets", "pass"),
    ],
)
def test_complete_development_judgments_bind_original_sources(case_id, status):
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads(
        (root / "docs/evidence/sprint-2-6-development-assessment-20261020/manifest.json").read_text(
            encoding="utf-8"
        )
    )
    row = next(r for r in manifest["cases"] if r["case"] == case_id)
    for source in [*row["sources"], row["review"], row["assessment"]]:
        assert hashlib.sha256((root / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    assessment = SemanticAssessmentV3.model_validate_json(
        (root / row["assessment"]["path"]).read_bytes()
    )
    assert assessment.status == row["status"] == status
    assert assessment == assess_v3(
        assessment.case, assessment.rubric, assessment.analysis, assessment.review
    )
    assert all(c.outcome != "not-run" for c in assessment.checks)
    assert assessment.analysis_sha256 == row["analysis_sha256"]
    assert assessment.compilation_eligibility == "not-authorized"
    assert assessment.model_qualification == "not-established"
    assert manifest["criteria_judged"] == 48
    assert manifest["criteria_pending"] == 0
    assert manifest["criteria_pass"] == 43
    assert manifest["criteria_fail"] == 5
    assert manifest["case_passes"] == 5
    assert manifest["case_failures"] == 3
