"""A complete transport campaign still has forty-eight pending human criteria."""

import json
from pathlib import Path

from ai_harness_compiler.models.semantic_campaign import (
    SemanticCampaignAuthorizationV1,
    SemanticCampaignCallV1,
    SemanticCampaignRequestV1,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/evidence/sprint-2-6-v42-development-20261028"


def test_exact_authorization_and_full_case_accounting_bind_the_new_request():
    data = json.loads((BASE / "execution.json").read_bytes())
    request = SemanticCampaignRequestV1.model_validate_json(
        (ROOT / "evals/understanding/v4/development-candidate-v42/request.json").read_bytes()
    )
    auth = SemanticCampaignAuthorizationV1.model_validate(data["authorization"])
    assert data["request_sha256"] == auth.request_sha256 == request.sha256
    assert data["authorization_question_id"] == "call_b23abc3ca2cd43e0ac4ff4f88e22b301"
    assert data["authorization_answer"] == "Autorizo esta única rodada nesses limites"
    assert data["technical_status"] == "completed" and data["failure_code"] is None
    assert data["attempted_cases"] == data["completed_cases"] == len(data["cases"]) == 8
    assert data["failed_cases"] == data["unstarted_cases"] == 0
    for case, flow in zip(data["cases"], request.flows, strict=True):
        assert case["case_id"] == flow.case.id and case["run_id"] == flow.run_id
        assert case["case_sha256"] == flow.case.snapshot_sha256
        assert case["disposition"] == flow.case.expected_behavior


def test_all_sixteen_calls_remain_serial_contained_and_within_the_closed_budget():
    data = json.loads((BASE / "execution.json").read_bytes())
    calls = [SemanticCampaignCallV1.model_validate(c) for c in data["calls"]]
    assert [c.index for c in calls] == list(range(1, 17))
    assert [c.flow_index for c in calls] == [i // 2 for i in range(16)]
    assert [c.stage for c in calls] == ["analysis", "audit"] * 8
    assert all(c.receipt.status == "succeeded" and c.interruption is None for c in calls)
    assert all(c.receipt.root_reaped and c.receipt.tree_termination_requested for c in calls)
    assert all(c.receipt.containment != "none" and c.receipt.exit_code == 0 for c in calls)
    assert all(c.receipt.granted_seconds <= 180 for c in calls)
    assert all(
        a.finished_offset_seconds <= b.started_offset_seconds
        for a, b in zip(calls[:-1], calls[1:], strict=True)
    )
    assert data["invocations"] == data["successful_invocations"] == 16
    assert data["failed_invocations"] == data["unused_invocation_ceiling"] == 0
    assert data["elapsed_seconds"] < 3600 and data["budget_closed"] is True
    assert data["unused_calls_authorized"] is False and data["offline_replay"] == "passed"


def test_complete_structure_and_proposed_passes_are_not_actual_human_acceptance():
    data = json.loads((BASE / "execution.json").read_bytes())
    assert (
        data["review_proposal_sha256"]
        == "1b816c0c34a382527f615e57483d0a74a849a1b1926e09c56ae6a1df46a64052"
    )
    for case in data["cases"]:
        assert case["initial_assessment_status"] == "not-run" and case["initial_failures"] == []
        assert case["human_output_review"] == "pending"
        assert case["conflict_diagnostic_status"] == (
            "questions-present" if case["case_id"] == "dev-branding-conflict-v4" else "no-conflicts"
        )
    assert sum(c["findings"] for c in data["cases"]) == 77
    assert sum(c["components"] for c in data["cases"]) == 110
    assert sum(c["coverage_count"] for c in data["cases"]) == 24
    assert data["proposed_case_passes"] == 8 and data["actual_human_case_passes"] == 0
    assert data["criteria_pending"] == 48
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert data["assets_read"] is data["holdout_accessed"] is data["defaults_changed"] is False
