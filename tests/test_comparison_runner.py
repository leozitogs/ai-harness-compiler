"""Mocked providers validate development journals without model or network calls."""

import json
from pathlib import Path

import pytest
from test_understanding_comparison import proposal

from ai_harness_compiler.adapters.codex_cli import CodexCompactModel
from ai_harness_compiler.comparison_runner import (
    ComparisonPlan,
    _bind_worker,
    run_development_comparison,
    validate_development_comparison,
)
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.model_sessions import IsolatedOllamaExecutor
from ai_harness_compiler.models.model_session import (
    ModelIdentity,
    ProviderObservation,
    WorkerResult,
)
from ai_harness_compiler.semantic_eval import FrozenCorpus

CORPUS = Path(__file__).resolve().parents[1] / "evals/understanding/v1"


def worker_result(request):
    spec = proposal(extract_grounding(request.request.original_input))
    return WorkerResult(
        status="completed",
        settings=request.settings,
        identity=ModelIdentity(
            requested_model=request.settings.model,
            model_sha256="a" * 64,
            parameters_sha256="b" * 64,
            quantization="fixture",
            family="fixture",
            model_size_bytes=1,
            provider_version="fixture",
            compiler_version="fixture",
            compiler_source_sha256="c" * 64,
            python_version="fixture",
            platform_system="fixture",
            observed_at="fixture",
            prompt_sha256=request.prompt_sha256,
        ),
        understanding=spec.understanding,
        compact_analysis=spec,
        observation=ProviderObservation(
            returned_model=request.settings.model, response_sha256="d" * 64
        ),
    )


@pytest.fixture
def mocked_providers(monkeypatch):
    calls = []

    def local(self, request, timeout):
        calls.append(("local", timeout))
        return worker_result(request)

    def cloud(self, extraction):
        calls.append(("cloud", self.settings.timeout_seconds))
        return proposal(extraction).interpretation

    monkeypatch.setattr(IsolatedOllamaExecutor, "execute", local)
    monkeypatch.setattr(CodexCompactModel, "generate_compact", cloud)
    return calls


def run(output):
    return run_development_comparison(
        FrozenCorpus(CORPUS), "dev-rules-a", "fixture-local", "fixture-cloud", "a" * 64, output, 7
    )


def test_journal_records_bound_calls_and_validates_without_provider_calls(
    mocked_providers, tmp_path, monkeypatch
):
    output = tmp_path / "comparison"
    report = run(output)
    assert sorted(mocked_providers) == [("cloud", 7), ("local", 7.0)]
    assert {p.name for p in output.iterdir()} == {
        "plan.json",
        "local-worker.json",
        "comparison.json",
    }

    def forbidden(*args):
        raise AssertionError("Validator cannot execute a provider")

    monkeypatch.setattr(CodexCompactModel, "generate_compact", forbidden)
    monkeypatch.setattr(IsolatedOllamaExecutor, "execute", forbidden)
    assert validate_development_comparison(FrozenCorpus(CORPUS), output) == report
    assert report.semantic_status == "not-established"


def test_existing_directory_and_holdout_are_rejected_before_calls(mocked_providers, tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    with pytest.raises(FileExistsError):
        run(existing)
    with pytest.raises(ValueError):
        run_development_comparison(
            FrozenCorpus(CORPUS), "hold-rules-a", "fixture", "fixture", "a" * 64, tmp_path / "new"
        )
    assert mocked_providers == []


@pytest.mark.parametrize("error", ["worker-timeout", "worker-result-error"])
def test_failed_local_worker_is_persisted_and_other_branch_survives(
    mocked_providers, tmp_path, monkeypatch, error
):
    monkeypatch.setattr(
        IsolatedOllamaExecutor,
        "execute",
        lambda *args: WorkerResult(status="error", error_code=error),
    )
    output = tmp_path / "comparison"
    report = run(output)
    assert report.candidates[0].status == ("timeout" if error == "worker-timeout" else "error")
    assert report.candidates[1].status == "completed"
    assert validate_development_comparison(FrozenCorpus(CORPUS), output) == report


def test_worker_model_drift_is_sanitized_before_journaling(mocked_providers, tmp_path, monkeypatch):
    def drift(self, request, timeout):
        result = worker_result(request)
        result.identity.model_sha256 = "0" * 64
        return result

    monkeypatch.setattr(IsolatedOllamaExecutor, "execute", drift)
    output = tmp_path / "comparison"
    report = run(output)
    assert report.candidates[0].status == "error"
    worker = json.loads((output / "local-worker.json").read_text())
    assert worker["error_code"] == "worker-result-error"
    validate_development_comparison(FrozenCorpus(CORPUS), output)


@pytest.mark.parametrize(
    "tamper", ["case", "corpus", "local-program", "cloud-program", "model", "proposal", "extra"]
)
def test_journal_contradictions_are_rejected(mocked_providers, tmp_path, tamper):
    output = tmp_path / "comparison"
    run(output)
    if tamper == "extra":
        (output / "unknown.json").write_text("{}")
    elif tamper in {"case", "corpus"}:
        path = output / "plan.json"
        data = json.loads(path.read_text())
        if tamper == "corpus":
            data["corpus_sha256"] = "0" * 64
        else:
            data["case"]["id"] = "dev-rules-b"
        path.write_text(json.dumps(data))
    else:
        path = output / "comparison.json"
        data = json.loads(path.read_text())
        if tamper == "local-program":
            data["candidates"][0]["program_sha256"] = "0" * 64
        elif tamper == "cloud-program":
            data["candidates"][1]["program_sha256"] = "0" * 64
        elif tamper == "model":
            data["candidates"][1]["requested_model"] = "another-model"
        else:
            data["candidates"][0]["compact_analysis"]["interpretation"]["criteria"][0]["note"] = (
                "Modified but still structurally valid"
            )
        path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        validate_development_comparison(FrozenCorpus(CORPUS), output)


def test_historical_program_digest_is_not_recomputed(mocked_providers, tmp_path, monkeypatch):
    output = tmp_path / "comparison"
    report = run(output)
    monkeypatch.setattr("ai_harness_compiler.adapters.codex_cli.program_digest", lambda: "0" * 64)
    assert validate_development_comparison(FrozenCorpus(CORPUS), output) == report


def test_incompatible_completed_worker_is_a_validation_error(mocked_providers, tmp_path):
    output = tmp_path / "comparison"
    run(output)
    plan = ComparisonPlan.model_validate_json((output / "plan.json").read_bytes())
    result = worker_result(plan.local_request)
    data = result.model_dump()
    data["settings"]["analysis_mode"] = "baseline"
    data["compact_analysis"] = None
    baseline = WorkerResult.model_validate(data)
    with pytest.raises(ValueError, match="compact analysis"):
        _bind_worker(plan, baseline)


def test_cli_missing_team_extra_is_actionable(monkeypatch, tmp_path, capsys):
    from ai_harness_compiler.cli import main

    def unavailable(*args, **kwargs):
        raise ModuleNotFoundError("Missing optional package", name="langgraph")

    monkeypatch.setattr(
        "ai_harness_compiler.comparison_runner.run_development_comparison", unavailable
    )
    code = main(
        [
            "compare-understanding",
            "--corpus",
            str(CORPUS),
            "--case",
            "dev-rules-a",
            "--ollama-model",
            "fixture",
            "--codex-model",
            "fixture",
            "--expected-model-sha256",
            "a" * 64,
            "--output",
            str(tmp_path / "new"),
        ]
    )
    assert code == 1
    assert "uv sync --extra team" in capsys.readouterr().err
