"""Executable Vera review and explicit current-evidence Nexo assessment."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.qa import QAInspection, QAReviewReport, QAReviewRequest
from ai_harness_compiler.models.scrum import SprintSnapshot
from ai_harness_compiler.qa import (
    assess_closure,
    compare_reviews,
    incident_candidates,
    project_for,
    review_report,
)
from ai_harness_compiler.qa_collection import assert_current_request, capture
from ai_harness_compiler.qa_runner import COMMANDS, run_checks
from ai_harness_compiler.scrum_collection import timestamp
from ai_harness_compiler.scrum_operation_cli import read_model


def add_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    command = commands.add_parser("qa", help="Vera evidence-bound QA review")
    sub = command.add_subparsers(dest="qa_command", required=True)
    collect = sub.add_parser("capture")
    collect.add_argument("--repository", type=Path, default=Path.cwd())
    collect.add_argument("--snapshot", type=Path, required=True)
    collect.add_argument("--base", required=True)
    collect.add_argument("--head", required=True)
    collect.add_argument("--author", required=True)
    collect.add_argument("--source", action="append", required=True)
    collect.add_argument("--checks", nargs="+", choices=list(COMMANDS))
    collect.add_argument("--output", type=Path, required=True)
    run = sub.add_parser("run")
    run.add_argument("input", type=Path)
    run.add_argument("--repository", type=Path, default=Path.cwd())
    run.add_argument("--output", type=Path, required=True)
    run.add_argument(
        "--engine", choices=["local", "primary", "codex-cli", "ollama"], default="local"
    )
    run.add_argument("--model")
    run.add_argument(
        "--trusted-checks-at", help="Explicitly trust executing fixed checks at this head"
    )
    run.add_argument(
        "--inspection", type=Path, help="Import advisory findings; never executed evidence"
    )
    run.add_argument(
        "--team", action="store_true", help="Run Vera and Nexo with persistent PO gate"
    )
    assess = sub.add_parser("assess")
    assess.add_argument("input", type=Path)
    assess.add_argument("--repository", type=Path, default=Path.cwd())
    assess.add_argument("--output", type=Path, required=True)
    compare = sub.add_parser("compare")
    compare.add_argument("previous", type=Path)
    compare.add_argument("current", type=Path)
    compare.add_argument("--repository", type=Path, default=Path.cwd())
    compare.add_argument("--output", type=Path, required=True)


def save_new(path: Path, data: dict[str, object]) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json_text(data))


def execute(args: argparse.Namespace) -> int:
    if args.output.exists():
        raise ValueError("QA output already exists; choose a new path")
    root = args.repository.resolve()
    if args.qa_command == "compare":
        previous, current = (
            read_model(args.previous, QAReviewReport),
            read_model(args.current, QAReviewReport),
        )
        assert_current_request(current.request, root, timestamp())
        save_new(args.output, compare_reviews(previous, current).model_dump())
        print("Compared observed checks; missing model findings do not establish resolution.")
        return 0
    if args.qa_command == "capture":
        request = capture(
            root,
            read_model(args.snapshot, SprintSnapshot),
            args.base,
            args.head,
            args.author,
            args.source,
            check_ids=args.checks,
        )
        save_new(args.output, request.model_dump())
        print(f"Captured QA request {request.request_sha256}; no code executed.")
        return 0
    if args.qa_command == "assess":
        report = read_model(args.input, QAReviewReport)
        assert_current_request(report.request, root, timestamp())
        save_new(args.output, assess_closure(report).model_dump())
        print("Saved advisory closure assessment; sprint remains open.")
        return 0
    request = read_model(args.input, QAReviewRequest)
    assert_current_request(request, root, timestamp())
    engine, model = args.engine, args.model
    if args.inspection is not None and (engine != "local" or model is not None):
        raise ValueError("Imported inspection cannot be combined with a model invocation")
    if engine == "local" and model is not None:
        raise ValueError("Local review cannot select a model")
    if engine == "primary" or (engine in {"codex-cli", "ollama"} and model is None):
        from ai_harness_compiler.model_policy import load_model_policy

        policy = load_model_policy()
        endpoint = policy.primary if engine == "primary" else policy.endpoint(engine)
        engine, model = endpoint.provider, endpoint.model if model is None else model
    checks = run_checks(
        request,
        root,
        args.trusted_checks_at,
        on_result=lambda c: print(f"QA check {c.id}: {c.status}", file=sys.stderr),
    )
    status = "not-requested"
    calls: int | None = 0
    attempts = 0
    inspection = QAInspection(
        limitations=[
            "No semantic inspection requested; checks alone do not establish business correctness.",
            "Criterion acceptance, performance and cost are not established by this review.",
        ]
    )
    if args.inspection is not None:
        engine, status = "provided-inspection", "completed"
        inspection = read_model(args.inspection, QAInspection)
    elif engine in {"codex-cli", "ollama"}:
        from ai_harness_compiler.adapters.qa_inspection import inspect

        calls, attempts = None, 1
        try:
            inspection = inspect(request, checks, root, engine, model or "")
            status = "completed"
            calls = 1
        except ModuleNotFoundError:
            raise
        except Exception:
            status = "rejected"
            inspection = QAInspection(
                limitations=[
                    "Model inspection failed or was rejected; no fallback or semantic pass.",
                ]
            )
    report = review_report(
        request,
        inspection,
        checks,
        engine=engine,
        model=model,
        inspection_status=status,
        model_calls=calls,
        model_attempts=attempts,
    )
    assert_current_request(request, root, timestamp())
    args.output.mkdir(parents=False, exist_ok=False)
    save_new(args.output / "qa-report.json", report.model_dump())
    save_new(args.output / "closure-assessment.json", assess_closure(report).model_dump())
    save_new(
        args.output / "incident-candidates.json",
        {
            "candidates": [c.model_dump() for c in incident_candidates(report)],
            "memory_modified": False,
        },
    )
    if args.team:
        from ai_harness_compiler.models.team import TeamConfig
        from ai_harness_compiler.team.runtime import prepare_team

        config = TeamConfig(
            project=project_for(request),
            selected=[s.id for s in request.snapshot.stories],
            request="Vera reviews QA evidence; Nexo prepares sprint review and explicit carryover.",
            mode="ask",
            repository_root=str(root),
            scrum_snapshot=request.snapshot,
            qa_report=report,
        )
        prepare_team(config, args.output / "team")
    print(
        f"Vera: {report.recommendation}; {len(report.inspection.findings)} advisory findings; "
        f"{sum(c.status == 'passed' for c in checks)} checks passed; acceptance not established."
    )
    return 0
