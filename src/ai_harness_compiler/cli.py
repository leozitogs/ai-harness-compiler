"""The public CLI: validate, plan, compile, build and export JSON Schemas."""

import argparse
import json
import sys
from pathlib import Path

import yaml
from pydantic import ValidationError

from ai_harness_compiler import __version__
from ai_harness_compiler.comparison_runner import ComparisonPlan
from ai_harness_compiler.compiler import compile_harness, json_text
from ai_harness_compiler.intake import DEFAULT_MAX_MANIFEST_BYTES, load_project
from ai_harness_compiler.models import CapabilityGraph, HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.benchmark import BenchmarkReport, BenchmarkSuite
from ai_harness_compiler.models.compact_analysis import (
    CompactAnalysisSpec,
    CompactInput,
    CompactProposal,
)
from ai_harness_compiler.models.comparison import ComparisonReport
from ai_harness_compiler.models.domain import DomainProfile
from ai_harness_compiler.models.evidence import EvidencePack, SourceRecord
from ai_harness_compiler.models.grounded_analysis import (
    GroundedAnalysisProposal,
    GroundedAnalysisSpec,
    GroundedRepairInput,
    GroundingDiagnostic,
)
from ai_harness_compiler.models.grounding import GroundingExtraction, GroundingQuotationReport
from ai_harness_compiler.models.memory import MemoryRecord, RecordDraft
from ai_harness_compiler.models.model_session import (
    ModelSessionReport,
    SessionPlan,
    SessionSettings,
    WorkerResult,
)
from ai_harness_compiler.models.repair import RepairPlan, RepairReport
from ai_harness_compiler.models.semantic_eval import (
    FrozenUnderstandingCorpus,
    SemanticReview,
    UnderstandingEvalReport,
    UnderstandingEvalSuite,
    UnderstandingRubric,
)
from ai_harness_compiler.models.task import TaskGraph
from ai_harness_compiler.models.team import AgentReport, Persona, TeamConfig
from ai_harness_compiler.models.understanding import (
    ProjectUnderstandingSpec,
    UnderstandingProposal,
    UnderstandingRequest,
)
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
    "domain-profile": DomainProfile,
    "benchmark-suite": BenchmarkSuite,
    "benchmark-report": BenchmarkReport,
    "understanding-request": UnderstandingRequest,
    "understanding-proposal": UnderstandingProposal,
    "project-understanding": ProjectUnderstandingSpec,
    "understanding-rubric": UnderstandingRubric,
    "understanding-eval-suite": UnderstandingEvalSuite,
    "understanding-eval-report": UnderstandingEvalReport,
    "semantic-review": SemanticReview,
    "frozen-understanding-corpus": FrozenUnderstandingCorpus,
    "model-session-plan": SessionPlan,
    "model-session-report": ModelSessionReport,
    "model-worker-result": WorkerResult,
    "grounding-extraction": GroundingExtraction,
    "grounding-quotation-report": GroundingQuotationReport,
    "grounded-analysis-proposal": GroundedAnalysisProposal,
    "grounded-analysis": GroundedAnalysisSpec,
    "grounding-diagnostic": GroundingDiagnostic,
    "grounded-repair-input": GroundedRepairInput,
    "understanding-repair-plan": RepairPlan,
    "understanding-repair-report": RepairReport,
    "compact-understanding-input": CompactInput,
    "compact-understanding-proposal": CompactProposal,
    "compact-understanding": CompactAnalysisSpec,
    "understanding-comparison": ComparisonReport,
    "understanding-comparison-plan": ComparisonPlan,
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
        "migrate", help="Explicitly migrate compatible IR v1/v2 to v3"
    )
    migration_command.add_argument("input", type=Path)
    migration_command.add_argument("--output", type=Path, required=True, help="New JSON file")
    benchmark_command = commands.add_parser("benchmark", help="Measure offline compiler fixtures")
    benchmark_command.add_argument("suite", type=Path)
    benchmark_command.add_argument(
        "--workspace", type=Path, required=True, help="New build session directory"
    )
    benchmark_command.add_argument(
        "--output", type=Path, required=True, help="New report JSON file"
    )
    benchmark_command.add_argument("--runs", type=int, default=3)
    prepare_command = commands.add_parser(
        "prepare-understanding", help="Prepare grounded input without invoking a model"
    )
    prepare_command.add_argument("input", type=Path)
    prepare_command.add_argument(
        "--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES
    )
    grounding_command = commands.add_parser(
        "prepare-grounding", help="Extract literal manifest evidence offline; assets are not read"
    )
    grounding_command.add_argument("input", type=Path)
    grounding_command.add_argument(
        "--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES
    )
    quotation_command = commands.add_parser(
        "verify-grounding", help="Check criterion quotations; semantic judgment stays pending"
    )
    quotation_command.add_argument("input", type=Path)
    quotation_command.add_argument("--output", type=Path, required=True, help="New JSON report")
    understanding_command = commands.add_parser(
        "validate-understanding", help="Validate understanding snapshot/proposal/review metadata"
    )
    understanding_command.add_argument("input", type=Path)
    understanding_command.add_argument(
        "--max-understanding-bytes", type=int, default=4 * 1024 * 1024
    )
    study_command = commands.add_parser("study", help="Propose understanding with local Ollama")
    study_command.add_argument("input", type=Path)
    study_command.add_argument("--model", required=True, help="Explicit installed Ollama model")
    study_command.add_argument("--output", type=Path, required=True, help="New proposal JSON file")
    study_command.add_argument("--timeout-seconds", type=int, default=60)
    study_command.add_argument("--max-output-tokens", type=int, default=4096)
    study_command.add_argument("--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES)
    eval_command = commands.add_parser("eval-understanding", help="Evaluate saved artifact offline")
    eval_command.add_argument("input", type=Path)
    eval_command.add_argument("--corpus", type=Path, required=True)
    eval_command.add_argument("--split", choices=["development", "holdout"], default="development")
    eval_command.add_argument("--case", required=True)
    eval_command.add_argument("--output", type=Path, required=True)
    eval_command.add_argument("--review", type=Path)
    eval_command.add_argument("--allow-holdout", action="store_true")
    eval_command.add_argument("--candidate-sha256")
    eval_validation = commands.add_parser(
        "validate-eval-report", help="Bind report to frozen corpus"
    )
    eval_validation.add_argument("input", type=Path)
    eval_validation.add_argument("--corpus", type=Path, required=True)
    session_command = commands.add_parser(
        "run-understanding-evals", help="Generate local Ollama cases in bounded isolated jobs"
    )
    session_command.add_argument("--corpus", type=Path, required=True)
    session_command.add_argument("--model", required=True)
    session_command.add_argument("--output", type=Path, required=True, help="New session directory")
    session_command.add_argument("--case", nargs="+")
    session_command.add_argument(
        "--split", choices=["development", "holdout"], default="development"
    )
    session_command.add_argument("--repeats", type=int, default=1)
    session_command.add_argument("--max-attempts", type=int, default=30)
    session_command.add_argument("--session-seconds", type=int, default=3600)
    session_command.add_argument("--timeout-seconds", type=int, default=180)
    session_command.add_argument("--context-tokens", type=int, default=8192)
    session_command.add_argument("--max-output-tokens", type=int, default=4096)
    session_command.add_argument(
        "--analysis-mode", choices=["baseline", "grounded", "compact"], default="baseline"
    )
    session_command.add_argument("--expected-model-sha256")
    session_command.add_argument("--allow-holdout", action="store_true")
    session_command.add_argument("--candidate-sha256")
    session_validation = commands.add_parser(
        "validate-model-session", help="Validate session journal"
    )
    session_validation.add_argument("input", type=Path, help="Session directory")
    session_validation.add_argument("--corpus", type=Path, required=True)
    repair_command = commands.add_parser(
        "run-understanding-repair", help="One development case with bounded charged repair attempts"
    )
    repair_command.add_argument("--corpus", type=Path, required=True)
    repair_command.add_argument("--case", required=True)
    repair_command.add_argument("--model", required=True)
    repair_command.add_argument("--expected-model-sha256", required=True)
    repair_command.add_argument("--output", type=Path, required=True)
    repair_command.add_argument("--max-repairs", type=int, default=1)
    repair_command.add_argument("--max-attempts", type=int, default=3)
    repair_command.add_argument("--session-seconds", type=int, default=300)
    repair_command.add_argument("--timeout-seconds", type=int, default=180)
    repair_command.add_argument("--context-tokens", type=int, default=8192)
    repair_command.add_argument("--max-output-tokens", type=int, default=4096)
    repair_validation = commands.add_parser(
        "validate-understanding-repair", help="Verify repair journal and frozen corpus"
    )
    repair_validation.add_argument("input", type=Path)
    repair_validation.add_argument("--corpus", type=Path, required=True)
    comparison_command = commands.add_parser(
        "compare-understanding", help="One development case with local and subscription proposals"
    )
    comparison_command.add_argument("--corpus", type=Path, required=True)
    comparison_command.add_argument("--case", required=True)
    comparison_command.add_argument("--ollama-model", required=True)
    comparison_command.add_argument("--codex-model", required=True)
    comparison_command.add_argument("--expected-model-sha256", required=True)
    comparison_command.add_argument("--timeout-seconds", type=int, default=180)
    comparison_command.add_argument("--output", type=Path, required=True)
    comparison_validation = commands.add_parser(
        "validate-understanding-comparison", help="Validate saved provider comparison offline"
    )
    comparison_validation.add_argument("input", type=Path)
    comparison_validation.add_argument("--corpus", type=Path, required=True)
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
        if args.command in {"compare-understanding", "validate-understanding-comparison"}:
            from ai_harness_compiler.comparison_runner import (
                run_development_comparison,
                validate_development_comparison,
            )
            from ai_harness_compiler.semantic_eval import FrozenCorpus

            comparison_corpus = FrozenCorpus(args.corpus)
            if args.command == "validate-understanding-comparison":
                validate_development_comparison(comparison_corpus, args.input)
                print("Comparison journal valid; semantic judgment and qualification pending.")
                return 0
            comparison = run_development_comparison(
                comparison_corpus,
                args.case,
                args.ollama_model,
                args.codex_model,
                args.expected_model_sha256,
                args.output,
                args.timeout_seconds,
            )
            print(
                f"Proposals: {sum(c.status == 'completed' for c in comparison.candidates)}/2; "
                f"textual disagreements: {len(comparison.criterion_disagreements)}."
            )
            print("Semantic judgment pending; model qualification: not-established.")
            return 0 if all(c.status == "completed" for c in comparison.candidates) else 1
        if args.command in {"run-understanding-repair", "validate-understanding-repair"}:
            from ai_harness_compiler.repairs import run_repair, validate_repair
            from ai_harness_compiler.semantic_eval import FrozenCorpus

            corpus = FrozenCorpus(args.corpus)
            if args.command == "validate-understanding-repair":
                repaired = validate_repair(corpus, args.input)
                print(
                    f"Repair journal valid: {repaired.termination}; qualification: not-established."
                )
                return 0
            from ai_harness_compiler.adapters.ollama import OllamaSettings, prompt_digest
            from ai_harness_compiler.model_sessions import IsolatedOllamaExecutor, make_plan

            OllamaSettings(model=args.model)
            settings = SessionSettings(
                model=args.model,
                analysis_mode="grounded",
                expected_model_sha256=args.expected_model_sha256,
                max_attempts=args.max_attempts,
                session_seconds=args.session_seconds,
                call_timeout_seconds=args.timeout_seconds,
                context_tokens=args.context_tokens,
                max_output_tokens=args.max_output_tokens,
            )
            repair_plan = RepairPlan(
                session=make_plan(corpus, settings, prompt_digest("grounded"), [args.case]),
                max_repairs=args.max_repairs,
                repair_prompt_sha256=prompt_digest("repair"),
            )
            repaired = run_repair(repair_plan, args.output, IsolatedOllamaExecutor())
            artifact_state = repaired.evaluation.status if repaired.evaluation else "not-run"
            print(
                f"Repair: {repaired.termination}; attempts: {len(repaired.attempts)}; "
                f"artifact eval: {artifact_state}."
            )
            print("Semantic judgment pending; model qualification: not-established.")
            return 0 if repaired.termination == "completed" else 1
        if args.command in {"run-understanding-evals", "validate-model-session"}:
            from ai_harness_compiler.model_sessions import (
                IsolatedOllamaExecutor,
                make_plan,
                run_session,
                validate_session,
            )
            from ai_harness_compiler.semantic_eval import FrozenCorpus

            if args.command == "validate-model-session":
                session_report = validate_session(
                    FrozenCorpus(args.corpus), args.input / "session.json"
                )
                print(
                    f"Session journal valid: {session_report.run_status}; "
                    f"eval: {session_report.evaluation_status}"
                )
                return 0
            if args.output.exists():
                raise FileExistsError("SESSION_EXISTS: Choose a new session directory")
            if args.split == "holdout" and not args.allow_holdout:
                raise ValueError("SESSION_HOLDOUT: Explicit opt-in required")
            from ai_harness_compiler.adapters.ollama import OllamaSettings, prompt_digest

            OllamaSettings(model=args.model)
            settings = SessionSettings(
                model=args.model,
                repeats=args.repeats,
                max_attempts=args.max_attempts,
                session_seconds=args.session_seconds,
                call_timeout_seconds=args.timeout_seconds,
                context_tokens=args.context_tokens,
                max_output_tokens=args.max_output_tokens,
                expected_model_sha256=args.expected_model_sha256,
                analysis_mode=args.analysis_mode,
            )
            session_plan = make_plan(
                FrozenCorpus(args.corpus),
                settings,
                prompt_digest(settings.analysis_mode),
                args.case,
                args.split,
                args.candidate_sha256,
            )
            session_report = run_session(session_plan, args.output, IsolatedOllamaExecutor())
            print(
                f"Generation: {session_report.run_status}; "
                f"attempts: {session_report.attempts_used}; "
                f"eval: {session_report.evaluation_status}."
            )
            print("Semantic judgment pending; model qualification: not-established.")
            return (
                0
                if session_report.run_status == "completed"
                and session_report.evaluation_status != "error"
                else 1
            )
        if args.command in {"eval-understanding", "validate-eval-report"}:
            from ai_harness_compiler.semantic_eval import (
                FrozenCorpus,
                assess_artifact,
                bounded_bytes,
                save_report,
            )

            if args.command == "validate-eval-report":
                corpus = FrozenCorpus(args.corpus)
                eval_report = UnderstandingEvalReport.model_validate_json(bounded_bytes(args.input))
                corpus.validate_report(eval_report)
                print(f"Eval report valid against frozen corpus: {eval_report.status}")
                print("Integrity and declared review do not establish reviewer authentication.")
                return 0
            if args.output.exists():
                raise FileExistsError("EVAL_EXISTS: Choose a new output file")
            if args.split == "holdout" and not (args.allow_holdout and args.candidate_sha256):
                raise ValueError(
                    "EVAL_HOLDOUT: Explicit opt-in and frozen candidate digest required"
                )
            corpus = FrozenCorpus(args.corpus)
            eval_report = assess_artifact(
                corpus, args.split, args.case, args.input, args.review, args.candidate_sha256
            )
            save_report(eval_report, args.output)
            print(f"Artifact eval: {eval_report.status}; model qualification: not-established.")
            return 0 if eval_report.status == "pass" else 1
        if args.command == "study":
            from ai_harness_compiler.adapters.ollama import OllamaSettings, OllamaUnderstandingModel
            from ai_harness_compiler.understanding import study_project

            if args.output.exists():
                raise FileExistsError("STUDY_EXISTS: Output exists; choose a new file")
            model = OllamaUnderstandingModel(
                OllamaSettings(
                    model=args.model,
                    timeout_seconds=args.timeout_seconds,
                    max_output_tokens=args.max_output_tokens,
                )
            )
            understanding = study_project(
                load_project(args.input, max_manifest_bytes=args.max_manifest_bytes), model
            )
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json_text(understanding.model_dump()))
            print(f"Understanding proposed: {args.output}; requested Ollama model: {args.model}.")
            print("Human review required; proposal has not been applied to the harness.")
            return 0
        if args.command == "prepare-grounding":
            from ai_harness_compiler.grounding import extract_grounding

            extraction = extract_grounding(
                load_project(args.input, max_manifest_bytes=args.max_manifest_bytes)
            )
            print(json_text(extraction.model_dump()), end="")
            return 0
        if args.command == "verify-grounding":
            from ai_harness_compiler.grounding import verify_quotations
            from ai_harness_compiler.semantic_eval import bounded_bytes

            if args.output.exists():
                raise FileExistsError("GROUNDING_EXISTS: Choose a new output file")
            quotation_spec = ProjectUnderstandingSpec.model_validate_json(bounded_bytes(args.input))
            quotation_report = verify_quotations(quotation_spec)
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json_text(quotation_report.model_dump()))
            quoted = sum(bool(item.quoted_by_rules) for item in quotation_report.criteria)
            print(f"Quoted criteria: {quoted}/{len(quotation_report.criteria)}.")
            print("Semantic coverage and model qualification: not-established.")
            return 0
        if args.command == "prepare-understanding":
            from ai_harness_compiler.understanding import prepare_understanding

            request = prepare_understanding(
                load_project(args.input, max_manifest_bytes=args.max_manifest_bytes)
            )
            print(json_text(request.model_dump()), end="")
            return 0
        if args.command == "validate-understanding":
            if args.max_understanding_bytes <= 0 or args.max_understanding_bytes >= sys.maxsize:
                raise ValueError("UNDERSTANDING_LIMIT: Positive readable byte limit required")
            with args.input.open("rb") as stream:
                content = stream.read(args.max_understanding_bytes + 1)
            if len(content) > args.max_understanding_bytes:
                raise ValueError("UNDERSTANDING_TOO_LARGE: Structured input exceeds byte limit")
            understanding_spec = ProjectUnderstandingSpec.model_validate_json(
                content.decode("utf-8-sig")
            )
            state = understanding_spec.review.decision if understanding_spec.review else "proposed"
            print(
                f"Understanding valid: {understanding_spec.request.original_input.id}; "
                f"review metadata: {state}."
            )
            print("Model execution and reviewer authentication are not established by this check.")
            return 0
        if args.command == "benchmark":
            from ai_harness_compiler.benchmark import run_benchmark

            if args.output.exists():
                raise FileExistsError("BENCHMARK_EXISTS: Report already exists; choose a new file.")
            report = run_benchmark(args.suite, args.workspace, runs=args.runs)
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(json_text(report.model_dump()))
            print(
                f"Compiler benchmark report: {args.output}; SLO not-defined; product evals not-run."
            )
            return 0
        if args.command == "migrate":
            from ai_harness_compiler.migration import migrate_harness

            payload = json.loads(args.input.read_text(encoding="utf-8-sig"))
            if not isinstance(payload, dict):
                raise ValueError("Legacy IR must be a mapping")
            migrated = migrate_harness(payload)
            content = json_text(migrated.model_dump())
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
            print(f"Migrated {payload['schema_version']} to HarnessSpec/v3: {args.output}")
            return 0
        if args.command == "compile":
            content = args.input.read_text(encoding="utf-8-sig")
            if isinstance(legacy := json.loads(content), dict) and legacy.get("schema_version") in (
                "HarnessSpec/v1",
                "HarnessSpec/v2",
            ):
                raise ValueError(
                    "Legacy HarnessSpec requires explicit migration with factory migrate"
                )
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
        if args.command not in {
            "team",
            "study",
            "run-understanding-evals",
            "compare-understanding",
        }:
            raise
        extra = "team" if args.command in {"team", "compare-understanding"} else "understanding"
        print(
            f"factory: install the {extra} extra with uv sync --extra {extra} ({exc.name})",
            file=sys.stderr,
        )
        return 1
