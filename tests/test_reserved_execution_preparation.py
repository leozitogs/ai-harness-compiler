"""Public request/source metadata only; no access to reserved inputs or model providers."""

import json
from pathlib import Path

from ai_harness_compiler.models.reserved_run import ReservedRunRequest
from ai_harness_compiler.reserved_runs import sha256, verify_frozen_sources

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "evals/understanding/v2/reserved-execution"


def test_concrete_request_preserves_frozen_candidate_and_po_expectations():
    raw = (FOLDER / "request.json").read_bytes()
    request = ReservedRunRequest.model_validate_json(raw)
    fingerprint = json.loads((FOLDER / "request-fingerprint.json").read_bytes())
    assert request.sha256 == fingerprint["request_sha256"]
    assert sha256(raw) == fingerprint["request_file_sha256"]
    assert request.protocol.corpus_sha256 == fingerprint["expectations_corpus_sha256"]
    assert (
        request.protocol.corpus_sha256
        == "c010e3373338edee86512a889ed12273c0a25ac44403e25e4c732fdbb97a8367"
    )
    assert request.protocol.review.corpus_sha256 == request.protocol.corpus_sha256
    assert (
        request.protocol.candidate.sha256
        == "134acf0dc934e23913c8bc698e91e724fbdd13efdb825d4fcdcba854fe6bbeb2"
    )
    assert request.protocol.budget.max_calls == 16
    assert request.protocol.budget.repetitions == 1
    assert request.protocol.budget.max_call_seconds == 180
    assert request.protocol.budget.max_session_seconds == 3600
    assert request.cleanup_grace_seconds == 20
    assert request.profile.observed_immutable_model is None
    assert request.profile.observed_sampling_parameters is None


def test_preparation_binds_code_but_never_claims_authorization_or_payload_reads(monkeypatch):
    request = ReservedRunRequest.model_validate_json((FOLDER / "request.json").read_bytes())
    original = Path.open
    private_cases = {ROOT / case.artifact_path for case in request.protocol.reserved}

    def guarded_open(path, *args, **kwargs):
        assert path not in private_cases, "Verification attempted to read a real reserved case"
        return original(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", guarded_open)
        verify_frozen_sources(ROOT, request)
    prepared = json.loads(
        (
            ROOT
            / "docs/evidence/sprint-2-6-reserved-execution-preparation-20261021/preparation.json"
        ).read_bytes()
    )
    assert prepared["request_sha256"] == request.sha256
    assert prepared["execution_authorized"] is False
    assert prepared["model_calls"] == 0
    assert prepared["payload_validation"] == "not-performed"
    assert prepared["state"] == "awaiting-explicit-human-execution-authorization"
