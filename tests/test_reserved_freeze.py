"""Reproduce numeric-default drift on synthetic inputs; never reopen the real corpus."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_reserved_runs import workspace as workspace

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.reserved_evaluation import ReservedEvaluationProtocol
from ai_harness_compiler.models.reserved_run import ReservedRunAuthorization, ReservedRunRequest
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.reserved_freeze import (
    freeze_serialized_case,
    materialize_confirmed_correction,
    prospective_correction_request,
)
from ai_harness_compiler.reserved_runs import load_verified_payloads, run_reserved, sha256


def drifted_workspace(workspace):
    root, request, _, cases, _, _ = workspace
    data = cases[0].model_dump()
    data["project"]["constraints"].pop("max_build_cost_usd")
    before_serialization = AssessmentCase.model_validate(data)
    raw = json_text(before_serialization.model_dump()).encode()
    binding = request.protocol.reserved[0]
    (root / binding.artifact_path).write_bytes(raw)
    protocol = request.protocol.model_dump()
    protocol["reserved"][0].update(
        artifact_sha256=sha256(raw),
        case_sha256=before_serialization.snapshot_sha256,
        input_sha256=canonical_project_digest(before_serialization.project.model_dump()),
    )
    semantic = before_serialization.project.model_dump()
    semantic.pop("id")
    semantic.pop("name")
    protocol["reserved"][0]["semantic_sha256"] = canonical_project_digest(semantic)
    protocol["review"] = None
    model = ReservedEvaluationProtocol.model_validate(protocol)
    protocol["review"] = {
        "reviewer": "synthetic-po",
        "note": "Synthetic original freeze approval",
        "corpus_sha256": model.corpus_sha256,
    }
    data = request.model_dump()
    data["protocol"] = protocol
    original = ReservedRunRequest.model_validate(data)
    authorization = ReservedRunAuthorization(
        reviewer="synthetic-po",
        note="Synthetic original run authorization only",
        request_sha256=original.sha256,
        authorized=True,
    )
    corrected = original.protocol.model_dump()
    corrected["review"] = None
    corrected["reserved"][0] = freeze_serialized_case(
        raw,
        artifact_path=binding.artifact_path,
        family_id=binding.family_id,
        scenario=binding.scenario,
    ).model_dump()
    proposal = {
        "format": "reserved-fingerprint-correction-proposal/v1",
        "state": "pending-explicit-po-confirmation",
        "original_request_sha256": original.sha256,
        "corrected_protocol": corrected,
        "run_id": "synthetic-corrected",
        "output_path": ".factory/reserved-v2-executions/synthetic-corrected",
        "planned_reviewer": "synthetic-po",
        "planned_review_note": "Synthetic proposed review, activated only by fixture decision",
    }
    proposal["prospective_request_sha256"] = canonical_project_digest(
        prospective_correction_request(original, proposal)
    )
    return root, original, authorization, proposal, raw


def test_serialized_freeze_is_stable_after_numeric_default_normalization(workspace):
    _, original, _, proposal, raw = drifted_workspace(workspace)
    parsed = AssessmentCase.model_validate_json(raw)
    old = original.protocol.reserved[0]
    new = proposal["corrected_protocol"]["reserved"][0]
    assert json.loads(raw)["project"]["constraints"]["max_build_cost_usd"] == 0
    assert type(json.loads(raw)["project"]["constraints"]["max_build_cost_usd"]) is int
    assert type(parsed.project.constraints.max_build_cost_usd) is float
    assert new["artifact_sha256"] == old.artifact_sha256
    assert new["case_sha256"] == parsed.snapshot_sha256 != old.case_sha256
    assert (
        parsed.snapshot_sha256
        == AssessmentCase.model_validate_json(parsed.model_dump_json()).snapshot_sha256
    )
    assert proposal["corrected_protocol"]["review"] is None


def test_original_drift_stops_before_any_model_and_correction_needs_new_decision(workspace):
    root, original, authorization, proposal, _ = drifted_workspace(workspace)
    with pytest.raises(ValueError, match="PREFLIGHT_FAILED"):
        run_reserved(
            root, original, authorization, generator_factory=lambda _: pytest.fail("Model called")
        )
    with pytest.raises(ValueError, match="EXACT_NEW_PO_DECISION"):
        materialize_confirmed_correction(original, proposal, authorization)
    fresh = ReservedRunAuthorization(
        reviewer="synthetic-po",
        note="Synthetic explicit correction and run approval, not real PO",
        request_sha256=proposal["prospective_request_sha256"],
        authorized=True,
    )
    corrected = materialize_confirmed_correction(original, proposal, fresh)
    cases, _, _, _ = load_verified_payloads(root, corrected)
    assert len(cases) == 8
    assert corrected.sha256 == fresh.request_sha256
    assert original.protocol.review.corpus_sha256 != corrected.protocol.review.corpus_sha256
    assert (root / original.output_path / "preflight-error.json").exists()
    assert not (root / corrected.output_path).exists()


@pytest.mark.parametrize("change", ["raw-hash", "identity", "candidate", "inline-review"])
def test_correction_cannot_change_approved_inputs_or_fabricate_review(workspace, change):
    _, original, _, proposal, _ = drifted_workspace(workspace)
    modified = copy.deepcopy(proposal)
    if change == "raw-hash":
        modified["corrected_protocol"]["reserved"][0]["artifact_sha256"] = "0" * 64
    elif change == "identity":
        modified["corrected_protocol"]["reserved"][0]["case_id"] = "different"
    elif change == "candidate":
        modified["corrected_protocol"]["candidate"]["code_sha256"] = "0" * 64
    else:
        modified["corrected_protocol"]["review"] = original.protocol.review.model_dump()
    with pytest.raises(ValueError):
        prospective_correction_request(original, modified)


def test_actual_proposal_is_unsigned_and_keeps_all_original_raw_bindings():
    root = Path(__file__).resolve().parents[1]
    original = ReservedRunRequest.model_validate_json(
        (root / "evals/understanding/v2/reserved-execution/request.json").read_bytes()
    )
    raw = (root / "evals/understanding/v2/reserved-correction/proposal.json").read_bytes()
    proposal = json.loads(raw)
    corrected = ReservedEvaluationProtocol.model_validate(proposal["corrected_protocol"])
    assert corrected.review is None
    assert proposal["execution_authorized"] is False
    assert (
        canonical_project_digest(prospective_correction_request(original, proposal))
        == (proposal["prospective_request_sha256"])
    )
    assert proposal["prospective_request_sha256"] == (
        "f5e410f3831c90615f7e7fc60b92c339b95f619db99685da2d06d7e259194c55"
    )
    for old, new in zip(original.protocol.reserved, corrected.reserved, strict=True):
        assert (old.case_id, old.artifact_path, old.artifact_sha256) == (
            new.case_id,
            new.artifact_path,
            new.artifact_sha256,
        )
    with pytest.raises(ValidationError):
        ReservedRunRequest.model_validate_json(raw)
