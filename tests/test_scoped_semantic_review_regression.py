"""Replay scoped PO judgments without qualifying the model or changing history."""

import json
from pathlib import Path

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
