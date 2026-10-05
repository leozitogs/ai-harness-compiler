"""Deterministic work decomposition with source criteria and prerequisite gates."""

from ai_harness_compiler.models.capability import CapabilityGraph
from ai_harness_compiler.models.task import Stage, Task, TaskGraph


def decompose(
    graph: CapabilityGraph,
    selected: list[str] | None = None,
    completed: list[str] | None = None,
) -> TaskGraph:
    graph = CapabilityGraph.model_validate(graph.model_dump())
    selected = list(selected) if selected is not None else graph.execution_order()
    completed = list(completed or [])
    ids = {node.id: index + 1 for index, node in enumerate(graph.capabilities)}
    stages: list[Stage] = ["design", "implement", "verify", "review"]
    tasks = []
    for index, node in enumerate(graph.capabilities):
        if node.id not in selected:
            continue
        objectives = {
            "design": f"Define contracts, boundaries and test cases for: {node.title}",
            "implement": f"Implement the agreed scope for: {node.title}",
            "verify": f"Collect acceptance and regression evidence for: {node.title}",
            "review": f"Review evidence, documentation and integration for: {node.title}",
        }
        deliverables = {
            "design": ["Contract/architecture proposal", "Acceptance test plan"],
            "implement": ["Implementation changes", "Automated tests"],
            "verify": ["Test results linked to each acceptance criterion", "Regression results"],
            "review": ["Reviewed pull request", "Updated documentation and completion evidence"],
        }
        for stage_index, stage in enumerate(stages):
            dependencies = (
                [
                    f"task-{ids[dependency]}-review"
                    for dependency in node.depends_on
                    if dependency in selected
                ]
                if stage == "design"
                else [f"task-{index + 1}-{stages[stage_index - 1]}"]
            )
            tasks.append(
                Task(
                    id=f"task-{index + 1}-{stage}",
                    capability_id=node.id,
                    stage=stage,
                    objective=objectives[stage],
                    depends_on=dependencies,
                    required_context=[
                        f"project.yaml#/backlog/{index}",
                        "project.yaml#/constraints",
                        "project.yaml#/branding",
                    ],
                    deliverables=deliverables[stage],
                    acceptance_criteria=node.acceptance_criteria,
                    completion_rule=(
                        "Human-reviewed evidence must satisfy this stage's deliverables and "
                        "source criteria. A generated plan is not completion evidence."
                    ),
                )
            )
    return TaskGraph(
        source_graph=graph,
        selected_capabilities=selected,
        declared_completed_capabilities=completed,
        tasks=tasks,
    )
