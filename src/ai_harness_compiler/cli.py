"""The public CLI: validate, plan, compile, build and export JSON Schemas."""

import argparse
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from ai_harness_compiler import __version__
from ai_harness_compiler.compiler import compile_harness, json_text
from ai_harness_compiler.intake import load_project
from ai_harness_compiler.models import CapabilityGraph, HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.memory import MemoryRecord, RecordDraft
from ai_harness_compiler.models.task import TaskGraph
from ai_harness_compiler.models.team import AgentReport, Persona, TeamConfig
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.planning import decompose

MODELS: dict[str, type[Contract]] = {
    "project-input": ProjectInput,
    "project-dna": ProjectDNA,
    "capability-graph": CapabilityGraph,
    "harness-spec": HarnessSpec,
    "task-graph": TaskGraph,
    "team-config": TeamConfig,
    "agent-report": AgentReport,
    "agent-persona": Persona,
    "memory-record": MemoryRecord,
    "memory-draft": RecordDraft,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compile project intent into a development harness."
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)
    from ai_harness_compiler.team.cli import add_commands

    add_commands(commands)
    from ai_harness_compiler.memory.cli import add_commands as add_memory_commands

    add_memory_commands(commands)
    for name in ("validate", "plan", "build", "tasks"):
        command = commands.add_parser(name)
        command.add_argument("input", type=Path, help="project.yaml or its parent directory")
        if name == "build":
            command.add_argument("--output", type=Path, required=True, help="New output directory")
        if name == "tasks":
            command.add_argument("--select", nargs="+", help="Capability IDs to decompose")
            command.add_argument(
                "--completed", nargs="+", help="User-declared completed prerequisites"
            )
    compile_command = commands.add_parser(
        "compile", help="Compile a reviewed HarnessSpec JSON file"
    )
    compile_command.add_argument("input", type=Path)
    compile_command.add_argument("--output", type=Path, required=True)
    schema_command = commands.add_parser("schema", help="Print a JSON Schema to stdout")
    schema_command.add_argument("model", choices=MODELS)
    args = parser.parse_args(argv)
    try:
        if args.command == "memory":
            from ai_harness_compiler.memory.cli import execute as execute_memory

            return execute_memory(args)
        if args.command == "team":
            from ai_harness_compiler.team.cli import execute

            return execute(args)
        if args.command == "schema":
            print(json_text(MODELS[args.model].model_json_schema()), end="")
            return 0
        if args.command == "compile":
            spec = HarnessSpec.model_validate_json(args.input.read_text(encoding="utf-8-sig"))
        else:
            spec = plan(load_project(args.input))
        if args.command == "validate":
            print(f"Valid: {spec.project_dna.project.id}; {len(spec.evals)} planned evals.")
        elif args.command == "tasks":
            graph = decompose(spec.capability_graph, args.select, args.completed)
            print(json_text(graph.model_dump()), end="")
        elif args.command == "plan":
            print(json_text(spec.model_dump()), end="")
        else:
            result = compile_harness(spec, args.output)
            print(f"Built development harness: {result}")
            print("Product evals: not-run. Runtime and installation: not implemented.")
        return 0
    except (OSError, ValueError, ValidationError, yaml.YAMLError) as exc:
        print(f"factory: {exc}", file=sys.stderr)
        return 1
    except ModuleNotFoundError as exc:
        if args.command != "team":
            raise
        print(
            f"factory: install the team extra with uv sync --extra team ({exc.name})",
            file=sys.stderr,
        )
        return 1
