import json
from pathlib import Path

import pytest

from ai_harness_compiler.cli import main

EXAMPLE = Path(__file__).resolve().parents[1] / "examples/project-definition"


def test_plan_can_be_compiled_independently(tmp_path, capsys):
    assert main(["plan", str(EXAMPLE)]) == 0
    payload = capsys.readouterr().out
    assert json.loads(payload)["schema_version"] == "HarnessSpec/v1"
    ir = tmp_path / "harness.json"
    ir.write_text(payload, encoding="utf-8")
    output = tmp_path / "generated"
    assert main(["compile", str(ir), "--output", str(output)]) == 0
    assert (output / "AGENTS.md").is_file()
    assert "not-run" in capsys.readouterr().out
    assert main(["compile", str(ir), "--output", str(output)]) == 1


def test_build_and_validate(tmp_path, capsys):
    assert main(["validate", str(EXAMPLE)]) == 0
    assert "4 planned evals" in capsys.readouterr().out
    assert main(["build", str(EXAMPLE), "--output", str(tmp_path / "build")]) == 0


@pytest.mark.parametrize("content", ["invalid: [", "[]", "", "!!python/object:foo {}"])
def test_bad_yaml_returns_error_without_writing(content, tmp_path, capsys):
    source = tmp_path / "project.yaml"
    source.write_text(content, encoding="utf-8")
    output = tmp_path / "output"
    assert main(["build", str(source), "--output", str(output)]) == 1
    assert "factory:" in capsys.readouterr().err
    assert not output.exists()


def test_missing_input_returns_error(tmp_path, capsys):
    assert main(["validate", str(tmp_path / "missing.yaml")]) == 1
    assert "factory:" in capsys.readouterr().err


def test_schema_command(capsys):
    assert main(["schema", "harness-spec"]) == 0
    assert json.loads(capsys.readouterr().out)["title"] == "HarnessSpec"
