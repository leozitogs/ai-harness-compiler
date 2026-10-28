"""A failed prefix is neither a full campaign nor a transferred semantic acceptance."""

import json
from pathlib import Path

from ai_harness_compiler.models.semantic_campaign import (
    SemanticCampaignAuthorizationV1,
    SemanticCampaignCallV1,
    SemanticCampaignRequestV1,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "docs/evidence/sprint-2-6-v41-development-20261028"


def test_failed_campaign_counts_completed_failed_and_unstarted_cases_separately():
    data = json.loads((BASE / "execution.json").read_bytes())
    request = SemanticCampaignRequestV1.model_validate_json(
        (ROOT / "evals/understanding/v4/development-candidate-v41/request.json").read_bytes()
    )
    auth = SemanticCampaignAuthorizationV1.model_validate(data["authorization"])
    assert data["request_sha256"] == auth.request_sha256 == request.sha256
    assert data["authorization_question_id"] == "call_0fa94728f3b64dd6ae4befac35632ae4"
    assert data["technical_status"] == "failed" and data["failure_code"] == "case-failed"
    assert len(data["cases"]) == len(request.flows) == 8
    assert [c["case_sha256"] for c in data["cases"]] == [
        f.case.snapshot_sha256 for f in request.flows
    ]
    assert (
        data["completed_cases"]
        == sum(c["execution_status"] == "completed" for c in data["cases"])
        == 4
    )
    assert (
        data["failed_cases"] == sum(c["execution_status"] == "failed" for c in data["cases"]) == 1
    )
    assert (
        data["unstarted_cases"]
        == sum(c["execution_status"] == "not-started" for c in data["cases"])
        == 3
    )
    assert data["attempted_cases"] == data["completed_cases"] + data["failed_cases"] == 5
    assert data["invocations"] == len(data["calls"]) == 9
    assert data["successful_invocations"] == 8 and data["failed_invocations"] == 1


def test_first_failed_receipt_stops_sequence_and_closes_even_unused_budget():
    data = json.loads((BASE / "execution.json").read_bytes())
    calls = [SemanticCampaignCallV1.model_validate(c) for c in data["calls"]]
    assert [c.index for c in calls] == list(range(1, 10))
    assert all(c.receipt.status == "succeeded" for c in calls[:-1])
    assert calls[-1].flow_index == 4 and calls[-1].stage == "analysis"
    receipt = calls[-1].receipt
    assert receipt.status == "failed" and receipt.failure_code == "worker-failed"
    assert receipt.exit_code == 2 and receipt.response_sha256 is None
    assert all(c.receipt.root_reaped and c.receipt.tree_termination_requested for c in calls)
    assert data["budget_closed"] is True and data["unused_invocation_ceiling"] == 7
    assert data["unused_calls_authorized"] is False and data["offline_replay"] == "passed"
    assert data["elapsed_seconds"] < 3600


def test_incomplete_case_has_no_analysis_assessment_or_semantic_verdict():
    data = json.loads((BASE / "execution.json").read_bytes())
    for case in data["cases"][:4]:
        assert case["initial_assessment_status"] == "not-run" and case["initial_failures"] == []
        assert case["human_output_review"] == "pending"
    for case in data["cases"][4:]:
        assert case["analysis_sha256"] is None and case["audit_sha256"] is None
        assert case["initial_assessment_status"] is None and case["initial_failures"] is None
        assert case["human_output_review"] == "unavailable"
    assert sum(c["findings"] for c in data["cases"]) == 49
    assert sum(c["components"] for c in data["cases"]) == 72
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert data["assets_read"] is False and data["holdout_accessed"] is False
    diagnosis = json.loads((BASE / "diagnosis.json").read_bytes())
    assert diagnosis["worker_request_contract_valid"] and diagnosis["response_schema_valid"]
    assert diagnosis["serialized_payload_bytes"] < diagnosis["input_limit_bytes"]
    assert diagnosis["approved_case_unchanged"] and diagnosis["unchanged_schema_from_baseline"]
    assert (
        diagnosis["raw_provider_error_retained"] is False
        and diagnosis["raw_response_retained"] is False
    )
    assert diagnosis["cause"].startswith("unknown") and diagnosis["new_model_invocations"] == 0
