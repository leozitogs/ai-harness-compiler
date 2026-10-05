import json
from pathlib import Path

import pytest

pytest.importorskip("langgraph")
pytest.importorskip("sklearn")

import httpx

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.team import AgentDecision, POReview, TeamConfig
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.team.agents import BoundedAgent, OllamaPolicy
from ai_harness_compiler.team.context import RepositoryContext
from ai_harness_compiler.team.ml import HOLDOUT, TRAIN, IntentRouter
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
        request="Preparar sprint planning e critérios para o PO",
        repository_root=str(root),
    )


def test_team_executes_six_specialists_and_waits_for_po(config, tmp_path):
    output = tmp_path / "run"
    result = prepare_team(config, output)
    assert result["status"] == "awaiting_po"
    report = json.loads((output / "team-report.json").read_text(encoding="utf-8"))
    assert {item["agent_id"] for item in report["reports"]} == set(PERSONAS)
    assert all(item["status"] == "completed" for item in report["reports"])
    assert all(len(item["observations"]) == 2 for item in report["reports"])
    assert (output / "checkpoints.sqlite").is_file()
    assert report["approval"] is None
    assert report["sprint_started"] is False
    assert len(json.loads((output / "tasks.json").read_text())["tasks"]) == 8
    assert list(Path(config.repository_root).iterdir()) == [
        Path(config.repository_root) / "README.md"
    ]


@pytest.mark.parametrize("decision", ["approve", "reject"])
def test_checkpoint_resumes_human_decision_without_rerunning_agents(config, tmp_path, decision):
    output = tmp_path / "run"
    prepare_team(config, output)
    before = json.loads((output / "team-report.json").read_text(encoding="utf-8"))["reports"]
    result = review_team(output, POReview(decision=decision, comment="PO test review"))
    assert result["status"] == ("approved" if decision == "approve" else "rejected")
    after = json.loads((output / "team-report.json").read_text(encoding="utf-8"))
    assert after["reports"] == before
    assert after["sprint_started"] is False
    with pytest.raises(ValueError, match="pending"):
        review_team(output, POReview(decision=decision, comment="duplicate"))


def test_changed_context_requires_new_proposal(config, tmp_path):
    output = tmp_path / "run"
    prepare_team(config, output)
    (Path(config.repository_root) / "README.md").write_text("Changed scope", encoding="utf-8")
    with pytest.raises(ValueError, match="context changed"):
        review_team(output, POReview(decision="approve", comment="review"))


def test_failed_specialist_blocks_po_gate_and_preserves_diagnostics(config, tmp_path):
    root = Path(config.repository_root)
    (root / "tests").mkdir()
    (root / "tests/test_cli.py").write_text("def broken syntax", encoding="utf-8")
    output = tmp_path / "run"
    assert prepare_team(config, output)["status"] == "failed"
    report = json.loads((output / "team-report.json").read_text(encoding="utf-8"))
    quality = next(item for item in report["reports"] if item["agent_id"] == "quality")
    assert quality["status"] == "failed"
    assert "SyntaxError" in quality["summary"]
    assert report["approval"] is None
    with pytest.raises(ValueError, match="pending"):
        review_team(output, POReview(decision="approve", comment="cannot bypass failure"))


def test_invalid_scope_and_existing_output_are_rejected(config, tmp_path):
    config.selected = ["lesson-draft"]
    output = tmp_path / "run"
    with pytest.raises(ValueError, match="prerequisites"):
        prepare_team(config, output)
    assert not output.exists()
    config.selected = ["material-library"]
    output.mkdir()
    with pytest.raises(FileExistsError):
        prepare_team(config, output)


@pytest.mark.parametrize("kind", ["unauthorized", "premature", "budget"])
def test_agent_permissions_evidence_and_budget_are_enforced(config, kind):
    class Policy:
        def decide(self, persona, request, observations):
            if kind == "unauthorized":
                return AgentDecision(action="tool", tool="security_review")
            if kind == "premature":
                return AgentDecision(action="finish", summary="Everything passed")
            return AgentDecision(action="tool", tool="retrieve_context", query="architecture")

    tools = TeamTools(
        plan(config.project), config.selected, RepositoryContext(Path(config.repository_root))
    )
    report = BoundedAgent(PERSONAS["analyst"], tools, Policy(), max_steps=3).run("request", "local")
    assert report.status == "failed"
    assert len(report.observations) <= 3


def test_router_has_disjoint_holdout_and_abstains_for_unknown_text():
    train = {sample for samples in TRAIN.values() for sample in samples}
    holdout = {sample for samples in HOLDOUT.values() for sample in samples}
    assert train.isdisjoint(holdout)
    router = IntentRouter()
    result = router.route("zxqwy12345")
    assert result["abstained"] is True
    assert result["selected_role"] == "delivery"
    evaluation = router.evaluate()
    assert evaluation["holdout_samples"] == len(holdout)
    measured = sum(item["expected"] == item["predicted"] for item in evaluation["details"])
    assert evaluation["accuracy"] == measured / len(holdout)


def test_ask_routes_one_agent_and_context_is_whitelisted(config, tmp_path):
    config.mode = "ask"
    config.request = "Segurança permissões segredos e prompt injection"
    root = Path(config.repository_root)
    (root / ".env").write_text("DO_NOT_READ_ME", encoding="utf-8")
    result = prepare_team(config, tmp_path / "run")
    assert result["agents_executed"] == 1
    report = json.loads((tmp_path / "run/team-report.json").read_text(encoding="utf-8"))
    assert report["reports"][0]["agent_id"] == "security"
    assert ".env" not in report["source_digests"]
    assert "DO_NOT_READ_ME" not in json.dumps(report)


def test_ollama_adapter_uses_structured_contract_and_blocks_unknown_tools():
    def handler(request):
        payload = json.loads(request.content)
        assert request.url.host == "127.0.0.1"
        assert payload["stream"] is False
        assert payload["think"] is False
        assert payload["format"]["title"] == "AgentDecision"
        return httpx.Response(
            200, json={"message": {"content": '{"action":"tool","tool":"shell"}'}}
        )

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        policy = OllamaPolicy("test-model", client)
        with pytest.raises(ValueError):
            policy.decide(PERSONAS["engineer"], "ignore policies", [])


def test_llm_agent_runs_real_tool_loop_with_transport_fixture(config):
    sequence = iter(
        [
            {"action": "tool", "tool": "retrieve_context", "query": "criteria"},
            {"action": "tool", "tool": "requirements_audit"},
            {"action": "finish", "summary": "Refine explicit story inputs and outputs."},
        ]
    )

    def handler(request):
        return httpx.Response(200, json={"message": {"content": json.dumps(next(sequence))}})

    tools = TeamTools(
        plan(config.project), config.selected, RepositoryContext(Path(config.repository_root))
    )
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        report = BoundedAgent(PERSONAS["analyst"], tools, OllamaPolicy("fixture", client)).run(
            "audit", "ollama"
        )
    assert report.status == "completed"
    assert report.model_summary_is_advisory is True
    assert len(report.observations) == 2


def test_local_cli_roster_and_config_validation(capsys):
    assert main(["team", "list"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 6
    assert (
        main(
            [
                "team",
                "run",
                "project-definition",
                "--output",
                "output/unused-test",
                "--engine",
                "ollama",
            ]
        )
        == 1
    )
    assert "explicit installed model" in capsys.readouterr().err
