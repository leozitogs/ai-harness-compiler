"""Real local subprocess supervision with synthetic payloads; no inference calls."""

import ctypes
import io
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from time import monotonic, sleep
from types import SimpleNamespace

import pytest
from jsonschema import Draft202012Validator
from test_semantic_assessment import declaration
from test_semantic_flow_v4 import audit_proposal, fixtures, request_pair

import ai_harness_compiler.supervised_semantic_flow as flow
from ai_harness_compiler.adapters.process_supervisor import invoke_json_worker
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.supervised_transport import (
    SupervisedFlowAuthorizationV1,
    SupervisedFlowReportV1,
    TransportLimitsV1,
    TransportReceiptV1,
)
from ai_harness_compiler.offline_schema_registry import OFFLINE_MODELS

WORKER = Path(__file__).parent / "fixtures/json_worker.py"
UNICODE_WORKER = Path(__file__).parent / "fixtures/unicode_semantic_worker.py"


def limits(**changes):
    return TransportLimitsV1.model_validate(
        dict(call_timeout_seconds=3, cleanup_timeout_seconds=2, session_timeout_seconds=15)
        | changes
    )


def command(mode="echo", *args):
    return [sys.executable, str(WORKER.resolve()), mode, *map(str, args)]


def invoke(tmp_path, mode="echo", *, policy=None, deadline=None):
    return invoke_json_worker(
        command(mode),
        {"synthetic": "dado de teste"},
        cwd=tmp_path,
        limits=policy or limits(),
        session_deadline=deadline or monotonic() + 15,
        index=1,
    )


def test_success_is_bounded_and_root_reaped(tmp_path):
    result = invoke(tmp_path)
    assert result.receipt.status == "succeeded"
    assert result.receipt.root_reaped and result.receipt.tree_termination_requested
    assert result.receipt.containment == ("windows-job" if os.name == "nt" else "posix-session")
    assert json.loads(result.response)["received"] == {"synthetic": "dado de teste"}
    assert result.receipt.response_sha256 == canonical_project_digest(json.loads(result.response))
    Draft202012Validator(TransportReceiptV1.model_json_schema()).validate(
        result.receipt.model_dump()
    )


@pytest.mark.parametrize(
    "mode,expected",
    [
        ("timeout", "call-timeout"),
        ("overflow", "output-limit"),
        ("invalid", "invalid-output"),
        ("exit", "worker-failed"),
    ],
)
def test_real_process_failures_are_sanitized_and_cleaned(tmp_path, mode, expected):
    started = monotonic()
    result = invoke(tmp_path, mode, policy=limits(call_timeout_seconds=1, max_output_bytes=1024))
    assert result.receipt.status == "failed"
    assert result.receipt.failure_code == expected
    assert result.response is None
    assert result.receipt.root_reaped and result.receipt.tree_termination_requested
    assert monotonic() - started < 6


@pytest.mark.parametrize("gate", ["budget", "input"])
def test_rejected_work_does_not_spawn(tmp_path, gate):
    policy = limits(max_input_bytes=1024)
    result = invoke_json_worker(
        [str(tmp_path / "must-not-run")],
        {"value": "x" * 2000 if gate == "input" else "x"},
        cwd=tmp_path,
        limits=policy,
        session_deadline=monotonic() + (1 if gate == "budget" else 15),
        index=1,
    )
    assert result.receipt.worker_pid is None
    assert result.receipt.failure_code == ("session-budget" if gate == "budget" else "input-limit")


def test_spawn_failure_never_claims_a_worker(tmp_path):
    result = invoke_json_worker(
        [str(tmp_path / "missing-program")],
        {},
        cwd=tmp_path,
        limits=limits(),
        session_deadline=monotonic() + 15,
        index=1,
    )
    assert result.receipt.status == "failed"
    assert result.receipt.failure_code == "spawn-failed"
    assert result.receipt.worker_pid is None
    assert not result.receipt.root_reaped


