"""Session budgets and IPC tests; executor fixtures do not prove model execution."""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError

from ai_harness_compiler.adapters.ollama import SYSTEM_PROMPT
from ai_harness_compiler.cli import main
from ai_harness_compiler.model_sessions import (
    IsolatedOllamaExecutor,
    make_plan,
    run_session,
    session_bytes,
    validate_session,
)
from ai_harness_compiler.model_worker import execute as execute_worker
from ai_harness_compiler.models.model_session import (
    ModelIdentity,
    ModelSessionReport,
    ProviderObservation,
    SessionSettings,
    WorkerRequest,
    WorkerResult,
)
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec
from ai_harness_compiler.semantic_eval import FrozenCorpus

CORPUS = Path(__file__).resolve().parents[1] / "evals/understanding/v1"
PROMPT_SHA = hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()


class FakeExecutor:
    def __init__(self, error=None, change=False):
        self.requests = []
        self.error = error
        self.change = change

    def execute(self, request, timeout):
        self.requests.append(request)
        if self.error:
            return WorkerResult(status="error", error_code=self.error)
        ref = request.request.references[0]
        spec = ProjectUnderstandingSpec.model_validate(
            {
                "request": request.request.model_dump(),
                "proposal": {
                    "statements": [
                        {
                            "id": "purpose",
                            "subject": "purpose",
                            "status": "declared",
                            "text": ref.value,
                            "source_refs": [ref.id],
                        }
                    ]
                },
            }
        )
        identity = ModelIdentity(
            requested_model=request.settings.model,
            model_sha256=("b" if self.change and len(self.requests) > 1 else "a") * 64,
            parameters_sha256="b" * 64,
            quantization="fixture",
            family="fixture",
            model_size_bytes=1,
            provider_version="fixture",
            compiler_version="fixture",
            compiler_source_sha256="d" * 64,
            prompt_sha256=request.prompt_sha256,
            observed_at="fixture-timestamp",
            python_version="fixture",
            platform_system="fixture",
        )
        return WorkerResult(
            status="completed",
            settings=request.settings,
            identity=identity,
            understanding=spec,
            observation=ProviderObservation(
                returned_model=request.settings.model, response_sha256="e" * 64
            ),
        )


def plan(**settings):
    return make_plan(
        FrozenCorpus(CORPUS),
        SessionSettings(model="fixture:4b", **settings),
        PROMPT_SHA,
        ["dev-rules-a", "dev-rules-b"],
    )


def test_sequential_session_records_every_job_and_no_semantic_success(tmp_path):
    executor = FakeExecutor()
    report = run_session(plan(repeats=2), tmp_path / "new", executor)
    assert len(executor.requests) == report.attempts_used == 4
    assert report.run_status == "completed" and report.evaluation_status == "fail"
    assert report.model_qualification == "not-established"
    assert all(
        "review_guidance" not in request.model_dump_json()
        and "required_rules" not in request.model_dump_json()
        for request in executor.requests
    )
    assert validate_session(FrozenCorpus(CORPUS), tmp_path / "new/session.json") == report


def test_attempt_budget_preserves_unexecuted_cases(tmp_path):
    executor = FakeExecutor()
    report = run_session(plan(max_attempts=1), tmp_path / "new", executor)
    assert report.run_status == "limited" and report.stop_reason == "attempt-limit"
    assert [job.state for job in report.jobs] == ["completed", "not-run"]
    assert len(executor.requests) == report.attempts_used == 1


def test_time_budget_admission_stops_before_any_call(tmp_path, monkeypatch):
    ticks = iter([0.0, 2.0, 3.0, 4.0])
    monkeypatch.setattr("ai_harness_compiler.model_sessions.monotonic", lambda: next(ticks))
    executor = FakeExecutor()
    report = run_session(plan(session_seconds=1), tmp_path / "new", executor)
    assert report.stop_reason == "time-limit" and report.attempts_used == 0
    assert all(job.state == "not-run" for job in report.jobs)


@pytest.mark.parametrize("error", ["worker-timeout", "model-changed"])
def test_stopping_error_prevents_another_call(tmp_path, error):
    executor = FakeExecutor(error=error)
    report = run_session(plan(), tmp_path / "new", executor)
    assert report.run_status == "stopped" and report.stop_reason == error
    assert [job.state for job in report.jobs] == ["error", "not-run"]
    assert len(executor.requests) == 1


