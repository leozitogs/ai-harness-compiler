"""Versioned opt-in semantic commands; saved human assessment remains offline."""

import argparse
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.intake import load_project
from ai_harness_compiler.model_policy import load_model_policy
from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.semantic_analysis import SemanticAnalysis
from ai_harness_compiler.models.semantic_assessment import (
    AssessmentCase,
    SemanticHumanReview,
    assess,
)
from ai_harness_compiler.models.semantic_eval import UnderstandingRubric


def read_contract[T: Contract](path: Path, model: type[T]) -> T:
    with path.open("rb") as stream:
        data = stream.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024:
        raise ValueError("SEMANTIC_INPUT_LIMIT: Artifact exceeds 4 MiB")
    return model.model_validate_json(data)


def execute(args: argparse.Namespace) -> int:
    if args.output.exists():
        raise FileExistsError("SEMANTIC_EXISTS: Choose a new output file")
    artifact: Contract
    if args.command == "assess-analysis-v2":
        assessment = assess(
            read_contract(args.case, AssessmentCase),
            read_contract(args.rubric, UnderstandingRubric),
            read_contract(args.input, SemanticAnalysis),
            read_contract(args.review, SemanticHumanReview) if args.review else None,
        )
        artifact = assessment
        exit_code = 0 if assessment.status == "pass" else 1
    else:
        from ai_harness_compiler.adapters.codex_cli import CodexCLISettings, CodexCompactModel
        from ai_harness_compiler.semantic_verification import analyze, verify

        policy = load_model_policy(args.model_policy)
        if policy.primary.provider != "codex-cli":
            raise ValueError("SEMANTIC_PROVIDER: V2 currently requires explicit Codex CLI policy")
        model_name = args.model if args.model is not None else policy.primary.model
        generator = CodexCompactModel(CodexCLISettings(model_name, args.timeout_seconds))
        if args.command == "analyze-project-v2":
            artifact = analyze(extract_grounding(load_project(args.input)), generator)
        else:
            artifact = verify(read_contract(args.input, SemanticAnalysis), generator, model_name)
        exit_code = 0
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json_text(artifact.model_dump()))
    print(f"Saved: {args.output}; compilation not authorized; model qualification not established.")
    return exit_code
