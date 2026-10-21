"""Public metadata replay only: never read private reserved cases or PO review."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.reserved_evaluation import (
    ReservedCandidateFreeze,
    ReservedEvaluationProtocol,
    ReservedPreparationReport,
    prepare_reserved_evaluation,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evals/understanding/v2/reserved-preparation"


def read_metadata(name):
    return json.loads((BASE / name).read_bytes())


def test_frozen_candidate_sources_and_requested_profile_match():
    candidate = ReservedCandidateFreeze.model_validate(read_metadata("candidate.json"))
    code = read_metadata("candidate-code.json")
    profile = read_metadata("requested-profile.json")
    assert candidate.code_sha256 == canonical_project_digest(code)
    assert candidate.profile_sha256 == canonical_project_digest(profile)
    assert candidate.sha256 == "134acf0dc934e23913c8bc698e91e724fbdd13efdb825d4fcdcba854fe6bbeb2"
    assert code["source_commit"] == candidate.source_commit
    for source in code["files"]:
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]


def test_public_preparation_replays_without_private_payloads():
    protocol = ReservedEvaluationProtocol.model_validate(read_metadata("protocol.json"))
    path = ROOT / "docs/evidence/sprint-2-6-reserved-preparation-20261021/preparation.json"
    recorded = ReservedPreparationReport.model_validate_json(path.read_bytes())
    assert prepare_reserved_evaluation(protocol) == recorded
    assert recorded.pending_gates == [
        "human-expectations-review-missing",
        "execution-budget-not-proposed",
    ]
    assert recorded.execution_authorized is False
    assert recorded.model_calls == 0
    assert recorded.payload_validation == "not-performed"
    assert len(protocol.reserved) == 8
    binding = read_metadata("po-review-binding.json")
    assert binding["corpus_sha256"] == protocol.corpus_sha256
    assert binding["review"] == "pending"


def test_curator_metadata_is_bound_without_exposing_inputs():
    manifest = read_metadata("curation-manifest.json")
    provenance = read_metadata("curation-provenance.json")
    protocol = ReservedEvaluationProtocol.model_validate(read_metadata("protocol.json"))
    assert manifest["candidate_sha256"] == protocol.candidate.sha256
    assert manifest["reserved"] == [case.model_dump() for case in protocol.reserved]
    assert manifest["human_expectations_review"] == "pending"
    assert manifest["runtime_evaluation_calls"] == 0
    assert manifest["contract_validation"]["all_expectations_approval_null"]
    assert (
        provenance["isolation_declaration"]["development_or_prior_reserved_cases_opened"] is False
    )
    allowed = set(type(protocol.reserved[0]).model_fields)
    assert all(set(case) == allowed for case in manifest["reserved"])
    assert provenance["validation"]["validated_cases"] == 8


def test_later_explicit_po_review_preserves_initial_pending_snapshot():
    initial = ReservedEvaluationProtocol.model_validate(read_metadata("protocol.json"))
    reviewed = ReservedEvaluationProtocol.model_validate(read_metadata("protocol-reviewed.json"))
    declaration = read_metadata("po-expectations-review.json")
    path = ROOT / "docs/evidence/sprint-2-6-reserved-preparation-20261021/preparation-reviewed.json"
    report = ReservedPreparationReport.model_validate_json(path.read_bytes())
    assert initial.review is None
    assert reviewed.corpus_sha256 == initial.corpus_sha256
    assert reviewed.review.corpus_sha256 == initial.corpus_sha256
    assert reviewed.review.model_dump() == declaration["review"]
    assert declaration["reviewed_case_ids"] == [case.case_id for case in initial.reserved]
    assert len(declaration["reviewed_case_ids"]) == 8
    assert reviewed.reserved == initial.reserved
    assert prepare_reserved_evaluation(reviewed) == report
    assert report.pending_gates == ["execution-budget-not-proposed"]
    assert report.state == "blocked"
    assert not report.execution_authorized
    assert declaration["execution_authorized"] is False
