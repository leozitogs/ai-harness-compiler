"""Draft explicit development expectations without modifying or approving the v1 corpus."""

import argparse
import hashlib
import json
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_eval import UnderstandingEvalSuite

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "evals/understanding/v1/development.json"
TARGET = ROOT / "evals/understanding/v2/development-draft"


def draft_cases() -> list[AssessmentCase]:
    suite = UnderstandingEvalSuite.model_validate_json(SOURCE.read_bytes())
    cases = []
    for original in suite.cases:
        obligations = [
            {
                "id": rule.id,
                "source_pointer": rule.source_pointer,
                "quote": rule.quote,
                "disposition": "rule",
            }
            for rule in original.required_rules
        ]
        # Preserve the existing first v2 case identifier for its saved smoke assessment.
        if original.id == "dev-new-domain":
            obligations[0]["id"] = "publication-origin"
        blocked = original.id in {"dev-branding-conflict", "dev-ambiguous"}
        conflicts = []
        if original.id == "dev-branding-conflict":
            conflicts = ["/branding/principles/0", "/backlog/0/acceptance_criteria/0"]
        if original.id == "dev-ambiguous":
            obligations.append(
                {
                    "id": "completion-definition",
                    "source_pointer": "/conception",
                    "quote": original.project.conception,
                    "disposition": "required-question",
                }
            )
        cases.append(
            AssessmentCase.model_validate(
                {
                    "id": original.id,
                    "project": original.project.model_dump(),
                    "expected_behavior": "blocked" if blocked else "ready",
                    "obligations": obligations,
                    "requires_conflict": bool(conflicts),
                    "conflict_source_pointers": conflicts,
                }
            )
        )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    cases = draft_cases()
    approved_count = 0
    expected = {f"{case.id}.json" for case in cases}
    if args.check and {p.name for p in TARGET.glob("*.json")} != expected:
        raise SystemExit("Unexpected or missing draft development cases")
    for case in cases:
        path = TARGET / f"{case.id}.json"
        if args.check and path.exists():
            existing = AssessmentCase.model_validate_json(path.read_bytes())
            case.expectations_approval = existing.expectations_approval
            approved_count += int(existing.expectations_approval is not None)
        content = json_text(case.model_dump())
        if args.check:
            if path.read_text(encoding="utf-8") != content:
                raise SystemExit(f"Stale draft expectations: {path.name}")
        else:
            TARGET.mkdir(exist_ok=True)
            if path.exists():
                existing = AssessmentCase.model_validate_json(path.read_bytes())
                if existing.expectations_approval is not None:
                    raise SystemExit("Do not overwrite approved cases; create a new version")
            path.write_text(content, encoding="utf-8", newline="\n")
    manifest_path = TARGET.parent / "development-approved-manifest.json"
    frozen = False
    if args.check and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        actual = [
            {
                "path": p.relative_to(TARGET.parent).as_posix(),
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            }
            for p in sorted(TARGET.glob("*.json"))
        ]
        rubric_sha = hashlib.sha256((TARGET.parent / "rubric.json").read_bytes()).hexdigest()
        if (
            approved_count != len(cases)
            or manifest.get("cases") != actual
            or manifest.get("rubric_sha256") != rubric_sha
            or manifest.get("scope") != "development-only"
        ):
            raise SystemExit("Frozen development expectations differ from approved manifest")
        frozen = True
    print(
        json.dumps(
            {
                "cases": len(cases),
                "approved_cases": approved_count,
                "expectations": "frozen-development" if frozen else "not-frozen",
                "holdout": "not-read",
                "v1": "unchanged",
            }
        )
    )


if __name__ == "__main__":
    main()
