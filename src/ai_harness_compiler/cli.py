"""The public CLI: validate, plan, compile, build and export JSON Schemas."""

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from ai_harness_compiler import __version__
from ai_harness_compiler.compiler import compile_harness, json_text
from ai_harness_compiler.intake import DEFAULT_MAX_MANIFEST_BYTES, load_project
from ai_harness_compiler.models import CapabilityGraph, HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.evidence import EvidencePack, SourceRecord
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
    "evidence-pack": EvidencePack,
    "source-record": SourceRecord,
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
        command.add_argument(
            "--max-manifest-bytes",
            type=int,
            default=DEFAULT_MAX_MANIFEST_BYTES,
            help="Maximum manifest size in bytes (default: 1048576)",
        )
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
    migration_command = commands.add_parser(
        "migrate", help="Explicitly migrate baseline IR v1 to v2"
    )
    migration_command.add_argument("input", type=Path)
    migration_command.add_argument("--output", type=Path, required=True, help="New JSON file")
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
        if args.command == "migrate":
            from ai_harness_compiler.migration import migrate_harness_v1

            payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
            if not isinstance(payload, dict):
                raise ValueError("Legacy IR must be a mapping")
            migrated = migrate_harness_v1(payload)
            content = json_text(migrated.model_dump())
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            print(f"Migrated HarnessSpec/v1 to HarnessSpec/v2: {args.output}")
            return 0
        if args.command == "compile":
            content = args.input.read_text(encoding="utf-8-sig")
            if (
                isinstance(legacy := json.loads(content), dict)
                and legacy.get("schema_version") == "HarnessSpec/v1"
            ):
                raise ValueError("HarnessSpec/v1 requires explicit migration with factory migrate")
            spec = HarnessSpec.model_validate_json(content)
        else:
            spec = plan(load_project(args.input, max_manifest_bytes=args.max_manifest_bytes))
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
