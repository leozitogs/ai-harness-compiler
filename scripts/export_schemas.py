"""Update checked-in schemas, or verify they match the Python source."""

import argparse
from pathlib import Path

from ai_harness_compiler.cli import MODELS
from ai_harness_compiler.compiler import json_text

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args = parser.parse_args()
root = Path(__file__).resolve().parents[1] / "schemas"
root.mkdir(exist_ok=True)
for name, model in MODELS.items():
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
