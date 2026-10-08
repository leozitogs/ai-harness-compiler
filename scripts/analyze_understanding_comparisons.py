"""Recompute preliminary observations from all eight frozen development journals."""

import argparse
import hashlib
from pathlib import Path

from ai_harness_compiler.comparison_runner import validate_development_comparison
from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.model_session import WorkerResult
from ai_harness_compiler.models.semantic_eval import case_checks
from ai_harness_compiler.semantic_eval import FrozenCorpus, bounded_bytes


def summarize(corpus: FrozenCorpus, directory: Path) -> dict[str, object]:
    expected = [case.id for case in corpus.suites["development"].cases]
    if {p.name for p in directory.iterdir()} != set(expected):
        raise ValueError("Exactly the eight development journals are required")
    rows = []
    hashes = {}
    identities: set[str] = set()
    programs: set[tuple[str, str | None, str, str | None]] = set()
    for case_id in expected:
        journal = directory / case_id
        report = validate_development_comparison(corpus, journal)
        case = corpus.case("development", case_id)
        worker = WorkerResult.model_validate_json(bounded_bytes(journal / "local-worker.json"))
        if worker.identity:
            identities.add(worker.identity.compiler_source_sha256)
        left, right = report.candidates
        programs.add(
            (left.requested_model, left.program_sha256, right.requested_model, right.program_sha256)
        )
        candidates = []
        for result in report.candidates:
            checks = (
                case_checks(case, result.compact_analysis.understanding, None)
                if result.compact_analysis
                else []
            )
            candidates.append(
                {
                    "id": result.id,
                    "status": result.status,
                    "error_code": result.error_code,
                    "elapsed_seconds": result.elapsed_seconds,
                    "automatic_failures": [c.criterion for c in checks if c.outcome == "fail"],
                    "artifact_eval_status": "error"
                    if not checks
                    else "fail"
                    if any(c.outcome == "fail" for c in checks)
                    else "not-run",
                    "semantic_review": "pending",
                    "reported_model": result.reported_model,
                }
            )
        rows.append(
            {
                "case": case_id,
                "wall_time_seconds": report.wall_time_seconds,
                "criterion_disagreements": report.criterion_disagreements,
                "unavailable_criteria": report.unavailable_criteria,
                "candidates": candidates,
            }
        )
        for path in sorted(journal.iterdir()):
            hashes[f"{case_id}/{path.name}"] = hashlib.sha256(bounded_bytes(path)).hexdigest()
    if len(identities) != 1 or len(programs) != 1:
        raise ValueError("Observed compiler source or requested programs differ between cases")
    totals = {}
    for id_ in ("local", "cloud"):
        records = [c for row in rows for c in row["candidates"] if c["id"] == id_]
        totals[id_] = {
            "attempts": len(records),
            "completed": sum(c["status"] == "completed" for c in records),
            "artifact_eval_statuses": {
                s: sum(c["artifact_eval_status"] == s for c in records)
                for s in ("error", "fail", "not-run")
            },
            "total_call_seconds": sum(c["elapsed_seconds"] for c in records),
        }
    return {
        "report_kind": "preliminary-development-observations",
        "corpus_sha256": corpus.sha256,
        "repetitions": 1,
        "requested_programs": list(next(iter(programs))),
        "observed_compiler_source_sha256": next(iter(identities)),
        "rows": rows,
        "totals": totals,
        "artifact_sha256": hashes,
        "semantic_status": "not-established",
        "model_qualification": "not-established",
        "limitations": [
            "Synthetic unblinded development; one repetition",
            "No human semantic adjudication or holdout",
            "Concurrent providers and uncontrolled cache",
            "CLI has no observed remote weights hash or effective output-token count",
            "Exact textual disagreement is not semantic disagreement",
            "No causal latency/quality ranking",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = summarize(FrozenCorpus(args.corpus), args.input)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json_text(value))
    print(json_text(value["totals"]), end="")
