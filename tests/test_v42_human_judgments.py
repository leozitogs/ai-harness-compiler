"""Actual scoped PO acceptance never overwrites initial results or grants new authority."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/evidence/sprint-2-6-v42-development-20261028"


def test_actual_decisions_bind_eight_new_snapshots_and_preserve_initial_statuses():
    data = json.loads((BASE / "human-review.json").read_bytes())
    initial = json.loads((BASE / "execution.json").read_bytes())
    assert data["review_proposal_sha256"] == initial["review_proposal_sha256"]
    assert data["campaign_report_sha256"] == initial["report_sha256"]
    assert data["decisions"] == [
        dict(
            question_id="call_dbd920ce0de347a6a3d2bd9eaac05981",
            item=0,
            answer="Li e aprovo os seis casos ready e vínculos propostos",
        ),
        dict(
            question_id="call_dbd920ce0de347a6a3d2bd9eaac05981",
            item=1,
            answer="Li e aprovo os dois casos blocked e vínculos propostos",
        ),
    ]
    assert len(data["cases"]) == len(initial["cases"]) == 8
    for new, old in zip(data["cases"], initial["cases"], strict=True):
        for key in (
            "case_id",
            "run_id",
            "case_sha256",
            "analysis_sha256",
            "initial_assessment_status",
            "initial_failures",
        ):
            assert new[key] == old[key]
        assert new["assessment_sha256"] != old["initial_assessment_sha256"]
        assert (
            old["human_output_review"] == "pending"
            and old["initial_assessment_status"] == "not-run"
        )
        assert new["question_item"] == int(old["disposition"] == "blocked")
        assert new["finding_count"] == old["findings"]
        assert new["component_count"] == old["components"]
    assert data["original_artifacts_preserved"] is True


def test_all_current_criteria_pass_without_erasing_historical_failures():
    data = json.loads((BASE / "human-review.json").read_bytes())
    assert (data["case_passes"], data["case_failures"]) == (8, 0)
    assert (data["criteria_passed"], data["criteria_failed"], data["criteria_pending"]) == (
        48,
        0,
        0,
    )
    for case in data["cases"]:
        assert case["reviewed_assessment_status"] == "pass" and case["failures"] == []
        assert len(case["checks"]) == 6 and all(c["outcome"] == "pass" for c in case["checks"])
    old_full = json.loads(
        (BASE.parent / "sprint-2-6-v4-development-20261027/human-review.json").read_bytes()
    )
    old_partial = json.loads(
        (BASE.parent / "sprint-2-6-v41-development-20261028/human-review.json").read_bytes()
    )
    assert old_full["case_failures"] == 2 and old_full["criteria_failed"] == 3
    assert old_partial["case_failures"] == 1 and old_partial["criteria_failed"] == 1
    assert len(old_partial["cases"]) == 4


def test_output_acceptance_does_not_reopen_budget_qualify_or_authorize_compilation():
    data = json.loads((BASE / "human-review.json").read_bytes())
    assert data["budget"] == "closed" and data["new_model_invocations"] == 0
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert data["authority"] == "human-declared-not-authenticated"
    assert sum(c["coverage_count"] for c in data["cases"]) == 24
    assert sum(c["finding_count"] for c in data["cases"]) == 77
    assert sum(c["component_count"] for c in data["cases"]) == 110
