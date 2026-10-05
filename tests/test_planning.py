import pytest
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.task import TaskGraph
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.planning import decompose


def test_dependency_review_gates_next_capability(project):
    tasks = decompose(plan(project).capability_graph)
    assert len(tasks.tasks) == 8
    assert tasks.tasks[4].depends_on == ["task-1-review"]
    assert tasks.ready_batches() == [[task.id] for task in tasks.tasks]
    assert all(task.status == "planned" for task in tasks.tasks)
    assert tasks.execution_status == "not-run"
    assert TaskGraph.model_validate_json(tasks.model_dump_json()) == tasks


def test_independent_capabilities_have_parallel_waves(project):
    project.backlog[1].depends_on = []
    graph = decompose(plan(project).capability_graph)
    assert graph.ready_batches()[0] == ["task-1-design", "task-2-design"]
    assert len(graph.ready_batches()) == 4


def test_selected_scope_requires_prerequisites(project):
    source = plan(project).capability_graph
    with pytest.raises(ValidationError, match="Unplanned prerequisites"):
        decompose(source, ["lesson-draft"])
    graph = decompose(source, ["lesson-draft"], ["material-library"])
    assert len(graph.tasks) == 4
    assert graph.declared_completed_capabilities == ["material-library"]
    assert graph.tasks[0].id == "task-2-design"


@pytest.mark.parametrize(
    "kind", ["cycle", "missing-stage", "skipped-gate", "criteria", "duplicate"]
)
def test_invalid_task_plans_are_rejected(project, kind):
    payload = decompose(plan(project).capability_graph).model_dump()
    if kind == "cycle":
        payload["tasks"][0]["depends_on"] = [payload["tasks"][-1]["id"]]
    elif kind == "missing-stage":
        payload["tasks"].pop()
    elif kind == "skipped-gate":
        payload["tasks"][4]["depends_on"] = []
    elif kind == "criteria":
        payload["tasks"][2]["acceptance_criteria"] = ["Invented criterion"]
    else:
        payload["tasks"].append(payload["tasks"][0])
    with pytest.raises(ValidationError):
        TaskGraph.model_validate(payload)


@pytest.mark.parametrize("selection", [["unknown"], ["material-library", "material-library"]])
def test_invalid_selection_is_rejected(project, selection):
    with pytest.raises(ValidationError):
        decompose(plan(project).capability_graph, selection)


def test_task_cli_works_for_this_repository(capsys):
    assert main(["tasks", "project-definition", "--select", "ahc-001", "ahc-002"]) == 0
    assert '"TaskGraph/v1"' in capsys.readouterr().out
