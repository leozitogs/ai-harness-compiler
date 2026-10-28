"""Historical request stays immutable; archived sources do not authorize current execution."""

import hashlib
import json
from pathlib import Path

import pytest

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_campaign import SemanticCampaignRequestV1
from ai_harness_compiler.supervised_semantic_flow import _validate_request

ROOT = Path(__file__).resolve().parents[1]
REQUEST = ROOT / "evals/understanding/v4/development-campaign/request.json"
DIGEST = "a64cb6e7a779d4c5c201db9beb54238e793604fc564eb963b3987e37ffd88236"


def test_prepared_request_binds_all_reviewed_cases_in_the_approved_order():
    request = SemanticCampaignRequestV1.model_validate_json(REQUEST.read_bytes())
    corpus = json.loads((ROOT / request.corpus_source).read_bytes())
    assert request.sha256 == DIGEST
    assert request.corpus_sha256 == canonical_project_digest(corpus)
    assert (
        request.corpus_sha256 == "8f666df68dcc150caaa085051487784ec907219d8ab7f78de8b120f480f7381b"
    )
    assert len(request.flows) == len(corpus["cases"]) == 8
    assert [f.case.id for f in request.flows] == [e["id"] for e in corpus["cases"]]
    for flow, entry in zip(request.flows, corpus["cases"], strict=True):
        assert flow.case.snapshot_sha256 == entry["case_sha256"]
        assert flow.case.expectations_approval.model_dump() == corpus["approval"]["declaration"]
        assert flow.requested_model == "gpt-6.1-sol" and flow.rubric.approval is not None


def test_historical_source_freeze_preserves_exact_bytes_and_global_limits():
    request = SemanticCampaignRequestV1.model_validate_json(REQUEST.read_bytes())
    directory = REQUEST.parent / "legacy-source-archive"
    archive = json.loads((directory / "manifest.json").read_bytes())
    assert archive["request_sha256"] == request.sha256 == DIGEST
    archived = {e["path"]: e for e in archive["sources"]}
    assert len(archived) == 5 and len(request.sources) == 103
    assert set(archived).issubset({s.path for s in request.sources})
    for source in request.sources:
        path = ROOT / source.path
        if source.path in archived:
            entry = archived[source.path]
            assert entry["sha256"] == source.sha256
            assert entry["archive"] == source.sha256 + ".py.txt"
            path = directory / entry["archive"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == source.sha256
    # Historical bytes are replay evidence, never an exception to live source gates.
    with pytest.raises(ValueError, match="Transport source"):
        _validate_request(ROOT, request.supervision(0))
    assert request.max_calls == 16 and request.limits.max_worker_launches == 2
    assert request.limits.call_timeout_seconds == 180
    assert request.limits.cleanup_timeout_seconds == 20
    assert request.limits.session_timeout_seconds == 3600
    assert request.limits.max_input_bytes == 1024 * 1024
    assert request.limits.max_output_bytes == 4 * 1024 * 1024
    assert request.destination == "codex-chatgpt-cli" and request.split == "development"


def test_protocol_is_a_pending_request_without_transferred_authorization():
    protocol = json.loads((REQUEST.parent / "protocol.json").read_bytes())
    assert protocol["request_sha256"] == DIGEST
    assert protocol["execution_authorized"] is False and protocol["model_invocations"] == 0
    assert protocol["status"] == "pending-exact-execution-authorization"
    assert protocol["assets_read"] is False and protocol["holdout_accessed"] is False
    assert protocol["output_review"] == "not-run"
    assert protocol["model_qualification"] == "not-established"
    assert not (REQUEST.parent / "authorization.json").exists()