def process_running(pid):
    if os.name == "nt":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel.OpenProcess(0x1000, False, pid)
        if not handle:
            return False
        try:
            code = ctypes.c_ulong()
            assert kernel.GetExitCodeProcess(handle, ctypes.byref(code))
            return code.value == 259
        finally:
            kernel.CloseHandle(handle)
    path = Path(f"/proc/{pid}/stat")
    try:
        return path.read_text().split(")", 1)[1].split()[0] != "Z"
    except FileNotFoundError:
        return False  # The process can disappear between lookup and read after SIGKILL.


def test_timeout_stops_descendant_as_well_as_worker(tmp_path):
    pidfile = tmp_path / "child-pid"
    result = invoke_json_worker(
        command("child", pidfile),
        {},
        cwd=tmp_path,
        limits=limits(call_timeout_seconds=2),
        session_deadline=monotonic() + 15,
        index=1,
    )
    assert result.receipt.failure_code == "call-timeout"
    assert pidfile.is_file()
    pid = int(pidfile.read_text())
    deadline = monotonic() + 2
    while process_running(pid) and monotonic() < deadline:
        sleep(0.02)
    assert not process_running(pid)
    assert result.receipt.root_reaped


@pytest.mark.parametrize(
    "change",
    [
        dict(call_timeout_seconds=0),
        dict(cleanup_timeout_seconds=0),
        dict(session_timeout_seconds=2, cleanup_timeout_seconds=2),
        dict(max_worker_launches=3),
        dict(max_output_bytes=100000000),
    ],
)
def test_limits_cannot_expand_unchecked(change):
    with pytest.raises(ValueError):
        limits(**change)


