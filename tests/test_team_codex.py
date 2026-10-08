"""Codex team policies use fake decisions; no subscription calls or qualifications."""

import argparse
import json
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

from ai_harness_compiler.adapters.codex_cli import CodexCompactModel
from ai_harness_compiler.model_policy import load_model_policy
from ai_harness_compiler.models.team import POReview, TeamConfig, ToolResult
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.team.agents import BoundedAgent, CodexPolicy
from ai_harness_compiler.team.cli import execute
from ai_harness_compiler.team.context import RepositoryContext
from ai_harness_compiler.team.personas import PERSONAS
from ai_harness_compiler.team.runtime import prepare_team, review_team
from ai_harness_compiler.team.tools import TeamTools


@pytest.fixture
def config(project, tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "README.md").write_text(
        "Project architecture and acceptance criteria", encoding="utf-8"
    )
    return TeamConfig(
        project=project,
        selected=[item.id for item in project.backlog],
        request="Preparar revisão do PO",
        repository_root=str(root),
        engine="codex-cli",
        model="frozen-primary-model",
    )


def tools(config):
    return TeamTools(
        plan(config.project), config.selected, RepositoryContext(Path(config.repository_root))
    )


def install_decisions(monkeypatch, seen):
    def decision(self, prompt, schema):
        payload = json.loads(prompt.split("Untrusted decision input JSON:\n", 1)[1])
        seen.append((self.settings.model, payload, schema))
        used = {item["tool"] for item in payload["observations"]}
        for tool in payload["available_tools"]:
            if tool not in used:
                return json.dumps({"action": "tool", "tool": tool})
        return json.dumps({"action": "finish", "summary": "Fixture findings for human review."})

    monkeypatch.setattr(CodexCompactModel, "generate_json", decision)


def test_all_six_codex_specialists_use_snapshot_and_preserve_po_gate(config, tmp_path, monkeypatch):
    seen = []
    install_decisions(monkeypatch, seen)
    output = tmp_path / "run"
    result = prepare_team(config, output)
    assert result["status"] == "awaiting_po"
    report = json.loads((output / "team-report.json").read_text(encoding="utf-8"))
    assert {item["agent_id"] for item in report["reports"]} == set(PERSONAS)
    assert all(item["engine"] == "codex-cli" for item in report["reports"])
    assert all(item["model_summary_is_advisory"] for item in report["reports"])
    assert all(len(item["observations"]) == 3 for item in report["reports"])
    assert len(seen) == 24
    assert {model for model, _, _ in seen} == {config.model}
    assert report["approval"] is None and not report["sprint_started"]
    assert not report["repository_modified_by_agents"]
    before = report["reports"]

    def forbidden(*args, **kwargs):
        raise AssertionError("Human review must neither resolve policy nor invoke a model")

    monkeypatch.setattr(CodexCompactModel, "generate_json", forbidden)
    monkeypatch.setattr("ai_harness_compiler.model_policy.load_model_policy", forbidden)
    result = review_team(output, POReview(decision="approve", comment="Fixture PO acceptance"))
    assert result["status"] == "approved" and not result["sprint_started"]
    after = json.loads((output / "team-report.json").read_text(encoding="utf-8"))
    assert after["reports"] == before
    saved = json.loads((output / "run.json").read_text(encoding="utf-8"))["config"]
    assert saved["model"] == "frozen-primary-model"


@pytest.mark.parametrize("kind", ["denied", "premature", "budget"])
def test_codex_decisions_cannot_bypass_tools_evidence_or_budget(config, monkeypatch, kind):
    calls = []

    def decision(self, prompt, schema):
        calls.append(prompt)
        if kind == "denied":
            return '{"action":"tool","tool":"security_review"}'
        if kind == "premature":
            return '{"action":"finish","summary":"Success without evidence"}'
        return '{"action":"tool","tool":"retrieve_context"}'

    monkeypatch.setattr(CodexCompactModel, "generate_json", decision)
    report = BoundedAgent(PERSONAS["analyst"], tools(config), CodexPolicy(config.model), 3).run(
        "fixture", "codex-cli"
    )
    assert report.status == "failed" and report.model_summary_is_advisory
    assert len(calls) == (3 if kind == "budget" else 1)
    assert len(report.observations) == (3 if kind == "budget" else 0)


