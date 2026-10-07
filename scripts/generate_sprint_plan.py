"""Regenerate a reviewable task graph from this project's input and selected sprint."""

import argparse
import json
import re
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.intake import load_project
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.planning import decompose

parser = argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
parser.add_argument(
    "--sprint", default="sprint-1", help="Planning ID, such as sprint-2 or sprint-2-5"
)
args = parser.parse_args()
if not re.fullmatch(r"sprint-[1-9][0-9]*(?:-[1-9][0-9]*)?", args.sprint):
    parser.error("Sprint ID must match sprint-N or sprint-N-M with positive integer parts")
root = Path(__file__).resolve().parents[1]
sprint = json.loads((root / f"planning/{args.sprint}.json").read_text(encoding="utf-8"))
spec = plan(load_project(root / "project-definition"))
tasks = decompose(
    spec.capability_graph,
    sprint["selected_capabilities"],
    sprint["declared_completed_capabilities"],
)
content = json_text(tasks.model_dump())
target = root / f"planning/{args.sprint}.tasks.json"
if args.check:
    if not target.exists() or target.read_text(encoding="utf-8") != content:
        raise SystemExit(
            "Sprint task plan is stale; run uv run python scripts/generate_sprint_plan.py "
            f"--sprint {args.sprint}"
        )
else:
    target.write_text(content, encoding="utf-8", newline="\n")
print(
    f"Sprint plan verified: {len(tasks.tasks)} tasks; "
    f"{len(tasks.ready_batches())} scheduling waves."
)
