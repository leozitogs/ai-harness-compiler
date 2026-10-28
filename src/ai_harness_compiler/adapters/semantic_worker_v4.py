"""Fixed one-request worker. The supervisor establishes containment before sending work."""

import json
import sys
from typing import Any

from pydantic import Field

from ai_harness_compiler.models.base import Contract, Text

MAX_REQUEST_BYTES = 2 * 1024 * 1024

# Only exact, trusted adapter codes map to a diagnostic. Never emit exception text.
PROVIDER_EXITS = {
    "CODEX_UNAVAILABLE": 22,
    "CODEX_CHATGPT_LOGIN_REQUIRED": 23,
    "CODEX_AUTH_TIMEOUT": 24,
    "CODEX_TIMEOUT": 25,
    "CODEX_PROVIDER_ERROR": 26,
    "CODEX_OUTPUT_LIMIT": 27,
    "CODEX_EVENT_INVALID": 28,
    "CODEX_EVENT_AFTER_COMPLETION": 28,
    "CODEX_UNEXPECTED_TOOL_EVENT": 29,
    "CODEX_INCOMPLETE": 30,
    "CODEX_STREAM_INCOMPLETE": 30,
    "CODEX_GENERATION_FAILED": 31,
    "CODEX_INPUT_LIMIT": 35,
}


class WorkerRequest(Contract):
    model: Text
    prompt: Text
    response_schema: dict[str, Any]
    timeout_seconds: int = Field(ge=1, le=300)


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            return 20
        request = WorkerRequest.model_validate_json(raw)
    except OSError:
        return 38
    except Exception:
        return 21
    try:
        # Import/instantiate provider only AFTER receiving and validating authorized work.
        from ai_harness_compiler.adapters.codex_cli import CodexCLISettings, CodexCompactModel

        generator = CodexCompactModel(
            CodexCLISettings(model=request.model, timeout_seconds=request.timeout_seconds)
        )
    except Exception:
        return 37
    try:
        response = generator.generate_json(request.prompt, request.response_schema)
    except (ValueError, TimeoutError) as exc:
        # Match one constant token, never substrings, arbitrary str(exc) or causes.
        if len(exc.args) == 1 and type(exc.args[0]) is str:
            return PROVIDER_EXITS.get(exc.args[0], 31)
        return 31
    except OSError:
        return 36
    except Exception:
        return 31
    try:
        # Pipes use the host locale on Windows. The wire protocol is UTF-8,
        # independent of stdout's text encoding and the response language.
        sys.stdout.buffer.write(
            json.dumps({"response": response}, ensure_ascii=False).encode("utf-8")
        )
        sys.stdout.buffer.flush()
        return 0
    except UnicodeError:
        return 32
    except OSError:
        return 33
    except Exception:
        return 34


if __name__ == "__main__":
    raise SystemExit(main())
