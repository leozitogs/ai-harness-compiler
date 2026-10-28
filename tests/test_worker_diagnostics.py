"""Sanitized observed categories, never inferred historical causes or raw exceptions."""

import io
import json
import sys
from pathlib import Path
from time import monotonic
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from test_supervised_transport import limits

from ai_harness_compiler.adapters import codex_cli, semantic_worker_v4
from ai_harness_compiler.adapters.process_supervisor import WorkerOutcome, invoke_json_worker
from ai_harness_compiler.models.supervised_transport import TransportReceiptV1
from ai_harness_compiler.models.worker_diagnostic import WorkerDiagnosticV1, diagnose_worker


def payload():
    return dict(
        model="synthetic.model",
        prompt="Private synthetic source",
        response_schema={"type": "object"},
        timeout_seconds=3,
    )


def streams(monkeypatch, raw):
    output = io.BytesIO()
    monkeypatch.setattr(sys, "stdin", SimpleNamespace(buffer=io.BytesIO(raw)))
    monkeypatch.setattr(sys, "stdout", SimpleNamespace(buffer=output))
    return output


@pytest.mark.parametrize("code,expected", list(semantic_worker_v4.PROVIDER_EXITS.items()))
def test_exact_adapter_codes_leave_only_exit_status(monkeypatch, capsys, code, expected):
    class Fake:
        def __init__(self, settings):
            pass

        def generate_json(self, prompt, schema):
            raise ValueError(code)

    monkeypatch.setattr(codex_cli, "CodexCompactModel", Fake)
    output = streams(monkeypatch, json.dumps(payload()).encode())
    assert semantic_worker_v4.main() == expected
    assert output.getvalue() == b""
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize(
    "error,expected",
    [
        (ValueError("CODEX_PROVIDER_ERROR secret=private"), 31),
        (ValueError("CODEX_PROVIDER_ERROR", "private"), 31),
        (OSError("private path or key"), 36),
        (RuntimeError("private runtime data"), 31),
    ],
)
def test_unknown_or_decorated_errors_are_not_parsed_or_leaked(monkeypatch, error, expected):
    class Fake:
        def __init__(self, settings):
            pass

        def generate_json(self, prompt, schema):
            raise error

    monkeypatch.setattr(codex_cli, "CodexCompactModel", Fake)
    output = streams(monkeypatch, json.dumps(payload()).encode())
    assert semantic_worker_v4.main() == expected
    assert output.getvalue() == b""


@pytest.mark.parametrize(
    "raw,expected",
    [(b"{}", 21), (b"\xff", 21), (b"x" * (semantic_worker_v4.MAX_REQUEST_BYTES + 1), 20)],
    ids=["invalid-contract", "invalid-utf8", "input-limit"],
)
def test_invalid_input_never_instantiates_provider(monkeypatch, raw, expected):
    monkeypatch.setattr(codex_cli, "CodexCompactModel", lambda *a: pytest.fail("No provider"))
    output = streams(monkeypatch, raw)
    assert semantic_worker_v4.main() == expected and output.getvalue() == b""


def receipt(exit_code=25, failure_code="worker-failed"):
    return TransportReceiptV1(
        index=1,
        payload_sha256="a" * 64,
        command_sha256="b" * 64,
        granted_seconds=3.0,
        elapsed_seconds=1.0,
        worker_pid=123,
        containment="posix-session",
        root_reaped=True,
        tree_termination_requested=True,
        exit_code=exit_code,
        status="failed",
        failure_code=failure_code,
    )


@pytest.mark.parametrize(
    "exit_code,category", [(25, "provider-timeout"), (2, "unknown"), (99, "unknown")]
)
def test_diagnostic_preserves_unknown_historical_codes(exit_code, category):
    diagnostic = diagnose_worker(receipt(exit_code))
    assert diagnostic.category == category
    assert WorkerDiagnosticV1.model_validate_json(diagnostic.model_dump_json()) == diagnostic
    Draft202012Validator(WorkerDiagnosticV1.model_json_schema()).validate(
        diagnostic.model_dump(mode="json")
    )
    with pytest.raises(ValueError):
        WorkerDiagnosticV1.model_validate(
            diagnostic.model_dump() | dict(category="subscription-required")
        )


def test_supervisor_timeout_is_not_reclassified_by_a_worker_exit_code():
    assert diagnose_worker(receipt(25, "call-timeout")).category == "not-worker-failure"


def test_real_contained_worker_retains_category_and_no_error_text(tmp_path):
    worker = Path(__file__).parent / "fixtures/diagnostic_semantic_worker.py"
    result = invoke_json_worker(
        [sys.executable, "-I", str(worker.resolve()), "CODEX_CHATGPT_LOGIN_REQUIRED"],
        payload(),
        cwd=tmp_path,
        limits=limits(),
        session_deadline=monotonic() + 15,
        index=1,
    )
    assert result.receipt.exit_code == 23 and result.receipt.failure_code == "worker-failed"
    assert (
        result.response is None
        and result.receipt.root_reaped
        and result.receipt.tree_termination_requested
    )
    assert diagnose_worker(result.receipt).category == "subscription-required"


def test_categorized_failure_still_closes_campaign_without_retry(tmp_path, monkeypatch):
    from test_semantic_campaign import prepare

    import ai_harness_compiler.semantic_campaign as campaign

    root, request, auth, _, seen, delegate = prepare(tmp_path, monkeypatch)

    def broken(*args, **kwargs):
        original = delegate(*args, **kwargs)
        data = original.receipt.model_dump() | dict(
            status="failed", failure_code="worker-failed", exit_code=25, response_sha256=None
        )
        return WorkerOutcome(TransportReceiptV1.model_validate(data), None)

    monkeypatch.setattr(campaign, "invoke_json_worker", broken)
    report = campaign.run_campaign(root, request, auth)
    assert (
        len(seen) == len(report.calls) == 1 and report.status == "failed" and report.budget_closed
    )
    assert diagnose_worker(report.calls[0].receipt).category == "provider-timeout"
    assert campaign.validate_campaign(root, request.campaign_id) == report
    with pytest.raises(FileExistsError):
        campaign.run_campaign(root, request, auth)
