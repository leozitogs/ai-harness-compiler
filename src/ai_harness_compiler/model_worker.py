"""One local generation in a supervised process; stdout is a typed, bounded JSON result."""

import hashlib
import json
import platform
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import ValidationError

from ai_harness_compiler import __version__
from ai_harness_compiler.models.model_session import ModelIdentity, WorkerRequest, WorkerResult
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec

MAX_WORKER_BYTES = 2 * 1024 * 1024


def source_digest() -> str:
    root = Path(__file__).parent
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*.py")):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(path.read_bytes().replace(b"\r\n", b"\n"))
    return digest.hexdigest()


def execute(request: WorkerRequest) -> WorkerResult:
    # SDK imports are confined to this explicitly selected provider boundary.
    import httpx

    from ai_harness_compiler.adapters.ollama import (
        OllamaSettings,
        OllamaUnderstandingModel,
        prompt_digest,
    )

    if request.prompt_sha256 != prompt_digest(request.settings.analysis_mode):
        return WorkerResult(status="error", error_code="prompt-mismatch")

    def metadata(client: httpx.Client, method: str, path: str) -> dict[str, Any]:
        with client.stream(
            method,
            "http://127.0.0.1:11434/api/" + path,
            json={"model": request.settings.model} if method == "POST" else None,
        ) as response:
            response.raise_for_status()
            data = bytearray()
            for chunk in response.iter_bytes(chunk_size=8192):
                if len(data) + len(chunk) > MAX_WORKER_BYTES:
                    raise ValueError("Metadata exceeds byte budget")
                data.extend(chunk)
        value = json.loads(data)
        if not isinstance(value, dict):
            raise ValueError("Metadata must be an object")
        return value

    def identity(client: httpx.Client) -> ModelIdentity:
        tags = metadata(client, "GET", "tags").get("models", [])
        if not isinstance(tags, list):
            raise ValueError("Model tags must be a list")
        found = next(
            (
                item
                for item in tags
                if isinstance(item, dict)
                and item.get("name")
                in {
                    request.settings.model,
                    request.settings.model + ":latest",
                }
            ),
            None,
        )
        if not found or found.get("details", {}).get("format") != "gguf":
            raise ValueError("Installed local GGUF model required")
        show = metadata(client, "POST", "show")
        if show.get("remote_host") or show.get("remote_model"):
            raise ValueError("Remote model not permitted by local session adapter")
        parameters = show.get("parameters")
        if not isinstance(parameters, str):
            raise ValueError("Model parameter metadata unavailable")
        return ModelIdentity(
            requested_model=request.settings.model,
            model_sha256=found["digest"],
            parameters_sha256=hashlib.sha256(parameters.encode()).hexdigest(),
            quantization=found["details"]["quantization_level"],
            family=found["details"]["family"],
            model_size_bytes=found["size"],
            provider_version=metadata(client, "GET", "version")["version"],
            compiler_version=__version__,
            compiler_source_sha256=source_digest(),
            python_version=platform.python_version(),
            platform_system=platform.system(),
            observed_at=datetime.now(UTC).isoformat(),
            prompt_sha256=request.prompt_sha256,
        )

    try:
        settings = OllamaSettings(
            model=request.settings.model,
            timeout_seconds=request.settings.call_timeout_seconds,
            max_output_tokens=request.settings.max_output_tokens,
            context_tokens=request.settings.context_tokens,
        )
        with httpx.Client(timeout=5, trust_env=False, follow_redirects=False) as client:
            before = identity(client)
            if request.settings.expected_model_sha256 and (
                before.model_sha256 != request.settings.expected_model_sha256
            ):
                return WorkerResult(status="error", error_code="model-changed")
            model = OllamaUnderstandingModel(settings)
            grounded = None
            if request.settings.analysis_mode == "grounded":
                from ai_harness_compiler.grounding import extract_grounding
                from ai_harness_compiler.models.grounded_analysis import (
                    GroundedAnalysisSpec,
                    GroundingInvariantError,
                )

                extraction = extract_grounding(request.request.original_input)
                if extraction.request != request.request:
                    return WorkerResult(status="error", error_code="grounded-input-invalid")
                try:
                    analysis, observation = model.generate_grounded(extraction)
                except ValueError as error:
                    # Only fixed public codes are recorded. Never persist raw provider/error text.
                    adapter_codes = {
                        "STUDY_INVALID": "grounded-output-invalid",
                        "STUDY_TRUNCATED": "output-token-limit",
                        "STUDY_INPUT_LIMIT": "input-byte-limit",
                        "STUDY_RESPONSE_LIMIT": "response-byte-limit",
                        "STUDY_PROPOSAL_LIMIT": "proposal-byte-limit",
                        "STUDY_PROVIDER": "provider-call-error",
                        "STUDY_DEADLINE": "provider-deadline",
                        "STUDY_INCOMPLETE": "provider-response-incomplete",
                        "STUDY_MESSAGE": "provider-message-invalid",
                    }
                    code = adapter_codes.get(str(error).split(":", 1)[0], "grounded-output-invalid")
                    return WorkerResult(status="error", error_code=code)
                try:
                    grounded = GroundedAnalysisSpec(extraction=extraction, analysis=analysis)
                except ValidationError as error:
                    codes = [
                        issue.get("ctx", {}).get("error")
                        for issue in error.errors(include_input=False)
                    ]
                    code = next(
                        (
                            issue.code
                            for issue in codes
                            if isinstance(issue, GroundingInvariantError)
                        ),
                        "grounded-analysis-invalid",
                    )
                    return WorkerResult(status="error", error_code=code)
                spec = grounded.understanding
            else:
                reply = model.generate(request.request)
                observation = reply.observation
                spec = ProjectUnderstandingSpec(request=request.request, proposal=reply.proposal)
            if observation.returned_model not in {
                request.settings.model,
                request.settings.model + ":latest",
            }:
                return WorkerResult(status="error", error_code="model-changed")
            after = identity(client)
        if before.model_dump(exclude={"observed_at"}) != after.model_dump(exclude={"observed_at"}):
            return WorkerResult(status="error", error_code="model-changed")
        return WorkerResult(
            status="completed",
            identity=before,
            settings=request.settings,
            understanding=spec,
            grounded_analysis=grounded,
            observation=observation,
        )
    except (httpx.HTTPError, ValueError, KeyError, TypeError, RecursionError):
        return WorkerResult(status="error", error_code="provider-or-metadata-error")


def main() -> int:
    try:
        data = sys.stdin.buffer.read(MAX_WORKER_BYTES + 1)
        if len(data) > MAX_WORKER_BYTES:
            raise ValueError("Worker input exceeds byte budget")
        request = WorkerRequest.model_validate_json(data)
        result = execute(request)
    except Exception:
        # Never expose private provider bodies, prompts or traceback contents over IPC.
        result = WorkerResult(status="error", error_code="worker-input-or-runtime-error")
    output = result.model_dump_json().encode()
    if len(output) > MAX_WORKER_BYTES:
        output = (
            WorkerResult(status="error", error_code="worker-output-limit")
            .model_dump_json()
            .encode()
        )
    sys.stdout.buffer.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
