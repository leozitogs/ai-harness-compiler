"""Fixed one-request worker. The supervisor establishes containment before sending work."""

import json
import sys
from typing import Any

from pydantic import Field

from ai_harness_compiler.models.base import Contract, Text

MAX_REQUEST_BYTES = 2 * 1024 * 1024


class WorkerRequest(Contract):
    model: Text
    prompt: Text
    response_schema: dict[str, Any]
    timeout_seconds: int = Field(ge=1, le=300)


def main() -> int:
    try:
        raw = sys.stdin.buffer.read(MAX_REQUEST_BYTES + 1)
        if len(raw) > MAX_REQUEST_BYTES:
            return 2
        request = WorkerRequest.model_validate_json(raw)
        # Import/instantiate provider only AFTER receiving and validating authorized work.
        from ai_harness_compiler.adapters.codex_cli import CodexCLISettings, CodexCompactModel

        generator = CodexCompactModel(
            CodexCLISettings(model=request.model, timeout_seconds=request.timeout_seconds)
        )
        response = generator.generate_json(request.prompt, request.response_schema)
        # Pipes use the host locale on Windows. The wire protocol is UTF-8,
        # independent of stdout's text encoding and the response language.
        sys.stdout.buffer.write(
            json.dumps({"response": response}, ensure_ascii=False).encode("utf-8")
        )
        sys.stdout.buffer.flush()
        return 0
    except Exception:
        return 2  # No raw provider errors, prompts, credentials or intermediate events.


if __name__ == "__main__":
    raise SystemExit(main())
