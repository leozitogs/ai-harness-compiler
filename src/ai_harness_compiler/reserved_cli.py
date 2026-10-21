"""Explicit CLI boundary; preparing metadata never opens reserved payloads."""

from __future__ import annotations

import argparse
from pathlib import Path

from ai_harness_compiler.models.reserved_run import (
    ReservedRunAuthorization,
    ReservedRunRequest,
    assess_reserved,
)
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_assessment_v3 import SemanticHumanReviewV3
from ai_harness_compiler.models.semantic_eval import UnderstandingRubric
from ai_harness_compiler.reserved_runs import (
    bounded_read,
    run_reserved,
    safe_path,
    validate_reserved_run,
    verify_frozen_sources,
    write_new,
)


def add_commands(commands: argparse._SubParsersAction[argparse.ArgumentParser]) -> None:
    for name, help_text in (
        ("prepare-reserved-run", "Validate a concrete request; no payload reads or model calls"),
        ("run-reserved-evaluation", "Read/run only an exactly authorized private reserved request"),
    ):
        action = commands.add_parser(name, help=help_text)
        action.add_argument("input", type=Path)
        action.add_argument("--repository", type=Path, default=Path.cwd())
        if name == "prepare-reserved-run":
            action.add_argument("--output", type=Path, required=True)
        else:
            action.add_argument("--authorization", type=Path, required=True)
    validate = commands.add_parser("validate-reserved-run", help="Offline private run integrity")
    validate.add_argument("input", type=Path)
    validate.add_argument("--repository", type=Path, default=Path.cwd())
    assess = commands.add_parser(
        "assess-reserved-analysis", help="Human assessment with external expectations approval"
    )
    assess.add_argument("input", type=Path, help="Private completed/stopped run directory")
    assess.add_argument("--repository", type=Path, default=Path.cwd())
    assess.add_argument("--case-id", required=True)
    assess.add_argument("--repetition", type=int, default=1)
    assess.add_argument("--review", type=Path)
    assess.add_argument("--output", type=Path, required=True)


def execute(args: argparse.Namespace) -> int:
    if args.command in {"validate-reserved-run", "assess-reserved-analysis"}:
        report = validate_reserved_run(args.repository, args.input)
        if args.command == "validate-reserved-run":
            print("Reserved run integrity verified; semantic quality not established.")
            return 0
        root, request = args.repository.resolve(), report.request
        output = args.output.resolve()
        if not output.is_relative_to(args.input.resolve()):
            raise ValueError("RESERVED_ASSESSMENT_MUST_REMAIN_PRIVATE")
        safe_path(root, output.relative_to(root).as_posix())
        match = next(
            (
                i
                for i, job in enumerate(report.jobs, 1)
                if (
                    job.case_id == args.case_id
                    and job.repetition == args.repetition
                    and job.stage == "analysis"
                    and job.state == "completed"
                )
            ),
            None,
        )
        if match is None:
            raise ValueError("RESERVED_COMPLETED_ANALYSIS_REQUIRED")
        folder = safe_path(root, request.output_path)
        case = AssessmentCase.model_validate_json(
            bounded_read(safe_path(root, f"{request.output_path}/cases/{args.case_id}.json"))
        )
        rubric_raw = bounded_read(folder / "rubric.json")
        analysis = SemanticAnalysisV3.model_validate_json(
            bounded_read(folder / f"job-{match:03}/artifact.json")
        )
        review = (
            SemanticHumanReviewV3.model_validate_json(bounded_read(args.review))
            if args.review
            else None
        )
        assessment = assess_reserved(
            request.protocol,
            case,
            UnderstandingRubric.model_validate_json(rubric_raw),
            analysis,
            rubric_raw,
            review,
        )
        write_new(output, assessment.model_dump())
        print(f"Reserved analysis assessment: {assessment.status}; qualification not established.")
        return 0 if assessment.status == "pass" else 1
    request = ReservedRunRequest.model_validate_json(bounded_read(args.input))
    if args.command == "prepare-reserved-run":
        verify_frozen_sources(args.repository.resolve(), request)
        write_new(
            args.output,
            {
                "format": "reserved-run-preparation/v1",
                "request_sha256": request.sha256,
                "state": "awaiting-explicit-human-execution-authorization",
                "payload_validation": "not-performed",
                "execution_authorized": False,
                "model_calls": 0,
            },
        )
        print("Reserved run request prepared; payloads unopened; execution not authorized.")
        return 0
    authorization = ReservedRunAuthorization.model_validate_json(bounded_read(args.authorization))
    report = run_reserved(args.repository, request, authorization)
    print(f"Reserved run: {report.state}; human output review and qualification remain separate.")
    return 0 if report.state == "completed" else 1
