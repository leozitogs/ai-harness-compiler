"""Actual scoped PO review supplements immutable initial results and retains failures."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/evidence/sprint-2-6-v4-development-20261027"


def test_actual_decisions_bind_new_snapshots_without_replacing_initial_assessments():
    data = json.loads((BASE / "human-review.json").read_bytes())
    initial = json.loads((BASE / "execution.json").read_bytes())
    assert data["review_proposal_sha256"] == initial["review_proposal_sha256"]
    assert data["campaign_report_sha256"] == initial["report_sha256"]
    assert data["decisions"] == [
        dict(
            question_id="call_5288f072466c47ed9a77f17da97d6132",
            item=0,
            answer="Li e aprovo os seis casos e vínculos propostos",
        ),
        dict(
            question_id="call_5288f072466c47ed9a77f17da97d6132",
            item=1,
            answer="Confirmo a matriz e os vínculos propostos",
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
        assert old["human_output_review"] == "pending"
        assert new["finding_count"] == old["findings"]
        assert new["component_count"] == old["components"]
    assert data["original_artifacts_preserved"] is True
    assert data["authority"] == "human-declared-not-authenticated"


def test_confirmed_failures_cannot_be_compensated_by_positive_support():
    data = json.loads((BASE / "human-review.json").read_bytes())
    cases = {c["case_id"]: c for c in data["cases"]}
    failures = {k: v for k, v in cases.items() if v["reviewed_assessment_status"] == "fail"}
    assert set(failures) == {"dev-ambiguous-v4", "dev-compatible-rules-v4"}
    ambiguous = failures["dev-ambiguous-v4"]
    compatible = failures["dev-compatible-rules-v4"]
    assert {(f["code"], f["reference"]) for f in ambiguous["failures"]} == {
        ("obligation-missing", "required-1"),
        ("inappropriate-question", "issue-2"),
    }
    assert {(f["code"], f["reference"]) for f in compatible["failures"]} == {
        ("obligation-missing", "required-2"),
        ("obligation-missing", "required-4"),
    }
    for case in cases.values():
        checks = {c["criterion"]: c["outcome"] for c in case["checks"]}
        assert checks["citation-support"] == "pass"
        assert len(checks) == 6 and "not-run" not in checks.values()
        assert case["question_item"] == (1 if case["case_id"] in failures else 0)
    assert data["case_passes"] == 6 and data["case_failures"] == 2
    assert (
        data["criteria_passed"]
        == sum(c["outcome"] == "pass" for x in cases.values() for c in x["checks"])
        == 45
    )
    assert (
        data["criteria_failed"]
        == sum(c["outcome"] == "fail" for x in cases.values() for c in x["checks"])
        == 3
    )
    assert data["criteria_pending"] == 0


def test_review_records_no_new_budget_qualification_or_compilation_authority():
    data = json.loads((BASE / "human-review.json").read_bytes())
    assert data["budget"] == "closed" and data["new_model_invocations"] == 0
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert sum(c["finding_count"] for c in data["cases"]) == 88
    assert sum(c["component_count"] for c in data["cases"]) == 128
    assert sum(c["coverage_count"] for c in data["cases"]) == 21
