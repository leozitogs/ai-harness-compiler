"""Inspect explicit local artifacts offline; never execute or contact a model."""

import argparse
from pathlib import Path

from ai_harness_compiler.models.conflict_questions import diagnose_conflict_questions
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.supervised_transport import TransportReceiptV1
from ai_harness_compiler.models.worker_diagnostic import diagnose_worker
from ai_harness_compiler.semantic_campaign import _bounded_path
from ai_harness_compiler.semantic_flow_runner_v4 import _read, _write


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--analysis")
    source.add_argument("--receipt")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = args.repository.resolve()
    if not args.output.startswith(".factory/") or not args.output.endswith(".json"):
        raise ValueError("Diagnostics must remain in an explicit private JSON path")
    output = _bounded_path(root, args.output)
    if not output.resolve().is_relative_to(root / ".factory"):
        raise ValueError("Diagnostic output must resolve inside the private directory")
    if args.analysis:
        result = diagnose_conflict_questions(
            SemanticAnalysisV4.model_validate(_read(_bounded_path(root, args.analysis)))
        )
        status = result.status
    else:
        result = diagnose_worker(
            TransportReceiptV1.model_validate(_read(_bounded_path(root, args.receipt)))
        )
        status = result.category
    # Parent must exist. Exclusive writing preserves every original artifact.
    _write(output, result.model_dump())
    print(f"Offline diagnostic: {status}. No model calls or semantic approval.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit("DIAGNOSTIC_FAILED: no raw input or exception retained") from None