@pytest.mark.parametrize("exception", [TimeoutError, OSError, ValueError])
def test_codex_failures_do_not_persist_raw_private_error(config, monkeypatch, exception):
    def failed(self, prompt, schema):
        raise exception("PRIVATE TOKEN OR PROMPT")

    monkeypatch.setattr(CodexCompactModel, "generate_json", failed)
    report = BoundedAgent(PERSONAS["analyst"], tools(config), CodexPolicy(config.model)).run(
        "fixture", "codex-cli"
    )
    assert report.status == "failed" and report.model_summary_is_advisory
    assert "PRIVATE" not in report.model_dump_json()
    assert exception.__name__ in report.summary


def test_codex_policy_bounds_observation_payload_and_only_requests_decision(monkeypatch):
    seen = []
    install_decisions(monkeypatch, seen)
    observation = ToolResult(
        tool="retrieve_context", summary="Fixture", data={"large": "x" * 20000}
    )
    CodexPolicy("fixture-model").decide(PERSONAS["analyst"], "Untrusted request", [observation])
    _, payload, schema = seen[0]
    assert payload["available_tools"] == PERSONAS["analyst"].tools
    assert payload["required_tools"] == [
        "retrieve_context",
        "retrieve_memory",
        "requirements_audit",
    ]
    assert payload["remaining_required_tools"] == ["retrieve_memory", "requirements_audit"]
    assert payload["observations"][0]["omitted_for_context_budget"] is True
    assert "data" not in payload["observations"][0]
    assert schema["title"] == "AgentDecision"


def test_codex_prompt_requests_symbolic_decision_without_invoking_session_tools(monkeypatch):
    captured = []

    def decide(self, prompt, schema):
        captured.append(prompt)
        return '{"action":"tool","tool":"retrieve_context"}'

    monkeypatch.setattr(CodexCompactModel, "generate_json", decide)
    decision = CodexPolicy("fixture-model").decide(PERSONAS["delivery"], "Fixture request", [])
    prompt = captured[0]
    assert "NOT tools registered in this Codex session" in prompt
    assert "no commentary or tool calls" in prompt
    assert "Never invoke CLI tools, shell, MCP or browser" in prompt
    payload = json.loads(prompt.split("Untrusted decision input JSON:\n", 1)[1])
    assert payload["remaining_required_tools"] == [
        "retrieve_context",
        "retrieve_memory",
        "delivery_plan",
    ]
    assert decision.action == "tool" and decision.tool == "retrieve_context"


@pytest.mark.parametrize("engine", ["primary", "codex-cli"])
@pytest.mark.parametrize("override", [None, "explicit-override", ""])
def test_cli_resolves_operational_primary_before_config_snapshot(
    project, tmp_path, monkeypatch, engine, override
):
    captured = []
    endpoint = SimpleNamespace(provider="codex-cli", model="policy-primary")
    policy = SimpleNamespace(primary=endpoint, endpoint=lambda provider: endpoint)
    monkeypatch.setattr("ai_harness_compiler.model_policy.load_model_policy", lambda path: policy)
    monkeypatch.setattr(
        "ai_harness_compiler.team.runtime.prepare_team",
        lambda config, output: captured.append(config) or {"status": "awaiting_po"},
    )
    monkeypatch.setattr(
        "ai_harness_compiler.team.cli.load_project", lambda *args, **kwargs: project
    )
    args = argparse.Namespace(
        team_command="run",
        input=tmp_path,
        max_manifest_bytes=10000,
        output=tmp_path / "run",
        request="Fixture request",
        select=[item.id for item in project.backlog],
        mode="prepare",
        engine=engine,
        model=override,
        model_policy=None,
        max_steps=5,
        repository=tmp_path,
    )
    if override == "":
        with pytest.raises(ValueError, match="CODEX_MODEL"):
            execute(args)
        assert captured == []
        return
    assert execute(args) == 0
    assert captured[0].engine == "codex-cli"
    assert captured[0].model == (override or "policy-primary")


