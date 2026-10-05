"""Observable task plans, separate from model-private reasoning and runtime execution."""

from graphlib import CycleError, TopologicalSorter
from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.capability import CapabilityGraph

Stage = Literal["design", "implement", "verify", "review"]
STAGES: tuple[Stage, ...] = ("design", "implement", "verify", "review")


class Task(Contract):
    id: Identifier
    capability_id: Identifier
    stage: Stage
    objective: Text
    depends_on: list[Identifier]
    required_context: list[Text] = Field(min_length=1)
    deliverables: list[Text] = Field(min_length=1)
    acceptance_criteria: list[Text] = Field(min_length=1)
    completion_rule: Text
    status: Literal["planned"] = "planned"


class TaskGraph(Contract):
    schema_version: Literal["TaskGraph/v1"] = "TaskGraph/v1"
    source_graph: CapabilityGraph
    selected_capabilities: list[Identifier] = Field(min_length=1)
    declared_completed_capabilities: list[Identifier] = Field(default_factory=list)
    tasks: list[Task] = Field(min_length=1)
    execution_status: Literal["not-run"] = "not-run"

    @model_validator(mode="after")
    def validate_plan(self) -> Self:
        nodes = {node.id: node for node in self.source_graph.capabilities}
        selected = set(self.selected_capabilities)
        completed = set(self.declared_completed_capabilities)
        if len(selected) != len(self.selected_capabilities):
            raise ValueError("Selected capabilities must be unique")
        if len(completed) != len(self.declared_completed_capabilities):
            raise ValueError("Completed capabilities must be unique")
        if selected & completed or (selected | completed) - nodes.keys():
            raise ValueError("Selected/completed capabilities must exist and must not overlap")
        by_id = {task.id: task for task in self.tasks}
        by_stage = {(task.capability_id, task.stage): task for task in self.tasks}
        expected = {(capability, stage) for capability in selected for stage in STAGES}
        if len(by_id) != len(self.tasks) or len(by_stage) != len(self.tasks):
            raise ValueError("Task IDs and capability-stage pairs must be unique")
        if set(by_stage) != expected:
            raise ValueError(
                "Each selected capability requires design, implement, verify and review"
            )
        for task in self.tasks:
            node = nodes[task.capability_id]
            if task.acceptance_criteria != node.acceptance_criteria:
                raise ValueError("Tasks must preserve source acceptance criteria")
            if len(task.depends_on) != len(set(task.depends_on)):
                raise ValueError("Task dependencies must be unique")
            if set(task.depends_on) - by_id.keys():
                raise ValueError("Task dependencies must resolve")
            index = STAGES.index(task.stage)
            if index:
                previous = by_stage[(task.capability_id, STAGES[index - 1])].id
                if previous not in task.depends_on:
                    raise ValueError(
                        "Task stages must preserve design → implement → verify → review"
                    )
            else:
                missing = set(node.depends_on) - selected - completed
                if missing:
                    raise ValueError(f"Unplanned prerequisites for {node.id}: {sorted(missing)}")
                required = {
                    by_stage[(dependency, "review")].id
                    for dependency in node.depends_on
                    if dependency in selected
                }
                if not required.issubset(task.depends_on):
                    raise ValueError("Design must wait for prerequisite capability reviews")
        try:
            self.ready_batches()
        except CycleError as exc:
            raise ValueError("Task graph must be acyclic") from exc
        return self

    def ready_batches(self) -> list[list[str]]:
        """Potential scheduling waves, assuming every preceding wave succeeds."""
        sorter = TopologicalSorter({task.id: task.depends_on for task in self.tasks})
        sorter.prepare()
        batches: list[list[str]] = []
        while sorter.is_active():
            ready = sorted(sorter.get_ready())
            batches.append(ready)
            sorter.done(*ready)
        return batches
