"""Opt-in subscription CLI boundary; no credentials, transcripts, retries or approvals."""

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import threading
from dataclasses import dataclass
from pathlib import Path
from time import monotonic
from typing import Any

from ai_harness_compiler.adapters.ollama import COMPACT_PROMPT, compact_response_schema
from ai_harness_compiler.models.compact_analysis import CompactProposal, compact_input
from ai_harness_compiler.models.grounding import GroundingExtraction

POLICY_VERSION = "codex-structured-cli/v5"
MAX_STREAM_BYTES = 2 * 1024 * 1024
MAX_INPUT_BYTES = 256 * 1024
OVERRIDES = (
    'forced_login_method="chatgpt"',
    'web_search="disabled"',
    "features.shell_tool=false",
    "features.unified_exec=false",
    "features.multi_agent=false",
    "features.shell_snapshot=false",
    "features.skill_mcp_dependency_install=false",
    "hide_agent_reasoning=true",
    'history.persistence="none"',
    "project_doc_max_bytes=0",
)


def strict_schema(value: Any) -> Any:
    """Require every object key, making Pydantic defaults explicit for strict outputs."""
    if isinstance(value, list):
        return [strict_schema(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: strict_schema(item) for key, item in value.items() if key != "default"}
    if result.get("type") == "object":
        result["required"] = list(result.get("properties", {}))
        result["additionalProperties"] = False
    return result


def program_digest() -> str:
    return hashlib.sha256(
        json.dumps(
            {
                "version": POLICY_VERSION,
                "prompt": COMPACT_PROMPT,
                "overrides": OVERRIDES,
                "schema": strict_schema(CompactProposal.model_json_schema()),
                "dimensions": "exact-input-criteria-count-and-context-range/v1",
                "projection": "literal-source-bindings-hypothesis-rules-criteria-context/v2",
            },
            sort_keys=True,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()


@dataclass(frozen=True)
class CodexCLISettings:
    model: str
    timeout_seconds: int = 180
    executable: str = "codex"

    def __post_init__(self) -> None:
        if not re.fullmatch(r"[A-Za-z0-9][\w.:-]{0,199}", self.model):
            raise ValueError("CODEX_MODEL: Explicit model identifier required")
        if type(self.timeout_seconds) is not int or not 1 <= self.timeout_seconds <= 300:
            raise ValueError("CODEX_LIMIT: Timeout must be 1..300 seconds")
        if not self.executable or "\x00" in self.executable:
            raise ValueError("CODEX_EXECUTABLE: Invalid executable")


def consume_events(stream: Any) -> tuple[str, bool]:
    """Discard intermediate/private events; accept only one final message and completion."""
    used = 0
    answer: str | None = None
    completed = False
    for line in stream:
        if completed:
            raise ValueError("CODEX_EVENT_AFTER_COMPLETION")
        used += len(line)
        if used > MAX_STREAM_BYTES or len(line) > MAX_STREAM_BYTES:
            raise ValueError("CODEX_OUTPUT_LIMIT")
        try:
            event = json.loads(line)
        except (ValueError, UnicodeError) as exc:
            raise ValueError("CODEX_EVENT_INVALID") from exc
        if not isinstance(event, dict):
            raise ValueError("CODEX_EVENT_INVALID")
        kind = event.get("type")
        if kind in {"error", "turn.failed"}:
            raise ValueError("CODEX_PROVIDER_ERROR")
        if kind == "turn.completed":
            if answer is None:
                raise ValueError("CODEX_EVENT_INVALID")
            completed = True
        if kind in {"item.started", "item.completed", "item.updated"}:
            item = event.get("item", {})
            if not isinstance(item, dict):
                raise ValueError("CODEX_EVENT_INVALID")
            item_type = item.get("type")
            if item_type not in {"reasoning", "agent_message"}:
                raise ValueError("CODEX_UNEXPECTED_TOOL_EVENT")
            if kind == "item.completed" and item_type == "agent_message":
                if answer is not None or not isinstance(item.get("text"), str):
                    raise ValueError("CODEX_EVENT_INVALID")
                answer = item["text"]
        elif kind not in {"thread.started", "turn.started", "turn.completed"}:
            raise ValueError("CODEX_EVENT_INVALID")
    if not completed or answer is None:
        raise ValueError("CODEX_INCOMPLETE")
    return answer, completed


class CodexCompactModel:
    def __init__(self, settings: CodexCLISettings) -> None:
        self.settings = settings

    def generate_compact(self, extraction: GroundingExtraction) -> CompactProposal:
        packet = compact_input(extraction)
        prompt = COMPACT_PROMPT + "\nUntrusted input JSON:\n" + packet.model_dump_json()
        answer = self.generate_json(
            prompt, compact_response_schema(len(packet.criteria), len(packet.context))
        )
        return CompactProposal.model_validate_json(answer)

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        """Return final structured text; callers validate their own domain contract."""
        started = monotonic()
        if len(prompt.encode()) > MAX_INPUT_BYTES:
            raise ValueError("CODEX_INPUT_LIMIT")
        executable = shutil.which(self.settings.executable)
        if executable is None:
            raise ValueError("CODEX_UNAVAILABLE")
        # Do not inherit API-key overrides, injected instructions or user configuration.
        environment = os.environ.copy()
        for name in ("OPENAI_API_KEY", "CODEX_API_KEY", "CODEX_ACCESS_TOKEN"):
            environment.pop(name, None)
        # Check harmless status before forced_login_method: a mismatching cached login
        # could otherwise be logged out by Codex. Never change the user's auth method.
        try:
            auth = subprocess.run(
                [executable, "login", "status"],
                env=environment,
                capture_output=True,
                timeout=min(10, self.settings.timeout_seconds),
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            raise TimeoutError("CODEX_AUTH_TIMEOUT") from exc
        status = auth.stdout + auth.stderr
        if (
            auth.returncode != 0
            or len(status) > 65536
            or b"Logged in using ChatGPT" not in status.splitlines()
        ):
            raise ValueError("CODEX_CHATGPT_LOGIN_REQUIRED")
        with tempfile.TemporaryDirectory(prefix="ahc-codex-") as directory:
            schema_file = Path(directory) / "schema.json"
            schema_file.write_text(
                json.dumps(strict_schema(schema)),
                encoding="utf-8",
            )
            command = [
                executable,
                "exec",
                "--ignore-user-config",
                "--strict-config",
                "--ephemeral",
                "--sandbox",
                "read-only",
                "--skip-git-repo-check",
                "--json",
                "--color",
                "never",
                "--model",
                self.settings.model,
                "--output-schema",
                str(schema_file),
                "--cd",
                directory,
            ]
            for override in OVERRIDES:
                command.extend(["--config", override])
            command.append("-")
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                cwd=directory,
                env=environment,
            )
            result: list[str] = []
            failures: list[Exception] = []

            def read() -> None:
                try:
                    assert process.stdout is not None
                    stream = process.stdout
                    result.append(
                        consume_events(iter(lambda: stream.readline(MAX_STREAM_BYTES + 1), b""))[0]
                    )
                except Exception as exc:
                    failures.append(exc)
                    process.kill()

            reader = threading.Thread(target=read, daemon=True)

            def write() -> None:
                try:
                    assert process.stdin is not None
                    process.stdin.write(prompt.encode())
                    process.stdin.close()
                except (OSError, ValueError):
                    pass  # A rejected/terminated invocation is handled by its exit status.

            writer = threading.Thread(target=write, daemon=True)
            reader.start()
            writer.start()
            try:
                process.wait(
                    timeout=max(0.001, self.settings.timeout_seconds - (monotonic() - started))
                )
                reader.join(timeout=5)
                if reader.is_alive():
                    raise ValueError("CODEX_STREAM_INCOMPLETE")
                if failures:
                    error = str(failures[0])
                    if error in {
                        "CODEX_OUTPUT_LIMIT",
                        "CODEX_EVENT_INVALID",
                        "CODEX_PROVIDER_ERROR",
                        "CODEX_UNEXPECTED_TOOL_EVENT",
                        "CODEX_INCOMPLETE",
                        "CODEX_EVENT_AFTER_COMPLETION",
                    }:
                        raise ValueError(error)
                    raise ValueError("CODEX_GENERATION_FAILED")
                if process.returncode != 0 or len(result) != 1:
                    raise ValueError("CODEX_GENERATION_FAILED")
                return result[0]
            except subprocess.TimeoutExpired as exc:
                raise TimeoutError("CODEX_TIMEOUT") from exc
            finally:
                if process.poll() is None:
                    process.kill()
                process.wait(timeout=5)
                reader.join(timeout=5)
                writer.join(timeout=5)
                if process.stdout is not None:
                    process.stdout.close()
                if process.stdin is not None:
                    process.stdin.close()
