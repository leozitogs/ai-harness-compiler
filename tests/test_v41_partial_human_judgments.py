"""A scoped human failure survives positive support and incomplete execution."""

import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1] / "docs/evidence/sprint-2-6-v41-development-20261028"


def test_human_judgments_bind_only_the_four_available_snapshots():
    data = json.loads((BASE / "human-review.json").read_bytes())
    initial = json.loads((BASE / "execution.json").read_bytes())
    assert data["review_proposal_sha256"] == initial["review_proposal_sha256"]
    assert data["campaign_report_sha256"] == initial["report_sha256"]
    assert len(data["cases"]) == 4
    for new, old in zip(data["cases"], initial["cases"][:4], strict=True):
        for key in (
            "case_id",
            "run_id",
            "case_sha256",
            "analysis_sha256",
            "initial_assessment_status",
            "initial_failures",
        ):
            assert new[key] == old[key]
        assert old["human_output_review"] == "pending"
        assert new["finding_count"] == old["findings"]
        assert new["component_count"] == old["components"]
    assert data["unavailable_cases"] == [c["case_id"] for c in initial["cases"][4:]]
    assert data["decisions"] == [
        dict(
            question_id="call_706debe7ce9148698302be78e0dd513c",
            item=0,
            answer="Li e aprovo os três casos e vínculos propostos",
        ),
        dict(
            question_id="call_706debe7ce9148698302be78e0dd513c",
            item=1,
            answer="Confirmo a matriz e os vínculos propostos",
        ),
    ]


def test_human_uncertainty_failure_needs_no_fabricated_deterministic_code():
    data = json.loads((BASE / "human-review.json").read_bytes())
    for case in data["cases"]:
        conflict = case["case_id"] == "dev-branding-conflict-v4"
        assert case["reviewed_assessment_status"] == ("fail" if conflict else "pass")
        assert case["question_item"] == int(conflict)
        assert case["failures"] == []
        assert len(case["checks"]) == 6
        for check in case["checks"]:
            assert check["outcome"] == (
                "fail" if conflict and check["criterion"] == "uncertainty" else "pass"
            )
    assert (data["case_passes"], data["case_failures"]) == (3, 1)
    assert (data["criteria_passed"], data["criteria_failed"], data["criteria_pending"]) == (
        23,
        1,
        0,
    )


def test_partial_review_does_not_reopen_budget_or_qualify_the_model():
    data = json.loads((BASE / "human-review.json").read_bytes())
    assert data["budget"] == "closed" and data["new_model_invocations"] == 0
    assert data["original_artifacts_preserved"] is True
    assert data["authority"] == "human-declared-not-authenticated"
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert sum(c["coverage_count"] for c in data["cases"]) == 15
    assert sum(c["finding_count"] for c in data["cases"]) == 49
    assert sum(c["component_count"] for c in data["cases"]) == 72
