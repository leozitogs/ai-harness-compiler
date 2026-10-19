"""Trusted operator CLI; none of these commands is an agent tool."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.scrum_operations import (
    OperationAuthorization,
    RemoteIssueState,
    ScrumOperationPlan,
)
from ai_harness_compiler.models.scrum_planning import ScrumPlanningReport
from ai_harness_compiler.scrum_collection import timestamp
from ai_harness_compiler.scrum_operations import OperationJournal, OperationRunner


def read_model[T: Contract](path: Path, model: type[T]) -> T:
    with path.open("rb") as stream:
        data = stream.read(12 * 1024 * 1024 + 1)
    if len(data) > 12 * 1024 * 1024:
        raise ValueError("Operation input exceeds twelve MiB")
    return model.model_validate_json(data)


def add_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    command = commands.add_parser("operation", help="Explicit authorized operator; no agent tools")
    sub = command.add_subparsers(dest="operation_command", required=True)
    inspect = sub.add_parser("inspect", help="Read exact remote issue state without writing")
    inspect.add_argument("--repo", required=True)
    inspect.add_argument("--issue", type=int, required=True)
    inspect.add_argument("--github", action="store_true", required=True)
    prepare = sub.add_parser("prepare", help="Persist concrete label diff without authorization")
    prepare.add_argument("--report", type=Path, required=True)
    prepare.add_argument("--expected", type=Path, required=True)
    prepare.add_argument("--proposal", required=True)
    prepare.add_argument("--story", required=True)
    prepare.add_argument("--label", required=True)
    prepare.add_argument("--journal", type=Path, required=True)
    for name in ("show", "authorize", "cancel", "apply", "reconcile"):
        item = sub.add_parser(name)
        item.add_argument("--journal", type=Path, required=True)
        item.add_argument("--operation", required=True)
        if name in {"authorize", "cancel"}:
            item.add_argument("--expected-version", type=int, required=True)
        if name == "authorize":
            item.add_argument("--expires-at", required=True)
            item.add_argument("--comment", required=True)
        if name in {"apply", "reconcile"}:
            item.add_argument("--repository", type=Path, default=Path.cwd())
            item.add_argument("--github", action="store_true", required=True)


def execute(args: argparse.Namespace) -> int:
    if args.operation_command == "inspect":
        from ai_harness_compiler.adapters.github_operations import GitHubOperationAdapter

        remote = GitHubOperationAdapter().read_issue(args.repo, args.issue, 10)
        print(json_text(remote.model_dump()), end="")
        return 0
    if args.operation_command != "prepare" and not args.journal.is_file():
        raise ValueError("Operation journal does not exist")
    journal = OperationJournal(args.journal)
    now = timestamp()
    if args.operation_command == "prepare":
        plan = ScrumOperationPlan.model_validate(
            {
                "report": read_model(args.report, ScrumPlanningReport).model_dump(),
                "proposal_id": args.proposal,
                "story_id": args.story,
                "label": args.label,
                "expected": read_model(args.expected, RemoteIssueState).model_dump(),
            }
        )
        event = journal.prepare(plan, now)
    else:
        plan, events = journal.load(args.operation)
        if args.operation_command == "authorize":
            authorization = OperationAuthorization(
                operation_sha256=args.operation,
                issued_at=now,
                expires_at=args.expires_at,
                comment=args.comment,
            )
            event = journal.append(
                args.operation,
                args.expected_version,
                "authorized",
                "human-authorized",
                now,
                authorization=authorization,
            )
        elif args.operation_command == "cancel":
            event = journal.append(
                args.operation, args.expected_version, "cancelled", "human-cancelled", now
            )
        elif args.operation_command in {"apply", "reconcile"}:
            from ai_harness_compiler.adapters.github_operations import GitHubOperationAdapter

            runner = OperationRunner(journal, args.repository, GitHubOperationAdapter())
            event = (
                runner.apply(args.operation)
                if args.operation_command == "apply"
                else runner.reconcile(args.operation)
            )
        else:
            event = events[-1]
    print(
        json_text(
            {
                "operation_sha256": plan.operation_sha256,
                "target": f"https://github.com/{plan.expected.repository}/issues/{plan.expected.number}",
                "expected_revision": plan.expected.revision,
                "before_labels": plan.expected.labels,
                "after_labels": sorted([*plan.expected.labels, plan.label]),
                "receipt": event.model_dump(),
                "receipt_sha256": event.receipt_sha256,
                "sprint_started": False,
                "criterion_acceptance": "not-established",
            }
        ),
        end="",
    )
    return 0 if event.state not in {"uncertain", "blocked"} else 2