def prepare(tmp_path, monkeypatch, mode="flow"):
    case, rubric_, analysis = fixtures()
    nested, _ = request_pair(case, rubric_, analysis)
    root = tmp_path / "repository"
    source_root = Path(__file__).resolve().parents[1]
    shutil.copytree(
        source_root / "src/ai_harness_compiler",
        root / "src/ai_harness_compiler",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for name in ["pyproject.toml", "uv.lock"]:
        shutil.copyfile(source_root / name, root / name)
    analysis_file, audit_file = tmp_path / "analysis.json", tmp_path / "audit.json"
    analysis_file.write_text(analysis.proposal.model_dump_json(), encoding="utf-8")
    audit_file.write_text(json.dumps(audit_proposal(analysis)), encoding="utf-8")
    monkeypatch.setattr(flow, "worker_command", lambda: command(mode, analysis_file, audit_file))
    # This fixture checks end-to-end integrity, including source hashing and typed
    # validation on disk. It is not a 15-second performance assertion. Keep the
    # strict per-worker deadline; test session expiry separately below.
    request = flow.prepare_supervised_flow(root, nested, limits(session_timeout_seconds=120))
    auth = SupervisedFlowAuthorizationV1(
        **declaration().model_dump(), request_sha256=request.sha256, authorized=True
    )
    return root, request, auth


def test_real_offline_worker_integrates_both_stages_and_replays(tmp_path, monkeypatch):
    root, request, auth = prepare(tmp_path, monkeypatch)
    result = flow.run_supervised_flow(root, request, auth)
    assert result.status == result.flow_result.status == "completed"
    assert len(result.receipts) == 2
    assert result.flow_result.assessment.status == "not-run"
    assert flow.validate_supervised_flow(root, request.flow.run_id) == result
    assert result.model_qualification == "not-established"
    for model in [request, auth, result]:
        Draft202012Validator(type(model).model_json_schema()).validate(
            model.model_dump(mode="json")
        )
    with pytest.raises(FileExistsError):
        flow.run_supervised_flow(root, request, auth)


@pytest.mark.parametrize("gate", ["auth", "sources", "runtime", "command", "case-approval"])
def test_outer_gates_precede_any_worker_or_claim(tmp_path, monkeypatch, gate):
    root, request, auth = prepare(tmp_path, monkeypatch)
    if gate == "auth":
        auth.request_sha256 = "0" * 64
    elif gate == "sources":
        request.sources[0].sha256 = "0" * 64
    elif gate == "runtime":
        request.python_runtime = "changed"
    elif gate == "command":
        request.worker_command_sha256 = "0" * 64
    else:
        request.flow.case.expectations_approval = None
    monkeypatch.setattr(
        flow, "invoke_json_worker", lambda *a, **k: pytest.fail("Worker must not start")
    )
    with pytest.raises(ValueError):
        flow.run_supervised_flow(root, request, auth)
    assert not (root / ".factory").exists()


def test_supervised_first_failure_stops_without_second_invocation(tmp_path, monkeypatch):
    root, request, auth = prepare(tmp_path, monkeypatch, mode="invalid")
    result = flow.run_supervised_flow(root, request, auth)
    assert result.status == "failed"
    assert len(result.receipts) == len(result.flow_result.calls) == 1
    assert result.receipts[0].failure_code == "invalid-output"
    assert flow.validate_supervised_flow(root, request.flow.run_id) == result


@pytest.mark.parametrize("mutation", ["receipt", "attempt", "claim", "response"])
def test_supervised_replay_rejects_changed_artifacts(tmp_path, monkeypatch, mutation):
    root, request, auth = prepare(tmp_path, monkeypatch)
    flow.run_supervised_flow(root, request, auth)
    directory = root / ".factory" / "supervised-v4-runs" / request.flow.run_id
    path = {
        "receipt": directory / "receipt-1.json",
        "attempt": directory / "attempt-1.json",
        "claim": root / ".factory" / "supervised-v4-claims" / f"{request.sha256}.json",
        "response": root
        / ".factory"
        / "semantic-v4-runs"
        / request.flow.run_id
        / "analysis-response.json",
    }[mutation]
    path.write_text("{}")
    with pytest.raises(ValueError):
        flow.validate_supervised_flow(root, request.flow.run_id)


def test_report_cannot_raise_limits_or_rebind_authorization(tmp_path, monkeypatch):
    root, request, auth = prepare(tmp_path, monkeypatch)
    result = flow.run_supervised_flow(root, request, auth)
    data = result.model_dump()
    data["receipts"][0]["granted_seconds"] = 300.0
    with pytest.raises(ValueError):
        SupervisedFlowReportV1.model_validate(data)
    data = result.model_dump()
    data["flow_result"]["authorization"]["reviewer"] = "someone-else"
    with pytest.raises(ValueError):
        SupervisedFlowReportV1.model_validate(data)
    data = result.model_dump()
    data["status"] = "failed"
    data["receipts"][-1].update(status="failed", failure_code="call-timeout")
    with pytest.raises(ValueError, match="failed transport"):
        SupervisedFlowReportV1.model_validate(data)


@pytest.mark.parametrize("mutation", ["elapsed", "order", "command", "incomplete", "workerless"])
def test_receipt_and_session_contradictions_are_rejected(tmp_path, monkeypatch, mutation):
    root, request, auth = prepare(tmp_path, monkeypatch)
    result = flow.run_supervised_flow(root, request, auth)
    data = result.model_dump()
    if mutation == "elapsed":
        data["session_elapsed_seconds"] = 0.0
    elif mutation == "order":
        data["receipts"].reverse()
    elif mutation == "command":
        data["receipts"][0]["command_sha256"] = "0" * 64
    elif mutation == "incomplete":
        data["receipts"][0]["tree_termination_requested"] = False
    else:
        data["receipts"][0]["worker_pid"] = None
    with pytest.raises(ValueError):
        SupervisedFlowReportV1.model_validate(data)


def test_session_overrun_is_failed_without_erasing_nested_technical_result(tmp_path, monkeypatch):
    root, request, auth = prepare(tmp_path, monkeypatch)
    result = flow.run_supervised_flow(root, request, auth)
    data = result.model_dump()
    data["session_elapsed_seconds"] = request.limits.session_timeout_seconds + 1.0
    with pytest.raises(ValueError):
        SupervisedFlowReportV1.model_validate(data)
    data["status"] = "failed"
    failed = SupervisedFlowReportV1.model_validate(data)
    assert failed.status == "failed"
    assert failed.flow_result.status == "completed"


def test_new_supervision_schemas_roundtrip(tmp_path, monkeypatch):
    root, request, auth = prepare(tmp_path, monkeypatch)
    result = flow.run_supervised_flow(root, request, auth)
    values = {
        "supervised-flow-request-v1": request,
        "supervised-flow-authorization-v1": auth,
        "supervised-flow-report-v1": result,
        "transport-limits-v1": request.limits,
        "transport-receipt-v1": result.receipts[0],
    }
    for name, value in values.items():
        model = OFFLINE_MODELS[name]
        Draft202012Validator(model.model_json_schema()).validate(value.model_dump(mode="json"))
        assert model.model_validate_json(value.model_dump_json()) == value


def test_fixed_worker_can_start_isolated_but_invalid_request_never_dispatches(tmp_path):
    result = subprocess.run(
        flow.worker_command(),
        input=b"{}",
        capture_output=True,
        timeout=10,
        cwd=tmp_path,
        check=False,
    )
    assert result.returncode == 21
    assert result.stdout == result.stderr == b""


@pytest.mark.parametrize("encoding", ["cp1252", "ascii", "utf-8"])
@pytest.mark.parametrize("value", ["ação", "ação / 東京 / 🧪"], ids=["latin", "multilingual"])
def test_actual_worker_pipe_preserves_unicode_independently_of_text_encoding(
    tmp_path, encoding, value
):
    outcome = invoke_json_worker(
        [sys.executable, "-I", str(UNICODE_WORKER.resolve()), encoding, value],
        dict(
            model="synthetic.model",
            prompt="Offline Unicode transport test",
            response_schema={"type": "object"},
            timeout_seconds=3,
        ),
        cwd=tmp_path,
        limits=limits(),
        session_deadline=monotonic() + 15,
        index=1,
    )
    assert outcome.receipt.status == "succeeded"
    assert outcome.receipt.root_reaped and outcome.receipt.tree_termination_requested
    assert json.loads(outcome.response) == {"text": value}
    assert outcome.receipt.response_sha256 == canonical_project_digest({"text": value})


@pytest.mark.parametrize("valid", [False, True])
def test_worker_validates_before_provider_and_preserves_only_final_response(monkeypatch, valid):
    from ai_harness_compiler.adapters import codex_cli, semantic_worker_v4

    calls = []

    class Fake:
        def __init__(self, settings):
            calls.append(settings)

        def generate_json(self, prompt, schema):
            assert prompt == "Synthetic source"
            assert schema == {"type": "object"}
            return '{"final":"synthetic"}'

    monkeypatch.setattr(codex_cli, "CodexCompactModel", Fake)
    payload = (
        dict(
            model="synthetic.model",
            prompt="Synthetic source",
            response_schema={"type": "object"},
            timeout_seconds=3,
        )
        if valid
        else {}
    )
    monkeypatch.setattr(
        sys, "stdin", SimpleNamespace(buffer=io.BytesIO(json.dumps(payload).encode()))
    )
    output = io.BytesIO()
    monkeypatch.setattr(sys, "stdout", SimpleNamespace(buffer=output))
    assert semantic_worker_v4.main() == (0 if valid else 21)
    assert len(calls) == (1 if valid else 0)
    if valid:
        assert json.loads(output.getvalue()) == {"response": '{"final":"synthetic"}'}
    else:
        assert output.getvalue() == b""
