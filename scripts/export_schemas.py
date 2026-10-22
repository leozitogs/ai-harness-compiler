"""Update checked-in schemas, or verify they match the Python source."""

import argparse
from pathlib import Path

from ai_harness_compiler.cli import MODELS
from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.offline_schema_registry import OFFLINE_MODELS

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / "schemas"
root.mkdir(exist_ok=True)
if MODELS.keys() & OFFLINE_MODELS.keys():
    raise SystemExit("Offline schema names must not replace historical CLI schemas")
for name, model in (MODELS | OFFLINE_MODELS).items():
    target = root / f"{name}.schema.json"
    content = json_text(model.model_json_schema())
    if args.check:
        if not target.exists() or target.read_text(encoding="utf-8") != content:
            raise SystemExit(
                f"Stale schema: {target.name}; run uv run python scripts/export_schemas.py"
            )
    else:
        target.write_text(content, encoding="utf-8", newline="\n")
print("Schemas are current.")
