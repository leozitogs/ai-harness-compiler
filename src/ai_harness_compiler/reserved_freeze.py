"""Freeze serialized cases, not pre-serialization Python defaults. No I/O or model calls."""

import copy
import hashlib
from typing import Any

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.reserved_evaluation import (
    ReservedCaseBinding,
    ReservedEvaluationProtocol,
    Scenario,
    reserved_preparation_gates,
)
from ai_harness_compiler.models.reserved_run import (
    ReservedRunAuthorization,
    ReservedRunRequest,
    validate_run_authorization,
)
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_eval import semantic_snapshot_digest

DERIVED_DIGESTS = {"case_sha256", "input_sha256", "semantic_sha256"}


def freeze_serialized_case(
    raw: bytes, *, artifact_path: str, family_id: str, scenario: Scenario
) -> ReservedCaseBinding:
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError("RESERVED_FREEZE_SIZE")
    case = AssessmentCase.model_validate_json(raw)
    roundtrip = AssessmentCase.model_validate_json(case.model_dump_json())
    if case.snapshot_sha256 != roundtrip.snapshot_sha256:
        raise ValueError("RESERVED_FREEZE_UNSTABLE_ROUNDTRIP")
    return ReservedCaseBinding(
        case_id=case.id,
        project_id=case.project.id,
        family_id=family_id,
        scenario=scenario,
        artifact_path=artifact_path,
        artifact_sha256=hashlib.sha256(raw).hexdigest(),
        case_sha256=case.snapshot_sha256,
        input_sha256=canonical_project_digest(case.project.model_dump()),
        semantic_sha256=semantic_snapshot_digest(case.project),
    )


def prospective_correction_request(
    original: ReservedRunRequest, proposal: dict[str, Any]
) -> dict[str, Any]:
    """Unsigned planned values only. Does NOT instantiate an approved request or review."""
    if (
        proposal.get("format") != "reserved-fingerprint-correction-proposal/v1"
        or proposal.get("state") != "pending-explicit-po-confirmation"
        or proposal.get("original_request_sha256") != original.sha256
    ):
        raise ValueError("RESERVED_CORRECTION_PROPOSAL_BINDING")
    corrected = ReservedEvaluationProtocol.model_validate(proposal["corrected_protocol"])
    if corrected.review is not None:
        raise ValueError("Pending correction must not fabricate a corpus review")
    before, after = original.protocol.model_dump(), corrected.model_dump()
    before["review"] = after["review"] = None
    changed = False
    for old, new in zip(before["reserved"], after["reserved"], strict=True):
        for field in DERIVED_DIGESTS:
            changed |= old[field] != new[field]
            old.pop(field)
            new.pop(field)
    if before != after:
        raise ValueError("Correction may only change derived digests of identical raw artifacts")
    if (
        not changed
        or proposal["run_id"] == original.id
        or (proposal["output_path"] == original.output_path)
    ):
        raise ValueError("Correction requires changed fingerprints and a new run/output identity")
    if reserved_preparation_gates(corrected) != ["human-expectations-review-missing"]:
        raise ValueError("Correction leaves other preparation gates unresolved")
    if not original.protocol.review or proposal["planned_reviewer"] != (
        original.protocol.review.reviewer
    ):
        raise ValueError("Correction requires the original PO's explicit confirmation")
    result = copy.deepcopy(original.model_dump())
    result["id"], result["output_path"] = proposal["run_id"], proposal["output_path"]
    result["protocol"] = corrected.model_dump()
    # These are proposed document values, not a human declaration or an effective approval.
    result["protocol"]["review"] = {
        "reviewer": proposal["planned_reviewer"],
        "note": proposal["planned_review_note"],
        "authority": "human-declared-not-authenticated",
        "corpus_sha256": corrected.corpus_sha256,
    }
    return result


def materialize_confirmed_correction(
    original: ReservedRunRequest, proposal: dict[str, Any], authorization: ReservedRunAuthorization
) -> ReservedRunRequest:
    """Only an explicit new PO decision bound to the prospective request activates the review."""
    data = prospective_correction_request(original, proposal)
    expected = canonical_project_digest(data)
    if (
        authorization.request_sha256 != expected
        or proposal.get("prospective_request_sha256") != expected
        or authorization.reviewer != proposal["planned_reviewer"]
    ):
        raise ValueError("RESERVED_CORRECTION_REQUIRES_EXACT_NEW_PO_DECISION")
    request = ReservedRunRequest.model_validate(data)
    validate_run_authorization(request, authorization)
    return request
