"""Observed transport metadata cannot erase coverage failures or create human PASS."""

import json
from pathlib import Path

from ai_harness_compiler.models.semantic_campaign import (
    SemanticCampaignAuthorizationV1,
    SemanticCampaignCallV1,
    SemanticCampaignRequestV1,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/sprint-2-6-v4-development-20261027/execution.json"


def test_observed_execution_binds_actual_scoped_authorization_and_all_cases():
    data = json.loads(EVIDENCE.read_bytes())
    request = SemanticCampaignRequestV1.model_validate_json(
        (ROOT / "evals/understanding/v4/development-campaign/request.json").read_bytes()
    )
    auth = SemanticCampaignAuthorizationV1.model_validate(data["authorization"])
    assert data["request_sha256"] == auth.request_sha256 == request.sha256
    assert data["authorization_question_id"] == "call_bbe0268ecd30479b8bb260e889d999d8"
    assert data["authorization_answer"] == "Autorizo esta única rodada nesses limites"
    assert data["campaign_id"] == request.campaign_id
    assert [c["case_id"] for c in data["cases"]] == [f.case.id for f in request.flows]
    assert [c["case_sha256"] for c in data["cases"]] == [
        f.case.snapshot_sha256 for f in request.flows
    ]
    assert data["model_invocations"] == len(data["calls"]) == request.max_calls == 16
    assert data["budget_closed"] is True and data["offline_replay"] == "passed"
    assert data["technical_status"] == "completed"


def test_public_receipts_preserve_serial_global_budget_and_cleanup_observations():
    data = json.loads(EVIDENCE.read_bytes())
    assert 0 < data["elapsed_seconds"] < 3600
    end = 0.0
    for index, raw in enumerate(data["calls"], 1):
        call = SemanticCampaignCallV1.model_validate(raw)
        assert call.index == index and call.flow_index == (index - 1) // 2
        assert call.started_offset_seconds >= end
        end = call.finished_offset_seconds
        assert end <= data["elapsed_seconds"]
        receipt = call.receipt
        assert receipt is not None and receipt.status == "succeeded"
        assert receipt.root_reaped and receipt.tree_termination_requested
        assert receipt.containment == "windows-job"
        assert receipt.granted_seconds <= min(180, 3600 - call.started_offset_seconds - 20)
    assert sum(c["receipt"]["elapsed_seconds"] for c in data["calls"]) <= data["elapsed_seconds"]


def test_transport_success_preserves_initial_failures_and_pending_human_review():
    data = json.loads(EVIDENCE.read_bytes())
    failed = {c["case_id"]: c for c in data["cases"] if c["initial_assessment_status"] == "fail"}
    assert set(failed) == {"dev-ambiguous-v4", "dev-compatible-rules-v4"}
    assert [f["reference"] for f in failed["dev-ambiguous-v4"]["initial_failures"]] == [
        "required-1"
    ]
    assert [f["reference"] for f in failed["dev-compatible-rules-v4"]["initial_failures"]] == [
        "required-2",
        "required-4",
    ]
    assert sum(len(c["initial_failures"]) for c in data["cases"]) == 3
    assert sum(c["initial_assessment_status"] == "not-run" for c in data["cases"]) == 6
    assert all(c["human_output_review"] == "pending" for c in data["cases"])
    assert all(c["disposition"] == c["expected_behavior"] for c in data["cases"])
    assert data["output_review"] == "pending-human-review"
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert data["assets_read"] is False and data["holdout_accessed"] is False
    assert data["defaults_changed"] is False
    assert sum(c["findings"] for c in data["cases"]) == 88
    assert sum(c["components"] for c in data["cases"]) == 128
