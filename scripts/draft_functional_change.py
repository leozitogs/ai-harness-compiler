"""Project a reviewed semantic assessment into an offline functional draft."""

import argparse
import json
from pathlib import Path

from inspect_functional_change import MAX_INPUT_BYTES, _path, _read

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.functional_change import FunctionalChangeV1
from ai_harness_compiler.models.semantic_analysis_v3 import BoundFindingV3
from ai_harness_compiler.models.semantic_assessment_v4 import SemanticAssessmentV4


def draft_change(
    assessment: SemanticAssessmentV4,
    expected_assessment: str,
    change_id: str,
    intent: str,
    revision: int,
    capabilities: list[str],
    rule_ids: list[str],
    question_assignments: list[list[str]],
) -> FunctionalChangeV1:
    assessment = SemanticAssessmentV4.model_validate(assessment.model_dump())
    if assessment.status != "pass":
        raise ValueError("Draft requires a passing human assessment")
    if canonical_project_digest(assessment.model_dump()) != expected_assessment:
        raise ValueError("Assessment digest differs from the expected snapshot")
    analysis = assessment.analysis
    if analysis.disposition == "safely-rejected":
        raise ValueError("Rejected project cannot be projected")

    atoms = {a.id: a for a in analysis.extraction.atoms}
    findings = {f.id: f for f in analysis.findings if isinstance(f, BoundFindingV3)}
    questions = {f.id: f for f in findings.values() if f.kind == "question"}
    assignments = {row[0]: (row[1], row[2:]) for row in question_assignments}
    if len(assignments) != len(question_assignments) or assignments.keys() != questions.keys():
        raise ValueError("Each semantic question requires exactly one explicit assignment")
    for conflict in (f for f in findings.values() if f.kind == "conflict"):
        if not any(
            q.impact == "precedence" and set(conflict.source_atom_ids) <= set(q.source_atom_ids)
            for q in questions.values()
        ):
            raise ValueError("Conflict requires a precedence question citing all sides")

    rejected = {a for f in analysis.proposal.content_rejections for a in f.source_atom_ids}
    used: set[str] = set()

    def sources(ids: list[str]) -> list[str]:
        if rejected.intersection(ids):
            raise ValueError("Rejected atom cannot support a functional draft")
        used.update(ids)
        return ids

    rules = []
    for identifier in rule_ids:
        rule = findings.get(identifier)
        if rule is None or rule.kind != "rule":
            raise ValueError("Selected finding must be a business rule")
        parts = [f"Condition: {rule.condition}", f"Outcome: {rule.outcome}"]
        parts.extend(f"Exception: {value}" for value in rule.exceptions)
        targets = rule.guard_target_atom_ids
        if rule.guard_target_scope == "project":
            parts.append("Scope: project")
        elif targets:
            parts.append("Scope: " + "; ".join(atoms[id_].quote for id_ in targets))
        rules.append(
            dict(
                id=identifier,
                origin="hypothesis",
                statement="\n".join(parts),
                source_refs=sources(list(dict.fromkeys(rule.source_atom_ids + targets))),
            )
        )

    pending = []
    for identifier, question in questions.items():
        owner, linked = assignments[identifier]
        pending.append(
            dict(
                id=identifier,
                text=question.text,
                owner=owner,
                impact=question.impact,
                rule_ids=linked,
                source_refs=sources(question.source_atom_ids),
            )
        )
    original = analysis.extraction.request
    return FunctionalChangeV1.model_validate(
        dict(
            id=change_id,
            revision=revision,
            capability_ids=capabilities,
            intent=intent,
            rules=rules,
            questions=pending,
            source=original.model_dump()
            | dict(
                references=[
                    dict(
                        id=atom.id,
                        project_id=original.original_input.id,
                        pointer=atom.pointer,
                        value=atom.quote,
                    )
                    for atom in atoms.values()
                    if atom.id in used
                ],
            ),
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--assessment", required=True)
    parser.add_argument("--expected-assessment", required=True)
    parser.add_argument("--change-id", required=True)
    parser.add_argument("--intent", required=True)
    parser.add_argument("--revision", type=int, default=1)
    parser.add_argument("--capability", action="append", required=True)
    parser.add_argument("--rule", action="append", required=True)
    parser.add_argument("--question", action="append", nargs="+", default=[])
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = args.repository.resolve()
    if any(len(row) < 3 for row in args.question):
        raise ValueError("Question requires ID, owner and at least one rule ID")
    assessment = SemanticAssessmentV4.model_validate(_read(_path(root, args.assessment)))
    change = draft_change(
        assessment,
        args.expected_assessment,
        args.change_id,
        args.intent,
        args.revision,
        args.capability,
        args.rule,
        args.question,
    )
    encoded = change.model_dump_json().encode("utf-8")
    if len(encoded) > MAX_INPUT_BYTES:
        raise ValueError("Draft exceeds offline input limit")
    with _path(root, args.output).open("xb") as stream:
        stream.write(encoded)
    print(json.dumps(dict(assessment_sha256=args.expected_assessment, change_sha256=change.sha256)))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RecursionError):
        raise SystemExit(
            "FUNCTIONAL_DRAFT_FAILED: invalid review, digest, selection, scope or output"
        ) from None
