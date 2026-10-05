"""LangGraph coordination, persistent checkpoints and explicit PO review."""

import json
import operator
from pathlib import Path
from typing import Annotated, Any, TypedDict, cast
from uuid import uuid4

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Command, Send, interrupt
from langsmith import tracing_context

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.team import POReview, Role, TeamConfig
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.team.agents import BoundedAgent, LocalPolicy, OllamaPolicy
from ai_harness_compiler.team.context import RepositoryContext
from ai_harness_compiler.team.ml import IntentRouter
from ai_harness_compiler.team.personas import PERSONAS
from ai_harness_compiler.team.tools import TeamTools


class TeamState(TypedDict, total=False):
    agent_id: Role
    selected_roles: list[Role]
    route: dict[str, object]
    reports: Annotated[list[dict[str, Any]], operator.add]
    source_digests: dict[str, str]
    status: str
    approval: dict[str, Any]


def build_graph(
    config: TeamConfig,
    tools: TeamTools,
    router: IntentRouter,
    saver: SqliteSaver,
) -> CompiledStateGraph[TeamState, None, TeamState, TeamState]:
    def dispatch(state: TeamState) -> dict[str, object]:
        route = router.route(config.request)
        roles = list(PERSONAS) if config.mode == "prepare" else [cast(Role, route["selected_role"])]
        return {"selected_roles": roles, "route": route, "status": "running"}

    def route_agents(state: TeamState) -> list[Send]:
        return [Send("specialist", {"agent_id": role}) for role in state["selected_roles"]]

    def specialist(state: TeamState) -> dict[str, object]:
        policy = OllamaPolicy(config.model or "") if config.engine == "ollama" else LocalPolicy()
        agent = BoundedAgent(PERSONAS[state["agent_id"]], tools, policy, config.max_steps)
        report = agent.run(config.request, config.engine)
        return {"reports": [report.model_dump()]}

    def consolidate(state: TeamState) -> dict[str, str]:
        failed = any(report["status"] == "failed" for report in state["reports"])
        return {"status": "failed" if failed else "awaiting_po"}

    def review(state: TeamState) -> dict[str, object]:
        answer = interrupt(
            {
                "kind": "product-owner-review",
                "request": config.request,
                "agent_count": len(state["reports"]),
                "instruction": (
                    "Review the proposal. Approval accepts this report; "
                    "sprint start and repository changes require separate decisions."
                ),
            }
        )
        decision = POReview.model_validate(answer)
        return {
            "status": "approved" if decision.decision == "approve" else "rejected",
            "approval": decision.model_dump(),
        }

    builder = StateGraph(TeamState)
    builder.add_node("dispatch", dispatch)
    builder.add_node("specialist", specialist)
    builder.add_node("consolidate", consolidate)
    builder.add_node("po_review", review)
    builder.add_edge(START, "dispatch")
    builder.add_conditional_edges("dispatch", route_agents, ["specialist"])
    builder.add_edge("specialist", "consolidate")
    builder.add_conditional_edges(
        "consolidate",
        lambda state: "failed" if state["status"] == "failed" else "review",
        {"failed": END, "review": "po_review"},
    )
    builder.add_edge("po_review", END)
    return builder.compile(checkpointer=saver)


def write_report(output: Path, state: TeamState, router: IntentRouter) -> None:
    report = {
        "status": state["status"],
        "reports": sorted(state["reports"], key=lambda item: item["agent_id"]),
        "routing": state["route"],
        "source_digests": state["source_digests"],
        "approval": state.get("approval"),
        "ml_evaluation": router.evaluate(),
        "sprint_started": False,
        "repository_modified_by_agents": False,
    }
    (output / "team-report.json").write_text(json_text(report), encoding="utf-8", newline="\n")


def prepare_team(config: TeamConfig, output: Path) -> dict[str, object]:
    config = TeamConfig.model_validate(config.model_dump())
    context = RepositoryContext(Path(config.repository_root))
    tools = TeamTools(plan(config.project), list(config.selected), context)
    router = IntentRouter()
    output.mkdir(parents=True, exist_ok=False)
    run_id = f"run-{uuid4().hex}"
    (output / "run.json").write_text(
        json_text({"run_id": run_id, "config": config.model_dump()}),
        encoding="utf-8",
        newline="\n",
    )
    (output / "tasks.json").write_text(
        json_text(tools.tasks.model_dump()), encoding="utf-8", newline="\n"
    )
    with SqliteSaver.from_conn_string(str(output / "checkpoints.sqlite")) as saver:
        graph = build_graph(config, tools, router, saver)
        invocation: RunnableConfig = {"configurable": {"thread_id": run_id}, "recursion_limit": 20}
        with tracing_context(enabled=False):
            initial: TeamState = {"reports": [], "source_digests": context.digests()}
            graph.invoke(initial, invocation)
            state = cast(TeamState, graph.get_state(invocation).values)
        write_report(output, state, router)
    return {
        "status": state["status"],
        "agents_executed": len(state["reports"]),
        "output": str(output),
    }


def review_team(output: Path, decision: POReview) -> dict[str, object]:
    decision = POReview.model_validate(decision.model_dump())
    metadata = json.loads((output / "run.json").read_text(encoding="utf-8"))
    config = TeamConfig.model_validate(metadata["config"])
    if not (output / "checkpoints.sqlite").is_file():
        raise ValueError("Run checkpoint does not exist")
    context = RepositoryContext(Path(config.repository_root))
    tools = TeamTools(plan(config.project), list(config.selected), context)
    router = IntentRouter()
    with SqliteSaver.from_conn_string(str(output / "checkpoints.sqlite")) as saver:
        graph = build_graph(config, tools, router, saver)
        invocation: RunnableConfig = {
            "configurable": {"thread_id": metadata["run_id"]},
            "recursion_limit": 20,
        }
        with tracing_context(enabled=False):
            state = cast(TeamState, graph.get_state(invocation).values)
            if state.get("status") != "awaiting_po":
                raise ValueError("Only a pending, successful team proposal can be reviewed")
            if state["source_digests"] != context.digests():
                raise ValueError(
                    "Repository context changed; prepare a new proposal before acceptance"
                )
            graph.invoke(Command(resume=decision.model_dump()), invocation)
            state = cast(TeamState, graph.get_state(invocation).values)
        write_report(output, state, router)
    return {"status": state["status"], "sprint_started": False, "output": str(output)}
