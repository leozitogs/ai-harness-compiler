"""Operational preference changes routing, not semantic approval or offline builds."""

import json

import pytest
from pydantic import ValidationError

from ai_harness_compiler.adapters.codex_cli import CodexCompactModel
from ai_harness_compiler.adapters.ollama import OllamaUnderstandingModel
from ai_harness_compiler.cli import main
from ai_harness_compiler.model_policy import load_model_policy
from ai_harness_compiler.models.compact_analysis import CompactProposal, compact_input
from ai_harness_compiler.models.model_policy import ModelPolicy


def fake_compact(self, extraction):
    return CompactProposal.model_validate(
        {
            "criteria": [
                {
                    "kind": "business-rule",
                    "condition": "Fixture condition",
                    "outcome": "Fixture outcome",
                    "note": "Unverified fixture hypothesis",
                }
                for _ in compact_input(extraction).criteria
            ]
        }
    )


def test_all_roles_inherit_one_preferred_model_without_qualification():
    policy = load_model_policy()
    for role in (
        "understanding",
        "analyst",
        "architect",
        "engineer",
        "quality",
        "security",
        "delivery",
    ):
        endpoint = policy.for_role(role)
        assert endpoint.provider == "codex-cli" and endpoint.model == "gpt-6.1-sol"
        endpoint.model = "independent-copy"
    assert policy.primary.model == "gpt-6.1-sol"
    assert (
        policy.fallback_policy == "explicit-only"
        and policy.model_qualification == "not-established"
    )
    with pytest.raises(ValueError):
        policy.for_role("unknown")


def test_study_uses_primary_when_model_not_given(tmp_path, monkeypatch, capsys):
    seen = []

    def propose(self, extraction):
        seen.append(self.settings.model)
        return fake_compact(self, extraction)

    monkeypatch.setattr(CodexCompactModel, "generate_compact", propose)
    monkeypatch.setattr(
        OllamaUnderstandingModel, "propose", lambda *_: pytest.fail("No local call")
    )
    target = tmp_path / "understanding.json"
    assert main(["study", "examples/project-definition", "--output", str(target)]) == 0
    assert seen == ["gpt-6.1-sol"]
    data = json.loads(target.read_text(encoding="utf-8"))
    assert data["review"] is None
    assert all(r["origin"] == "hypothesis" for r in data["proposal"]["business_rules"])
    assert "codex-cli" in capsys.readouterr().out


def test_primary_failure_has_no_silent_local_fallback(tmp_path, monkeypatch):
    def fail(*args):
        raise ValueError("CODEX_PROVIDER_ERROR")

    monkeypatch.setattr(CodexCompactModel, "generate_compact", fail)
    monkeypatch.setattr(OllamaUnderstandingModel, "propose", lambda *_: pytest.fail("No fallback"))
    target = tmp_path / "understanding.json"
    assert main(["study", "examples/project-definition", "--output", str(target)]) == 1
    assert not target.exists()


def test_explicit_local_uses_registered_alternative(tmp_path, monkeypatch):
    from test_ollama_understanding import proposal_for

    from ai_harness_compiler.models.understanding import UnderstandingProposal

    seen = []

    def propose(self, request):
        seen.append(self.settings.model)
        return UnderstandingProposal.model_validate(proposal_for(request.original_input))

    monkeypatch.setattr(OllamaUnderstandingModel, "propose", propose)
    monkeypatch.setattr(
        CodexCompactModel, "generate_compact", lambda *_: pytest.fail("No cloud call")
    )
    assert (
        main(
            [
                "study",
                "examples/project-definition",
                "--provider",
                "ollama",
                "--output",
                str(tmp_path / "local.json"),
            ]
        )
        == 0
    )
    assert seen == [load_model_policy().local_alternative.model]


def test_empty_override_rejected_without_using_primary(tmp_path, monkeypatch):
    monkeypatch.setattr(
        CodexCompactModel, "generate_compact", lambda *_: pytest.fail("No cloud call")
    )
    monkeypatch.setattr(
        OllamaUnderstandingModel, "propose", lambda *_: pytest.fail("No local call")
    )
    assert (
        main(
            [
                "study",
                "examples/project-definition",
                "--model",
                "",
                "--output",
                str(tmp_path / "empty.json"),
            ]
        )
        == 1
    )


def test_cli_rejects_unenforceable_cloud_token_limit_before_model_call(tmp_path, monkeypatch):
    monkeypatch.setattr(CodexCompactModel, "generate_compact", lambda *_: pytest.fail("No call"))
    assert (
        main(
            [
                "study",
                "examples/project-definition",
                "--max-output-tokens",
                "100",
                "--output",
                str(tmp_path / "new.json"),
            ]
        )
        == 1
    )


@pytest.mark.parametrize("tamper", ["qualification", "fallback", "local-provider", "unknown-field"])
def test_policy_cannot_claim_qualification_or_silent_fallback(tamper):
    data = load_model_policy().model_dump()
    if tamper == "qualification":
        data["model_qualification"] = "qualified"
    elif tamper == "fallback":
        data["fallback_policy"] = "automatic"
    elif tamper == "local-provider":
        data["local_alternative"]["provider"] = "codex-cli"
    else:
        data["arbitrary"] = "extra"
    with pytest.raises(ValidationError):
        ModelPolicy.model_validate(data)


def test_policy_limit_and_inspection_are_offline(tmp_path, capsys):
    assert main(["model-policy"]) == 0
    assert json.loads(capsys.readouterr().out)["primary"]["model"] == "gpt-6.1-sol"
    target = tmp_path / "policy.json"
    target.write_bytes(b"x" * 65537)
    with pytest.raises(ValueError, match="LIMIT"):
        load_model_policy(target)