def test_model_drift_between_jobs_is_not_mixed_into_result(tmp_path):
    report = run_session(plan(), tmp_path / "new", FakeExecutor(change=True))
    assert report.jobs[1].state == "error"
    assert report.stop_reason == "model-changed"


@pytest.mark.parametrize(
    "kind", ["attempts", "status", "skip", "eval", "qualification", "time", "reason"]
)
def test_contradictory_session_reports_are_rejected(tmp_path, kind):
    data = run_session(plan(), tmp_path / "new", FakeExecutor()).model_dump()
    if kind == "attempts":
        data["attempts_used"] = 0
    elif kind == "status":
        data["run_status"] = "limited"
    elif kind == "skip":
        data["jobs"].pop()
    elif kind == "eval":
        data["evaluation_status"] = "not-run"
    elif kind == "qualification":
        data["model_qualification"] = "qualified"
    elif kind == "time":
        data["elapsed_seconds"] = 0.0
    else:
        data["stop_reason"] = "worker-timeout"
        data["run_status"] = "stopped"
    with pytest.raises(ValidationError):
        ModelSessionReport.model_validate(data)


def test_existing_output_refused_without_generation(tmp_path):
    executor = FakeExecutor()
    with pytest.raises(FileExistsError):
        run_session(plan(), tmp_path, executor)
    assert not executor.requests


@pytest.mark.parametrize("artifact", ["plan.json", "job-001.json"])
def test_changed_journal_is_rejected(tmp_path, artifact):
    output = tmp_path / "new"
    run_session(plan(), output, FakeExecutor())
    data = json.loads((output / artifact).read_text(encoding="utf-8"))
    if artifact == "plan.json":
        data["settings"]["model"] = "different:4b"
    else:
        data["elapsed_seconds"] = 999.0
    (output / artifact).write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError):
        validate_session(FrozenCorpus(CORPUS), output / "session.json")


def test_session_reader_limits_bytes(tmp_path, monkeypatch):
    monkeypatch.setattr("ai_harness_compiler.model_sessions.MAX_SESSION_BYTES", 3)
    path = tmp_path / "large"
    path.write_bytes(b"1234")
    with pytest.raises(ValueError, match="SESSION_SIZE"):
        session_bytes(path)


def test_holdout_generation_refuses_unapproved_rubric():
    with pytest.raises(ValueError, match="Holdout"):
        make_plan(
            FrozenCorpus(CORPUS),
            SessionSettings(model="fixture:4b"),
            PROMPT_SHA,
            ["held-rules-a"],
            "holdout",
            "a" * 64,
        )


def test_supervisor_kills_timed_out_worker(monkeypatch):
    class Process:
        returncode = None
        killed = False
        stdout = None

        def communicate(self, *args, **kwargs):
            if not self.killed:
                raise subprocess.TimeoutExpired("worker", 0.1)
            return b"", None

        def kill(self):
            self.killed = True

    process = Process()
    monkeypatch.setattr(
        "ai_harness_compiler.model_sessions.subprocess.Popen", lambda *a, **k: process
    )
    from ai_harness_compiler.understanding import prepare_understanding

    planned = plan()
    result = IsolatedOllamaExecutor().execute(
        WorkerRequest(
            settings=planned.settings,
            request=prepare_understanding(planned.cases[0].project),
            prompt_sha256=PROMPT_SHA,
        ),
        0.1,
    )
    assert result.error_code == "worker-timeout" and process.killed


def test_cli_existing_directory_refused(tmp_path):
    assert (
        main(
            [
                "run-understanding-evals",
                "--corpus",
                str(CORPUS),
                "--model",
                "fixture",
                "--output",
                str(tmp_path),
            ]
        )
        == 1
    )
    assert not (tmp_path / "plan.json").exists()


@pytest.mark.parametrize(
    "settings",
    [
        {"max_attempts": 31},
        {"max_attempts": True},
        {"repeats": 4},
        {"session_seconds": 0},
        {"call_timeout_seconds": 301},
        {"context_tokens": 0},
        {"max_output_tokens": 0},
    ],
)
def test_invalid_session_budgets_rejected(settings):
    with pytest.raises(ValueError):
        SessionSettings(model="fixture", **settings)


