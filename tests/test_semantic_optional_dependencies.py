"""Core-only users receive an actionable extra hint before any provider call."""

import builtins

import pytest

from ai_harness_compiler.cli import main


@pytest.mark.parametrize(
    "command",
    [
        "analyze-project-v2",
        "analyze-project-v3",
        "verify-analysis-v2",
        "verify-analysis-v3",
        "verify-analysis-v4",
    ],
)
def test_missing_optional_dependency_reports_extra(command, tmp_path, monkeypatch, capsys):
    original = builtins.__import__

    def without_provider(name, *args, **kwargs):
        if name == "ai_harness_compiler.adapters.codex_cli":
            raise ModuleNotFoundError("No module named 'httpx'", name="httpx")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", without_provider)
    output = tmp_path / "no-output.json"
    assert main([command, "not-opened.json", "--output", str(output)]) == 1
    assert "uv sync --extra understanding" in capsys.readouterr().err
    assert not output.exists()
