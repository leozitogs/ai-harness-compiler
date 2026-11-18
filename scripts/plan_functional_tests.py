"""Export or verify a business test plan derived from reviewed functional readiness."""

import argparse
import json
from pathlib import Path

from inspect_functional_change import _path

from ai_harness_compiler.functional_changes import FunctionalReadinessV1
from ai_harness_compiler.models.evidence import canonical_project_digest

# Archive show may escape non-ASCII text, so its JSON can exceed the inspection report limit.
MAX_DOCUMENT_BYTES = 8 * 1024 * 1024


def _read_document(path: Path) -> bytes:
    if not path.is_file():
        raise ValueError("Document must be a regular file")
    with path.open("rb") as stream:
        data = stream.read(MAX_DOCUMENT_BYTES + 1)
    if len(data) > MAX_DOCUMENT_BYTES:
        raise ValueError("Document exceeds byte limit")
    return data


def build_plan(report: FunctionalReadinessV1) -> bytes:
    report = FunctionalReadinessV1.model_validate(report.model_dump())
    if report.status != "approved" or report.review is None:
        raise ValueError("Test plan requires an exact approved functional revision")
    change = report.change
    source_ids = {ref for item in [*change.rules, *change.questions] for ref in item.source_refs}
    plan = {
        "format": "FunctionalBusinessTestPlan/v1",
        "project_id": change.source.original_input.id,
        "change_id": change.id,
        "revision": change.revision,
        "change_sha256": change.sha256,
        "readiness_sha256": canonical_project_digest(report.model_dump()),
        "review_sha256": canonical_project_digest(report.review.model_dump()),
        "test_execution_status": report.test_execution_status,
        "source_pointers": [
            {"id": ref.id, "pointer": ref.pointer}
            for ref in change.source.references
            if ref.id in source_ids
        ],
        "rules": [rule.model_dump(mode="json") for rule in change.rules],
        "requirements": [
            requirement.model_dump(mode="json") for requirement in change.requirements
        ],
        "examples": [example.model_dump(mode="json") for example in change.examples],
        "exemptions": [exemption.model_dump(mode="json") for exemption in change.exemptions],
        "questions": [question.model_dump(mode="json") for question in change.questions],
        "answers": [
            {"question_id": decision.question_id, "answer": decision.answer}
            for decision in change.decisions
        ],
        "scenarios": [scenario.model_dump(mode="json") for scenario in change.scenarios],
    }
    payload = (json.dumps(plan, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if len(payload) > MAX_DOCUMENT_BYTES:
        raise ValueError("Test plan exceeds byte limit")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--readiness", required=True)
    parser.add_argument("command", choices=["export", "verify"])
    parser.add_argument("--plan", required=True)
    args = parser.parse_args()
    root = args.repository.resolve()
    report = FunctionalReadinessV1.model_validate_json(_read_document(_path(root, args.readiness)))
    plan = build_plan(report)
    target = _path(root, args.plan)
    if args.command == "verify":
        if _read_document(target) != plan:
            raise ValueError("Plan differs from the approved revision")
        print("Business test plan verified; test execution: not-run.")
        return

    with target.open("xb") as stream:
        stream.write(plan)
    print(f"Business test plan exported for {len(report.change.scenarios)} scenarios.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RecursionError):
        raise SystemExit(
            "BUSINESS_TEST_PLAN_FAILED: invalid approval, plan mismatch or storage error"
        ) from None