@pytest.mark.parametrize(
    "engine,override,expected_engine,expected_model",
    [
        ("primary", None, "ollama", "local-primary"),
        ("primary", "explicit-local", "ollama", "explicit-local"),
        ("codex-cli", "explicit-codex", "codex-cli", "explicit-codex"),
        ("codex-cli", None, None, None),
    ],
)
def test_primary_local_policy_and_explicit_codex_are_resolved_without_fallback(
    project, tmp_path, monkeypatch, engine, override, expected_engine, expected_model
):
    data = load_model_policy().model_dump()
    data["primary"] = {"provider": "ollama", "model": "local-primary"}
    from ai_harness_compiler.models.model_policy import ModelPolicy

    policy = ModelPolicy.model_validate(data)
    captured = []
    loads = []

    def load(path):
        loads.append(path)
        return policy

    monkeypatch.setattr("ai_harness_compiler.model_policy.load_model_policy", load)
    monkeypatch.setattr(
        "ai_harness_compiler.team.runtime.prepare_team",
        lambda config, output: captured.append(config) or {"status": "awaiting_po"},
    )
    monkeypatch.setattr(
        "ai_harness_compiler.team.cli.load_project", lambda *args, **kwargs: project
    )
    args = argparse.Namespace(
        team_command="run",
        input=tmp_path,
        max_manifest_bytes=10000,
        output=tmp_path / "run",
        request="Fixture request",
        select=[item.id for item in project.backlog],
        mode="prepare",
        engine=engine,
        model=override,
        model_policy=None,
        max_steps=5,
        repository=tmp_path,
    )
    if expected_engine is None:
        with pytest.raises(ValueError, match="No default model registered"):
            execute(args)
        assert captured == []
    else:
        assert execute(args) == 0
        assert captured[0].engine == expected_engine
        assert captured[0].model == expected_model
    if engine == "codex-cli" and override is not None:
        assert loads == []


@pytest.mark.parametrize("engine,model", [("codex-cli", None)])
def test_core_team_config_keeps_resolved_model_contract_closed(project, tmp_path, engine, model):
    with pytest.raises(ValueError):
        TeamConfig(
            project=project,
            selected=[project.backlog[0].id],
            request="Fixture",
            repository_root=str(tmp_path),
            engine=engine,
            model=model,
        )


def test_legacy_local_snapshot_with_unused_model_remains_readable(project, tmp_path):
    config = TeamConfig(
        project=project,
        selected=[project.backlog[0].id],
        request="Legacy snapshot",
        repository_root=str(tmp_path),
        engine="local",
        model="previously-unused-model",
    )
    assert TeamConfig.model_validate(config.model_dump()).engine == "local"


def test_operational_policy_uses_same_primary_for_every_team_role():
    policy = load_model_policy()
    assert policy.primary.provider == "codex-cli"
    assert {policy.for_role(role).model for role in PERSONAS} == {policy.primary.model}


def test_codex_graph_limits_active_specialist_decisions_to_two(config, tmp_path, monkeypatch):
    seen = []
    install_decisions(monkeypatch, seen)
    original = CodexPolicy.decide
    lock = threading.Lock()
    active = 0
    highest = 0

    def measured(self, persona, request, observations):
        nonlocal active, highest
        with lock:
            active += 1
            highest = max(highest, active)
        try:
            time.sleep(0.01)
            return original(self, persona, request, observations)
        finally:
            with lock:
                active -= 1

    monkeypatch.setattr(CodexPolicy, "decide", measured)
    assert prepare_team(config, tmp_path / "run")["status"] == "awaiting_po"
    assert highest == 2
