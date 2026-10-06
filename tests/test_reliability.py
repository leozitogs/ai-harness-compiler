"""Real fixture builds and injected failures test the compiler's I/O boundary."""

import errno
import hashlib
import json
import socket
from pathlib import Path

import pytest

from ai_harness_compiler.cli import main
from ai_harness_compiler.compiler import CompilationError, compile_harness, render, verify_bundle
from ai_harness_compiler.intake import load_project
from ai_harness_compiler.pipeline import plan

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("domain", ["education", "commerce", "dev-tools"])
def test_three_domains_preserve_criteria_and_reproduce_bytes(domain, tmp_path, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Compiler fixture must stay offline")

    monkeypatch.setattr(socket, "socket", no_network)
    project = load_project(ROOT / "benchmarks/fixtures" / domain)
    spec = plan(project)
    assert len(spec.evals) == 4
    expected = {
        (item.id, criterion) for item in project.backlog for criterion in item.acceptance_criteria
    }
    assert {(case.capability_id, case.criterion) for case in spec.evals} == expected
    assert all(case.status == "not-run" for case in spec.evals)
    first = compile_harness(spec, tmp_path / "first")
    second = compile_harness(spec, tmp_path / "second")
    assert verify_bundle(first) == verify_bundle(second)
    for name in render(spec):
        assert (first / name).read_bytes() == (second / name).read_bytes()


def test_write_failure_is_diagnostic_preserves_existing_project_and_no_final_manifest(
    project, tmp_path, monkeypatch, capsys
):
    existing = tmp_path / "existing"
    existing.mkdir()
    marker = existing / "application.py"
    marker.write_text("user-owned content", encoding="utf-8")
    before = hashlib.sha256(marker.read_bytes()).hexdigest()
    output = tmp_path / "new-output"
    original_open = Path.open
    writes = []

    def fail_during_write(path, mode="r", *args, **kwargs):
        if path.is_relative_to(output) and mode == "x":
            writes.append(path)
            if len(writes) == 3:
                raise OSError(errno.ENOSPC, "Injected disk full")
        return original_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail_during_write)
    with pytest.raises(CompilationError) as error:
        compile_harness(plan(project), output)
    assert error.value.code == "COMPILE_WRITE" and "partial" in str(error.value)
    assert not (output / ".ai/manifest.json").exists()
    assert hashlib.sha256(marker.read_bytes()).hexdigest() == before
    assert list(existing.iterdir()) == [marker]
    assert main(["build", str(ROOT / "examples/project-definition"), "--output", str(output)]) == 1
    assert "COMPILE_EXISTS" in capsys.readouterr().err


def test_reservation_failure_has_stable_diagnostic(project, tmp_path, monkeypatch):
    output = tmp_path / "denied"
    original = Path.mkdir

    def denied(path, *args, **kwargs):
        if path == output:
            raise PermissionError("Injected permission denial")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "mkdir", denied)
    with pytest.raises(CompilationError, match="COMPILE_RESERVE"):
        compile_harness(plan(project), output)
    assert not output.exists()


def test_existing_output_refused_before_any_artifact_is_opened(project, tmp_path, monkeypatch):
    output = tmp_path / "existing"
    output.mkdir()
    original = Path.open

    def no_output_open(path, *args, **kwargs):
        assert not path.is_relative_to(output)
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", no_output_open)
    with pytest.raises(FileExistsError, match="COMPILE_EXISTS"):
        compile_harness(plan(project), output)
    assert not list(output.iterdir())


def test_manifest_is_emitted_last(project, tmp_path, monkeypatch):
    output = tmp_path / "fresh"
    original = Path.open
    writes = []

    def record(path, mode="r", *args, **kwargs):
        if path.is_relative_to(output) and mode == "x":
            writes.append(path.relative_to(output).as_posix())
        return original(path, mode, *args, **kwargs)

    monkeypatch.setattr(Path, "open", record)
    compile_harness(plan(project), output)
    assert writes[-1] == ".ai/manifest.json"
    assert verify_bundle(output)


def test_in_process_integrity_rejects_tampering(project, tmp_path):
    output = compile_harness(plan(project), tmp_path / "build")
    (output / "AGENTS.md").write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="ARTIFACT_INTEGRITY"):
        verify_bundle(output)
    manifest = json.loads((output / ".ai/manifest.json").read_text(encoding="utf-8"))
    manifest["files"] = {"../escape": "0" * 64}
    (output / ".ai/manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(ValueError, match="unsafe"):
        verify_bundle(output)


def test_stream_write_error_is_caught_by_cli(project, tmp_path, monkeypatch, capsys):
    output = tmp_path / "output"
    original = Path.open

    class FailingStream:
        def __init__(self, stream):
            self.stream = stream

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.stream.close()

        def write(self, content):
            self.stream.write(content[:10])
            raise OSError(errno.ENOSPC, "Injected write failure")

    def fail(path, mode="r", *args, **kwargs):
        stream = original(path, mode, *args, **kwargs)
        return FailingStream(stream) if path.is_relative_to(output) and mode == "x" else stream

    monkeypatch.setattr(Path, "open", fail)
    assert main(["build", str(ROOT / "examples/project-definition"), "--output", str(output)]) == 1
    error = capsys.readouterr().err
    assert "COMPILE_WRITE" in error and "partial" in error and "Traceback" not in error
    assert not (output / ".ai/manifest.json").exists()
