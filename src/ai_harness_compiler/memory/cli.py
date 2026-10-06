"""Documentation and experience registration for chat-based and runtime agents."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import yaml

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.memory.store import MemoryStore
from ai_harness_compiler.models.memory import RecordDraft


def add_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    memory = commands.add_parser("memory", help="Versioned engineering decisions and lessons")
    memory.add_argument("--repository", type=Path, default=Path.cwd())
    memory.add_argument("--project", default="ai-harness-compiler")
    children = memory.add_subparsers(dest="memory_command", required=True)
    for name in ("add", "revise"):
        action = children.add_parser(name)
        action.add_argument("input", type=Path)
        if name == "revise":
            action.add_argument("--expected", required=True, type=int)
    search = children.add_parser("search")
    search.add_argument("query")
    search.add_argument("--include-drafts", action="store_true")
    show = children.add_parser("show")
    show.add_argument("id")
    review = children.add_parser("review")
    review.add_argument("id")
    review.add_argument("--expected", required=True, type=int)
    review.add_argument("--status", choices=["active", "verified", "superseded"], required=True)
    review.add_argument("--reviewer", required=True)
    review.add_argument("--note", required=True)
    index = children.add_parser("index")
    index.add_argument("--check", action="store_true")
    children.add_parser("check")
    digest = children.add_parser("digest")
    digest.add_argument("source")
    capture = children.add_parser("capture-team")
    capture.add_argument("report", type=Path)
    capture.add_argument("--id", required=True, help="New INC-NNNN ID")


def execute(args: argparse.Namespace) -> int:
    store = MemoryStore(args.repository, args.project)
    result: object
    try:
        match args.memory_command:
            case "add" | "revise":
                if args.input.stat().st_size > 64 * 1024:
                    raise ValueError("Draft exceeds 64 KiB")
                draft = RecordDraft.model_validate(
                    yaml.safe_load(args.input.read_text(encoding="utf-8"))
                )
                record = (
                    store.add(draft)
                    if args.memory_command == "add"
                    else store.revise(draft, args.expected)
                )
                result = record.model_dump()
            case "review":
                result = store.review(
                    args.id, args.expected, args.status, args.reviewer, args.note
                ).model_dump()
            case "show":
                result = store.latest()[args.id].model_dump()
            case "search":
                result = store.search(args.query, include_drafts=args.include_drafts)
            case "check":
                records = store.latest()
                result = {
                    "records": len(records),
                    "reusable": len(store.reusable()),
                    "status": "valid",
                    "source_of_truth": "versioned-json-revisions",
                }
            case "index":
                expected = store.render_index()
                target = store.safe_path("knowledge/INDEX.md")
                if args.check:
                    if not target.is_file() or target.read_text(encoding="utf-8") != expected:
                        raise ValueError("Knowledge index is stale; run factory memory index")
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(expected, encoding="utf-8", newline="\n")
                result = {"index": str(target), "status": "current"}
            case "digest":
                source = store.safe_path(args.source.split("#", 1)[0])
                if not source.is_file() or source.stat().st_size > 1024 * 1024:
                    raise ValueError("Evidence source missing or exceeds 1 MiB")
                result = {
                    "source": args.source,
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                }
            case "capture-team":
                report_path = args.report.resolve()
                if (
                    not report_path.is_relative_to(store.root)
                    or report_path.stat().st_size > 2 * 1024 * 1024
                ):
                    raise ValueError("Team report must be inside repository and at most 2 MiB")
                report = json.loads(report_path.read_text(encoding="utf-8"))
                if not isinstance(report, dict) or not isinstance(report.get("reports"), list):
                    raise ValueError("Invalid team report shape")
                if not all(
                    isinstance(item, dict)
                    and isinstance(item.get("agent_id"), str)
                    and item.get("status") in {"completed", "failed"}
                    for item in report["reports"]
                ):
                    raise ValueError("Invalid team specialist report")
                failed = [
                    item["agent_id"] for item in report["reports"] if item["status"] == "failed"
                ]
                if not failed:
                    result = {"captured": False, "reason": "No specialist failure in report"}
                else:
                    relative = report_path.relative_to(store.root).as_posix()
                    draft = RecordDraft.model_validate(
                        {
                            "id": args.id,
                            "kind": "INC",
                            "project_id": args.project,
                            "title": "Falha na execução de especialistas",
                            "author": "agent-team-capture",
                            "summary": f"Especialistas com falha: {', '.join(failed)}.",
                            "context": "Captura de estado; diagnóstico e revisão ainda pendentes.",
                            "challenge": "A equipe não chegou a uma proposta aprovável.",
                            "tags": ["agents", "runtime", "failure"],
                            "evidence": [
                                {
                                    "source": relative,
                                    "note": "Report snapshot; raw model output is not copied.",
                                    "outcome": "failed",
                                    "sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
                                }
                            ],
                        }
                    )
                    result = store.add(draft).model_dump()
            case _:
                raise ValueError("Unknown memory command")
    except KeyError as exc:
        raise ValueError(f"Unknown record or invalid report field: {exc}") from exc
    print(json_text(result), end="")
    return 0
