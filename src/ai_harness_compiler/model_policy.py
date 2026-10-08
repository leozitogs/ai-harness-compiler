"""Load the packaged operational preference; no network calls or provider fallback."""

from importlib.resources import files
from pathlib import Path

from ai_harness_compiler.models.model_policy import ModelPolicy


def load_model_policy(path: Path | None = None) -> ModelPolicy:
    if path is None:
        data = files("ai_harness_compiler").joinpath("default-model-policy.json").read_bytes()
    else:
        with path.open("rb") as stream:
            data = stream.read(65537)
    if len(data) > 65536:
        raise ValueError("MODEL_POLICY_LIMIT: Policy exceeds 64 KiB")
    return ModelPolicy.model_validate_json(data)