def test_real_supervisor_process_is_terminated_without_network(monkeypatch):
    from ai_harness_compiler.understanding import prepare_understanding

    actual_popen = subprocess.Popen
    processes = []

    def sleeper(*args, **kwargs):
        process = actual_popen([sys.executable, "-c", "import time; time.sleep(10)"], **kwargs)
        processes.append(process)
        return process

    monkeypatch.setattr("ai_harness_compiler.model_sessions.subprocess.Popen", sleeper)
    planned = plan()
    result = IsolatedOllamaExecutor().execute(
        WorkerRequest(
            settings=planned.settings,
            request=prepare_understanding(planned.cases[0].project),
            prompt_sha256=PROMPT_SHA,
        ),
        0.1,
    )
    assert result.error_code == "worker-timeout"
    assert processes[0].poll() is not None


def test_invalid_worker_input_is_sanitized_in_real_process():
    result = subprocess.run(
        [sys.executable, "-m", "ai_harness_compiler.model_worker"],
        input=b"PRIVATE malformed JSON",
        capture_output=True,
        timeout=5,
        check=False,
    )
    value = WorkerResult.model_validate_json(result.stdout)
    assert value.status == "error"
    assert b"PRIVATE" not in result.stdout and not result.stderr


def test_inflight_allowance_is_capped_by_remaining_session_time(tmp_path, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr("ai_harness_compiler.model_sessions.monotonic", lambda: clock[0])

    class AdvancingExecutor(FakeExecutor):
        def execute(self, request, timeout):
            assert timeout == 1.0
            value = super().execute(request, timeout)
            clock[0] = 2.0
            return value

    report = run_session(plan(session_seconds=1), tmp_path / "new", AdvancingExecutor())
    assert report.stop_reason == "time-limit"
    assert report.attempts_used == 1 and report.jobs[1].state == "not-run"


@pytest.mark.parametrize("change", [None, "cloud", "model", "digest", "metrics"])
def test_worker_metadata_and_proposal_use_mock_transport(monkeypatch, change):
    from ai_harness_compiler.understanding import prepare_understanding

    planned = plan()
    request = WorkerRequest(
        settings=planned.settings,
        request=prepare_understanding(planned.cases[0].project),
        prompt_sha256=PROMPT_SHA,
    )
    real_client = httpx.Client
    fake = FakeExecutor().execute(request, 1)
    tag_calls = 0

    def respond(wire):
        nonlocal tag_calls
        assert str(wire.url).startswith("http://127.0.0.1:11434/api/")
        if wire.url.path == "/api/tags":
            tag_calls += 1
            digest = ("b" if change == "digest" and tag_calls > 1 else "a") * 64
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": request.settings.model,
                            "digest": digest,
                            "size": 1,
                            "details": {
                                "format": "gguf",
                                "family": "fixture",
                                "quantization_level": "fixture",
                            },
                        }
                    ]
                },
            )
        if wire.url.path == "/api/show":
            value = {"parameters": "temperature 0", "system": "PRIVATE SYSTEM NOT PERSISTED"}
            if change == "cloud":
                value["remote_host"] = "https://remote.example"
            return httpx.Response(200, json=value)
        if wire.url.path == "/api/version":
            return httpx.Response(200, json={"version": "fixture"})
        payload = json.loads(wire.content)
        assert payload["options"]["num_ctx"] == 8192
        return httpx.Response(
            200,
            json={
                "done": True,
                "model": "wrong-model" if change == "model" else request.settings.model,
                "total_duration": 10,
                "load_duration": 11 if change == "metrics" else 1,
                "message": {
                    "content": fake.understanding.proposal.model_dump_json(),
                    "thinking": "PRIVATE REASONING NOT PERSISTED",
                },
            },
        )

    def mock_client(**kwargs):
        kwargs["transport"] = httpx.MockTransport(respond)
        return real_client(**kwargs)

    monkeypatch.setattr(httpx, "Client", mock_client)
    result = execute_worker(request)
    assert result.status == ("completed" if change is None else "error")
    assert "PRIVATE" not in result.model_dump_json()
