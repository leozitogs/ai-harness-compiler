"""Prepare a development request offline. This command cannot authorize or run it."""

import argparse
from pathlib import Path

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_eval import UnderstandingRubric
from ai_harness_compiler.models.semantic_flow_v4 import SemanticFlowRequestV4
from ai_harness_compiler.models.semantic_verification_v5 import audit_v5_program_digest
from ai_harness_compiler.models.supervised_transport import TransportLimitsV1
from ai_harness_compiler.semantic_campaign import _bounded_path, prepare_campaign
from ai_harness_compiler.semantic_flow_runner_v4 import _read, _write
from ai_harness_compiler.semantic_generation_v4 import generation_program_v4


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--campaign-id", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--call-seconds", type=int, default=180)
    parser.add_argument("--cleanup-seconds", type=int, default=20)
    parser.add_argument("--session-seconds", type=int, default=3600)
    args = parser.parse_args()
    root = args.repository.resolve()
    if (
        not args.corpus.startswith("evals/")
        or ".." in args.corpus.split("/")
        or "\\" in args.corpus
        or not args.corpus.endswith(".json")
    ):
        raise ValueError("Corpus must be an explicit repository eval JSON file")
    manifest = _read(_bounded_path(root, args.corpus))
    if (
        manifest.get("status") != "expectations-approved"
        or manifest.get("split") != "development"
        or manifest.get("target_analysis") != "SemanticAnalysis/v4"
        or not 1 <= len(manifest.get("cases", [])) <= 8
    ):
        raise ValueError("Only an approved, bounded development corpus can be prepared")
    rubric_source = manifest["rubric_source"]
    if not rubric_source.startswith("evals/") or ".." in rubric_source.split("/"):
        raise ValueError("Rubric must remain an explicit eval source")
    rubric = UnderstandingRubric.model_validate(
        _read(_bounded_path(root, manifest["rubric_source"]))
    )
    flows = []
    for index, entry in enumerate(manifest["cases"], 1):
        name = entry["path"]
        if Path(name).name != name or "\\" in name or not name.endswith(".json"):
            raise ValueError("Case must be a local JSON filename")
        relative = (Path(args.corpus).parent / entry["path"]).as_posix()
        case = AssessmentCaseV3.model_validate(_read(_bounded_path(root, relative)))
        flows.append(
            SemanticFlowRequestV4(
                run_id=f"{args.campaign_id}-{index:02}",
                case=case,
                rubric=rubric,
                requested_model=args.model,
                generation_program_sha256=generation_program_v4(extract_grounding(case.project)),
                audit_program_sha256=audit_v5_program_digest(),
            )
        )
    request = prepare_campaign(
        root,
        campaign_id=args.campaign_id,
        corpus_source=args.corpus,
        flows=flows,
        limits=TransportLimitsV1(
            call_timeout_seconds=args.call_seconds,
            cleanup_timeout_seconds=args.cleanup_seconds,
            session_timeout_seconds=args.session_seconds,
        ),
    )
    target = _bounded_path(root, args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    _write(target, request.model_dump())
    print(
        f"Prepared request {request.sha256}; {len(flows)} cases; maximum {request.max_calls} calls."
    )
    print("No authorization, claim, model invocation, output judgment or qualification.")


if __name__ == "__main__":
    main()
