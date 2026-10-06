import json
import socket
from pathlib import Path
from statistics import median

import pytest
from jsonschema import Draft202012Validator

from ai_harness_compiler.benchmark import run_benchmark
from ai_harness_compiler.cli import main
from ai_harness_compiler.models.benchmark import BenchmarkReport

ROOT = Path(__file__).resolve().parents[1]
SUITE = ROOT / "benchmarks/suite.json"


def test_benchmark_measures_real_bundles_offline(tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Benchmark must not use network")

    monkeypatch.setattr(socket, "socket", no_network)
    workspace = tmp_path / "session"
    report = run_benchmark(SUITE, workspace, runs=2)
    assert len(report.cases) == 3
    assert report.product_evaluation_status == "not-run" and report.slo_status == "not-defined"
    assert report.python_version and report.compiler_version
    assert len(report.compiler_source_sha256) == 64
    for case in report.cases:
        assert len(case.samples) == 2
        assert case.median_ms == median(item.duration_ms for item in case.samples)
        assert len({item.bundle_sha256 for item in case.samples}) == 1
        for index, sample in enumerate(case.samples, start=1):
            output = workspace / case.fixture_id / f"run-{index}"
            files = [path for path in output.rglob("*") if path.is_file()]
            assert sample.file_count == len(files)
            assert sample.artifact_bytes == sum(path.stat().st_size for path in files)
    Draft202012Validator(BenchmarkReport.model_json_schema()).validate(report.model_dump())
    assert BenchmarkReport.model_validate_json(report.model_dump_json()) == report


def test_benchmark_cli_protects_existing_report_and_session(tmp_path, capsys):
    report = tmp_path / "report.json"
    session = tmp_path / "session"
    args = [
        "benchmark",
        str(SUITE),
        "--workspace",
        str(session),
        "--output",
        str(report),
        "--runs",
        "2",
    ]
    assert main(args) == 0
    assert "SLO not-defined" in capsys.readouterr().out
    before = report.read_bytes()
    assert main(args) == 1
    assert "BENCHMARK_EXISTS" in capsys.readouterr().err
    assert report.read_bytes() == before
    assert (
        main(
            [
                "benchmark",
                str(SUITE),
                "--workspace",
                str(session),
                "--output",
                str(tmp_path / "second.json"),
            ]
        )
        == 1
    )
    assert not (tmp_path / "second.json").exists()


@pytest.mark.parametrize("runs", [0, -1, 1, True])
def test_invalid_runs_cannot_claim_reproducibility(runs, tmp_path):
    output = tmp_path / "session"
    with pytest.raises(ValueError, match="BENCHMARK_RUNS"):
        run_benchmark(SUITE, output, runs=runs)
    assert not output.exists()


def test_fixture_paths_cannot_escape_suite(tmp_path):
    suite = tmp_path / "suite.json"
    payload = json.loads(SUITE.read_text(encoding="utf-8"))
    payload["fixtures"][0]["manifest"] = "../outside.yaml"
    suite.write_text(json.dumps(payload), encoding="utf-8")
    with pytest.raises(ValueError, match="BENCHMARK_PATH"):
        run_benchmark(suite, tmp_path / "session")
    assert not (tmp_path / "session").exists()


def test_criteria_drift_cannot_produce_a_success_report(tmp_path, capsys):
    source = ROOT / "benchmarks/fixtures/education/project.yaml"
    (tmp_path / "project.yaml").write_bytes(source.read_bytes())
    payload = json.loads(SUITE.read_text(encoding="utf-8"))
    payload["fixtures"] = [payload["fixtures"][0]]
    payload["fixtures"][0].update(manifest="project.yaml", acceptance_criteria_count=999)
    suite = tmp_path / "suite.json"
    suite.write_text(json.dumps(payload), encoding="utf-8")
    report = tmp_path / "report.json"
    assert (
        main(
            [
                "benchmark",
                str(suite),
                "--workspace",
                str(tmp_path / "session"),
                "--output",
                str(report),
            ]
        )
        == 1
    )
    assert "BENCHMARK_CRITERIA" in capsys.readouterr().err
    assert not report.exists()
