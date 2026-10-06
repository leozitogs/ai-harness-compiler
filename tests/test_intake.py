"""Intake boundaries reject ambiguous/unbounded input before planning or writing."""

import socket
import sys
from io import BytesIO
from pathlib import Path

import pytest

from ai_harness_compiler.cli import main
from ai_harness_compiler.intake import IntakeError, load_project

VALID = """id: example
name: Educação
conception: Ferramenta local
backlog:
  - id: first
    title: Entrega
    description: Critério observável
    acceptance_criteria: [Funciona]
assets:
  - path: assets/not-read.md
    description: Referência apenas
"""


def write_manifest(tmp_path: Path, content: str | bytes) -> Path:
    path = tmp_path / "project.yaml"
    path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
    return path


@pytest.mark.parametrize(
    ("content", "code"),
    [
        (VALID + "name: hidden\n", "INTAKE_DUPLICATE_KEY"),
        (
            VALID.replace("title: Entrega", "title: Entrega\n    title: secret"),
            "INTAKE_DUPLICATE_KEY",
        ),
        (VALID + "branding: {tone: &tone [formal], audience: *tone}\n", "INTAKE_YAML_ALIAS"),
        (VALID + "branding: {<<: {tone: [formal]}}\n", "INTAKE_YAML_MERGE"),
        (VALID + "branding: {true: [formal]}\n", "INTAKE_YAML_KEY"),
        (VALID + "branding: {[a, b]: [formal]}\n", "INTAKE_YAML_KEY"),
        (VALID + "schema_version: ProjectInput/v999\n", "INTAKE_SCHEMA_VERSION"),
        (VALID + "schema_version: null\n", "INTAKE_SCHEMA_VERSION"),
        ("[]", "INTAKE_SHAPE"),
        ("", "INTAKE_SHAPE"),
        (VALID + "---\nid: second\n", "INTAKE_YAML"),
        ("invalid: [", "INTAKE_YAML"),
        ("!!python/object/apply:os.system [echo unexpected]", "INTAKE_YAML"),
        (b"\xff", "INTAKE_ENCODING"),
        (b"id: ex\x00ample", "INTAKE_YAML"),
        (VALID + "extra: unknown\n", "INTAKE_CONTRACT"),
        ("nested: " + "[" * 65 + "0" + "]" * 65, "INTAKE_YAML_DEPTH"),
        ("many: [" + ",".join(["0"] * 50_001) + "]", "INTAKE_YAML_NODES"),
    ],
    ids=[f"case-{index}" for index in range(18)],
)
def test_rejected_inputs_have_stable_codes(content, code, tmp_path, capsys):
    source = write_manifest(tmp_path, content)
    with pytest.raises(IntakeError) as error:
        load_project(source)
    assert error.value.code == code
    output = tmp_path / "generated"
    assert main(["build", str(source), "--output", str(output)]) == 1
    diagnostic = capsys.readouterr().err
    assert diagnostic.startswith(f"factory: {code}: ")
    assert "secret" not in diagnostic and "Traceback" not in diagnostic
    assert not output.exists()


def test_utf8_bom_and_metadata_only_assets(tmp_path, monkeypatch):
    source = write_manifest(tmp_path, b"\xef\xbb\xbf" + VALID.encode("utf-8"))
    original_open = Path.open
    opened = []

    def manifest_only(path, *args, **kwargs):
        opened.append(path)
        assert path == source
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", manifest_only)

    def no_network(*args, **kwargs):
        raise AssertionError("Intake must not open network connections")

    monkeypatch.setattr(socket, "socket", no_network)
    project = load_project(tmp_path)
    assert project.name == "Educação"
    assert project.assets[0].path == "assets/not-read.md"
    assert opened == [source]


def test_manifest_limit_counts_bytes_and_is_configurable(tmp_path, capsys):
    source = write_manifest(tmp_path, VALID)
    size = len(VALID.encode("utf-8"))
    assert load_project(source, max_manifest_bytes=size).id == "example"
    with pytest.raises(IntakeError, match="INTAKE_TOO_LARGE"):
        load_project(source, max_manifest_bytes=size - 1)
    assert main(["validate", str(source), "--max-manifest-bytes", str(size)]) == 0
    capsys.readouterr()
    assert main(["validate", str(source), "--max-manifest-bytes", str(size - 1)]) == 1
    assert "INTAKE_TOO_LARGE" in capsys.readouterr().err


@pytest.mark.parametrize("limit", [0, -1, True, 1.5, sys.maxsize])
def test_invalid_limit_fails_before_reading(limit, tmp_path):
    with pytest.raises(IntakeError, match="INTAKE_LIMIT"):
        load_project(tmp_path / "missing", max_manifest_bytes=limit)


def test_missing_manifest_has_stable_read_error(tmp_path):
    with pytest.raises(IntakeError, match="INTAKE_READ"):
        load_project(tmp_path / "missing")


def test_default_limit_rejects_large_manifest(tmp_path):
    source = write_manifest(tmp_path, VALID + "#" + "x" * (1024 * 1024))
    with pytest.raises(IntakeError, match="INTAKE_TOO_LARGE"):
        load_project(source)


def test_read_is_bounded_before_decoding(tmp_path, monkeypatch):
    requests = []

    class TrackedStream(BytesIO):
        def read(self, size=-1):
            requests.append(size)
            return super().read(size)

    def bounded_open(*args, **kwargs):
        return TrackedStream(b"x" * 1024)

    monkeypatch.setattr(Path, "open", bounded_open)
    with pytest.raises(IntakeError, match="INTAKE_TOO_LARGE"):
        load_project(tmp_path / "project.yaml", max_manifest_bytes=16)
    assert requests == [17]


def test_yaml_scalar_conversion_error_is_normalized(tmp_path):
    source = write_manifest(tmp_path, VALID.replace("Ferramenta local", "2026-99-01"))
    with pytest.raises(IntakeError, match="INTAKE_YAML"):
        load_project(source)
