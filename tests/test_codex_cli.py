"""Subscription adapter tests use fake streams/processes; never authenticate or call a model."""

import io
import json
import subprocess

import pytest

from ai_harness_compiler.adapters import codex_cli
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import compact_input


def events(answer):
    return b"\n".join(
        json.dumps(e).encode()
        for e in [
            {"type": "thread.started", "thread_id": "fake"},
            {"type": "turn.started"},
            {"type": "item.completed", "item": {"type": "reasoning", "text": "PRIVATE"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": answer}},
            {"type": "turn.completed", "usage": {"output_tokens": 42}},
        ]
    )


def test_events_discard_private_content_and_require_completion():
    answer, complete = codex_cli.consume_events(io.BytesIO(events('{"result":true}')))
    assert answer == '{"result":true}' and complete
    assert "PRIVATE" not in answer
    with pytest.raises(ValueError, match="INCOMPLETE"):
        codex_cli.consume_events(io.BytesIO(b'{"type":"turn.started"}\n'))


def test_completion_order_is_mandatory():
    premature = b'{"type":"turn.completed"}\n'
    with pytest.raises(ValueError, match="EVENT_INVALID"):
        codex_cli.consume_events(io.BytesIO(premature))
    with pytest.raises(ValueError, match="AFTER_COMPLETION"):
        codex_cli.consume_events(io.BytesIO(events("{}") + b'\n{"type":"turn.started"}\n'))


@pytest.mark.parametrize(
    "item_type", ["command_execution", "mcp_tool_call", "web_search", "file_change"]
)
def test_unexpected_tool_events_rejected(item_type):
    stream = json.dumps({"type": "item.started", "item": {"type": item_type}}).encode()
    with pytest.raises(ValueError, match="UNEXPECTED_TOOL"):
        codex_cli.consume_events(io.BytesIO(stream))


def test_stream_bound_and_duplicate_final_message_rejected(monkeypatch):
    monkeypatch.setattr(codex_cli, "MAX_STREAM_BYTES", 10)
    with pytest.raises(ValueError, match="OUTPUT_LIMIT"):
        codex_cli.consume_events(io.BytesIO(b"x" * 11))
    monkeypatch.setattr(codex_cli, "MAX_STREAM_BYTES", 4096)
    final = b'{"type":"item.completed","item":{"type":"agent_message","text":"{}"}}\n'
    with pytest.raises(ValueError, match="EVENT_INVALID"):
        codex_cli.consume_events(io.BytesIO(final + final))


def test_subscription_boundary_uses_isolated_readonly_invocation(monkeypatch, project):
    extraction = extract_grounding(project)
    proposal = {
        "schema_version": "CompactUnderstandingProposal/v1",
        "criteria": [
            {
                "kind": "requirement",
                "condition": None,
                "outcome": None,
                "question": None,
                "note": "Test fixture",
                "uncertainties": [],
            }
            for _ in compact_input(extraction).criteria
        ],
        "context_findings": [],
        "issues": [],
    }
    capture = {}

    class Process:
        stdin = io.BytesIO()
        stdout = io.BytesIO(events(json.dumps(proposal)))
        returncode = 0

        def __init__(self, command, **kwargs):
            capture.update(command=command, **kwargs)

        def wait(self, timeout):
            return 0

        def poll(self):
            return 0

        def kill(self):
            pass

    monkeypatch.setenv("CODEX_API_KEY", "SECRET")
    monkeypatch.setenv("OPENAI_API_KEY", "SECRET")
    monkeypatch.setattr(codex_cli.shutil, "which", lambda _: "/trusted/codex")
    monkeypatch.setattr(
        codex_cli.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(
            a[0], 0, stdout=b"", stderr=b"Logged in using ChatGPT\n"
        ),
    )
    monkeypatch.setattr(codex_cli.subprocess, "Popen", Process)
    result = codex_cli.CodexCompactModel(
        codex_cli.CodexCLISettings("explicit-model")
    ).generate_compact(extraction)
    assert result.criteria[0].kind == "requirement"
    command = capture["command"]
    assert command[:2] == ["/trusted/codex", "exec"]
    assert "read-only" in command and "--ephemeral" in command
    assert "--ignore-user-config" in command and 'forced_login_method="chatgpt"' in command
    assert "features.shell_tool=false" in command and 'web_search="disabled"' in command
    assert "--dangerously-bypass-approvals-and-sandbox" not in command
    assert capture["cwd"] != str(project)
    assert "CODEX_API_KEY" not in capture["env"] and "OPENAI_API_KEY" not in capture["env"]
    assert capture["stderr"] == subprocess.DEVNULL


@pytest.mark.parametrize("status", [b"Not logged in", b"Logged in using an API key"])
def test_other_auth_methods_fail_before_forced_login_or_generation(monkeypatch, project, status):
    calls = []
    monkeypatch.setattr(codex_cli.shutil, "which", lambda _: "/trusted/codex")
    monkeypatch.setattr(
        codex_cli.subprocess,
        "run",
        lambda *a, **kw: subprocess.CompletedProcess(a[0], 0, stdout=status, stderr=b""),
    )
    monkeypatch.setattr(codex_cli.subprocess, "Popen", lambda *a, **kw: calls.append(a))
    model = codex_cli.CodexCompactModel(codex_cli.CodexCLISettings("explicit-model"))
    with pytest.raises(ValueError, match="CHATGPT_LOGIN_REQUIRED"):
        model.generate_compact(extract_grounding(project))
    assert calls == []


def test_strict_output_schema_requires_defaulted_fields_without_mutating_original():
    original = {"type": "object", "properties": {"x": {"type": "string", "default": "a"}}}
    normalized = codex_cli.strict_schema(original)
    assert normalized["required"] == ["x"] and normalized["additionalProperties"] is False
    assert "default" not in normalized["properties"]["x"]
    assert original["properties"]["x"]["default"] == "a"


@pytest.mark.parametrize("model,timeout", [("x;rm", 180), ("x", 0), ("x", True), ("x", 301)])
def test_invalid_settings_rejected(model, timeout):
    with pytest.raises(ValueError):
        codex_cli.CodexCLISettings(model, timeout)
