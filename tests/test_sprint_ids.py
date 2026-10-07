"""Sprint identifiers cannot escape planning paths; focus plans preserve dependencies."""

import subprocess
import sys
from pathlib import Path

import pytest

from ai_harness_compiler.models.task import TaskGraph

ROOT = Path(__file__).resolve().parents[1]


def test_sprint_25_generation_and_dependency_gates():
    result = subprocess.run(
        [sys.executable, "scripts/generate_sprint_plan.py", "--sprint", "sprint-2-5", "--check"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    graph = TaskGraph.model_validate_json(
        (ROOT / "planning/sprint-2-5.tasks.json").read_text(encoding="utf-8")
    )
    assert graph.selected_capabilities == ["ahc-021", "ahc-022", "ahc-023"]
    assert graph.ready_batches()[0] == ["task-21-design"]
    assert graph.tasks[4].depends_on == ["task-21-review"]
    assert graph.tasks[8].depends_on == ["task-22-review"]
    assert graph.execution_status == "not-run"


@pytest.mark.parametrize(
    "identifier",
    [
        "../sprint-2",
        "sprint-2/../sprint-1",
        "sprint-0",
        "sprint-02-5",
        "sprint-2-0",
        "sprint-2.5",
        "sprint-2-5-1",
    ],
)
def test_invalid_sprint_identifier_fails_before_read(identifier):
    result = subprocess.run(
        [sys.executable, "scripts/generate_sprint_plan.py", "--sprint", identifier],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert "Sprint ID must match" in result.stderr
    assert "Traceback" not in result.stderr
