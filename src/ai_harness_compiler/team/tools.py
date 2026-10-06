"""Concrete tools over compiler contracts and a bounded repository snapshot."""

import ast

from ai_harness_compiler.models import HarnessSpec
from ai_harness_compiler.models.team import Finding, ToolName, ToolResult
from ai_harness_compiler.planning import decompose
from ai_harness_compiler.team.context import RepositoryContext

CHANGE_MAP = {
    "ahc-001": ["src/ai_harness_compiler/intake.py", "tests/test_cli.py"],
    "ahc-002": ["src/ai_harness_compiler/models/project.py", "tests/test_pipeline.py"],
    "ahc-003": [
        "src/ai_harness_compiler/models/project.py",
        "src/ai_harness_compiler/models/harness.py",
    ],
    "ahc-004": ["src/ai_harness_compiler/compiler.py", "tests/test_compiler.py", "examples/"],
}


class TeamTools:
    def __init__(self, spec: HarnessSpec, selected: list[str], context: RepositoryContext) -> None:
        self.spec = spec
        self.context = context
        self.tasks = decompose(spec.capability_graph, selected)
        self.nodes = [node for node in spec.capability_graph.capabilities if node.id in selected]

    def call(self, name: ToolName, query: str = "") -> ToolResult:
        match name:
            case "retrieve_context":
                matches = self.context.retrieve(query)
                return ToolResult(
                    tool=name,
                    summary=f"Retrieved {len(matches)} bounded repository excerpts.",
                    data={"matches": matches, "content_trust": "untrusted-data"},
                )
            case "requirements_audit":
                findings = []
                for node in self.nodes:
                    source = f"project.yaml#backlog/{node.id}"
                    if not node.inputs or not node.outputs:
                        findings.append(
                            Finding(
                                capability_id=node.id,
                                severity="warning",
                                source=source,
                                message="Refine explicit inputs and outputs before implementation.",
                            )
                        )
                    if node.data_owner is None:
                        findings.append(
                            Finding(
                                capability_id=node.id,
                                severity="warning",
                                source=source,
                                message="Data ownership is undeclared; confirm during refinement.",
                            )
                        )
                return ToolResult(
                    tool=name,
                    summary=f"Audited {len(self.nodes)} stories and their source criteria.",
                    findings=findings,
                    data={
                        "criteria_count": sum(len(node.acceptance_criteria) for node in self.nodes),
                        "stories": [node.model_dump() for node in self.nodes],
                    },
                )
            case "architecture_review":
                return ToolResult(
                    tool=name,
                    summary="Mapped story changes to compiler boundaries and compatibility gates.",
                    data={
                        "change_map": {
                            node.id: CHANGE_MAP.get(node.id, ["docs/architecture.md"])
                            for node in self.nodes
                        },
                        "principles": [
                            "Typed contracts before rendering",
                            "I/O at adapters",
                            "Version incompatible schemas",
                        ],
                        "reference_sources": sorted(self.context.documents),
                        "recommendations_status": "proposal-requires-review",
                    },
                    findings=[
                        Finding(
                            severity="info",
                            source="docs/architecture.md",
                            message=(
                                "LangGraph coordinates this project team in an optional adapter; "
                                "the compiler core stays independent."
                            ),
                        )
                    ],
                )
            case "implementation_plan":
                return ToolResult(
                    tool=name,
                    summary=f"Built {len(self.tasks.tasks)} validated tasks with review gates.",
                    data={
                        "task_graph": self.tasks.model_dump(),
                        "waves": self.tasks.ready_batches(),
                        "execution_status": "not-run",
                    },
                )
            case "quality_review":
                inventory: dict[str, object] = {}
                for source, content in self.context.documents.items():
                    if source.startswith("tests/"):
                        tree = ast.parse(content)
                        inventory[source] = [
                            node.name
                            for node in ast.walk(tree)
                            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
                        ]
                matrix = [
                    {
                        "capability_id": node.id,
                        "criterion": criterion,
                        "suggested_method": "automated-test-or-reviewed-evidence",
                        "status": "not-run",
                    }
                    for node in self.nodes
                    for criterion in node.acceptance_criteria
                ]
                return ToolResult(
                    tool=name,
                    summary=f"Produced {len(matrix)} acceptance checks and test inventory.",
                    data={
                        "acceptance_matrix": matrix,
                        "test_inventory": inventory,
                        "tests_executed_by_this_tool": False,
                    },
                )
            case "security_review":
                findings = [
                    Finding(
                        capability_id=node.id,
                        severity="warning",
                        source=f"project.yaml#backlog/{node.id}",
                        message=f"Risk: {node.risk}; review input trust, data scope and effects.",
                    )
                    for node in self.nodes
                    if node.risk in {"unknown", "medium", "high"}
                ]
                return ToolResult(
                    tool=name,
                    summary="Reviewed declared risks and bounded team-tool permissions.",
                    findings=findings,
                    data={
                        "compiler_policy": self.spec.permissions.model_dump(),
                        "team_policy": {
                            "shell": False,
                            "repository_writes": False,
                            "publishing": False,
                            "allowed_network": "explicit-ollama-loopback-only",
                            "po_controls_acceptance": True,
                        },
                    },
                )
            case "delivery_plan":
                return ToolResult(
                    tool=name,
                    summary="Prepared a dependency-aware sprint proposal for PO review.",
                    data={
                        "selected_capabilities": [node.id for node in self.nodes],
                        "task_count": len(self.tasks.tasks),
                        "scheduling_waves": self.tasks.ready_batches(),
                        "capacity_confirmed": False,
                        "sprint_started": False,
                        "po_decisions": [
                            "Priorities",
                            "Capacity and start date",
                            "Acceptance of scope",
                        ],
                    },
                    findings=[
                        Finding(
                            severity="warning",
                            source="planning/sprint-1.json",
                            message="Capacity, owners and start date require human confirmation.",
                        )
                    ],
                )
        raise ValueError(f"Unknown tool: {name}")
