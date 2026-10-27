"""Public pending proposal: literal expectations and hashes, without inference."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import preflight_case
from ai_harness_compiler.models.supervised_transport import SupervisedFlowRequestV1

ROOT = Path(__file__).resolve().parents[1]
PROPOSAL = ROOT / "evals/understanding/v4/compatibility-proposal"


def test_public_case_preserves_pending_expectations_and_fragment_rejection():
    case = AssessmentCaseV3.model_validate_json((PROPOSAL / "case.json").read_bytes())
    assert case.expectations_approval is None
    assert case.expected_behavior == "ready"
    assert case.required_content_rejection_pointers == ["/branding/principles/0"]
    assert not case.required_project_rejection_pointers
    assert not case.requires_conflict
    assert not case.project.assets
    assert case.project.domain is None and case.project.domain_profile is None
    assert {item.id: item.disposition for item in case.obligations} == {
        "purpose": "statement",
        "responsible-identity": "requirement",
        "publication-approval": "rule",
        "content-origin": "requirement",
    }
    preflight = preflight_case(case, "SemanticAnalysis/v4")
    assert preflight.status == "compatible"
    assert preflight.model_dump(mode="json") == json.loads(
        (PROPOSAL / "preflight.json").read_text(encoding="utf-8")
    )


def test_proposed_request_and_manifest_bind_exact_public_snapshots():
    protocol = json.loads((PROPOSAL / "protocol.json").read_text(encoding="utf-8"))
    request_raw = (PROPOSAL / "request.proposed.json").read_bytes()
    request = SupervisedFlowRequestV1.model_validate_json(request_raw)
    case_raw = (PROPOSAL / "case.json").read_bytes()
    case = AssessmentCaseV3.model_validate_json(case_raw)
    assert request.flow.case == case
    assert case.snapshot_sha256 == protocol["case_sha256"]
    assert request.sha256 == protocol["proposed_request_sha256"]
    assert hashlib.sha256(case_raw).hexdigest() == protocol["case_file_sha256"]
    assert hashlib.sha256(request_raw).hexdigest() == protocol["proposed_request_file_sha256"]
    rubric_raw = (ROOT / protocol["rubric_source"]).read_bytes()
    assert hashlib.sha256(rubric_raw).hexdigest() == protocol["rubric_file_sha256"]
    assert request.flow.rubric.model_dump(mode="json") == json.loads(rubric_raw)
    assert (
        canonical_project_digest(request.flow.rubric.model_dump())
        == protocol["rubric_snapshot_sha256"]
    )


def test_proposal_cannot_represent_granted_budget_or_approved_outputs():
    protocol = json.loads((PROPOSAL / "protocol.json").read_text(encoding="utf-8"))
    request = SupervisedFlowRequestV1.model_validate_json(
        (PROPOSAL / "request.proposed.json").read_bytes()
    )
    assert protocol["status"] == "pending-po-expectations"
    assert protocol["execution_authorized"] is False
    assert protocol["expectations_approved"] is False
    assert protocol["model_invocations_observed"] == 0
    assert protocol["max_proposed_invocations"] == request.flow.max_generator_calls == 2
    assert request.limits.model_dump() == protocol["limits"]
    assert request.limits.call_timeout_seconds == 180
    assert request.limits.cleanup_timeout_seconds == 20
    assert request.limits.session_timeout_seconds == 400
    assert request.limits.max_input_bytes == 1024 * 1024
    assert request.limits.max_output_bytes == 4 * 1024 * 1024
    assert request.flow.requested_model == protocol["requested_model"] == "gpt-6.1-sol"
    assert request.destination == protocol["destination"] == "codex-chatgpt-cli"
    assert all(protocol[key] is False for key in ["retry", "repair", "fallback", "resume"])
    assert protocol["compilation_eligibility"] == "not-authorized"
    assert protocol["model_qualification"] == "not-established"
    assert not list(PROPOSAL.glob("*authorization*"))
