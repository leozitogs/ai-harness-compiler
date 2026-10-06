"""CLI for roster, local/LLM runs, ML evaluation and explicit PO decisions."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.intake import DEFAULT_MAX_MANIFEST_BYTES, load_project
from ai_harness_compiler.models.team import POReview, TeamConfig


def add_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    team = commands.add_parser(
        "team", help="Project-specific team runtime (install the team extra)"
    )
    subcommands = team.add_subparsers(dest="team_command", required=True)
    subcommands.add_parser("list")
    subcommands.add_parser("evaluate-ml")
    run = subcommands.add_parser("run")
    run.add_argument("input", type=Path)
    run.add_argument("--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--request", default="Preparar a Sprint 1 para revisão do PO.")
    run.add_argument("--select", nargs="+", default=["ahc-001", "ahc-002", "ahc-003", "ahc-004"])
    run.add_argument("--mode", choices=["prepare", "ask"], default="prepare")
    run.add_argument("--engine", choices=["local", "ollama"], default="local")
    run.add_argument("--model", help="Explicit installed Ollama model name")
    run.add_argument("--repository", type=Path, default=Path.cwd())
    run.add_argument("--max-steps", type=int, default=5)
    review = subcommands.add_parser("review")
    review.add_argument("output", type=Path)
    review.add_argument("--decision", choices=["approve", "reject"], required=True)
    review.add_argument("--comment", required=True)


def execute(args: argparse.Namespace) -> int:
    # Imports of optional frameworks are confined to the explicitly invoked team command.
    from ai_harness_compiler.team.ml import IntentRouter
    from ai_harness_compiler.team.personas import PERSONAS
    from ai_harness_compiler.team.runtime import prepare_team, review_team

    if args.team_command == "list":
        result: object = [persona.model_dump() for persona in PERSONAS.values()]
    elif args.team_command == "evaluate-ml":
        result = IntentRouter().evaluate()
    elif args.team_command == "review":
        result = review_team(
            args.output,
            POReview.model_validate(
                {
                    "decision": args.decision,
                    "comment": args.comment,
                }
            ),
        )
    else:
        config = TeamConfig.model_validate(
            {
                "project": load_project(
                    args.input, max_manifest_bytes=args.max_manifest_bytes
                ).model_dump(),
                "selected": args.select,
                "request": args.request,
                "mode": args.mode,
                "engine": args.engine,
                "model": args.model,
                "max_steps": args.max_steps,
                "repository_root": str(args.repository.resolve()),
            }
        )
        result = prepare_team(config, args.output)
    print(json_text(result), end="")
    return 1 if isinstance(result, dict) and result.get("status") == "failed" else 0
