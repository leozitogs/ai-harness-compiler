import json
import subprocess
import sys
from pathlib import Path

import pytest
from test_semantic_assessment import declaration, rubric
from test_semantic_contract_v4 import add_rejection, development
from test_semantic_flow_v4 import human_review

from ai_harness_compiler.functional_changes import assess_functional_change
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.functional_change import FunctionalChangeV1
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.semantic_assessment_v4 import assess_v4
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3

ROOT = Path(__file__).resolve().parents[1]


def assessment(disposition="blocked", *, reviewed=True, rejected_source=False, conflict=False):
    _, _, case, analysis = development()
    source = next(a for a in analysis.extraction.atoms if a.pointer == "/conception")
    criterion = next(a for a in analysis.extraction.atoms if a.kind == "acceptance-criterion")
    proposal = analysis.model_dump()
    base = proposal["proposal"]["project_analysis"]
    base["criteria"][0] = dict(
        source_atom_id=criterion.id,
        kind="business-rule",
        condition=dict(text="When requested", source_atom_ids=[criterion.id]),
        outcome=dict(text="Show the synthetic label", source_atom_ids=[criterion.id]),
        exceptions=[dict(text="During recovery", source_atom_ids=[criterion.id])],
        note="Synthetic",
    )
    positions = {a.id: i for i, a in enumerate(compact_context(analysis.extraction))}
    if disposition == "blocked":
        base["issues"] = [
            dict(
                kind="question",
                text="What completes the display?",
                impact="outcome",
                context_indices=[positions[criterion.id]],
                rationale="Synthetic",
            )
        ]
    elif disposition == "safely-rejected":
        base["issues"] = [
            dict(
                kind="safe-rejection",
                text="Required source unavailable",
                rejection_reason="unread-required-source",
                context_indices=[positions[source.id]],
                rationale="Synthetic",
            )
        ]
    if conflict:
        base["issues"].append(
            dict(
                kind="conflict",
                text="Synthetic conflict",
                context_indices=[positions[criterion.id], positions[source.id]],
                rationale="Synthetic",
            )
        )
    analysis = SemanticAnalysisV4.model_validate(proposal)
    if rejected_source:
        data = add_rejection(analysis).model_dump()
        data["proposal"]["content_rejections"][0]["content"]["source_atom_ids"] = [criterion.id]
        analysis = SemanticAnalysisV4.model_validate(data)
    updated_case = case.model_dump() | dict(
        expected_behavior=disposition,
        expectations_approval=declaration().model_dump(),
    )
    if disposition == "blocked":
        updated_case["obligations"].append(
            dict(
                id="material-question",
                source_pointer=criterion.pointer,
                quote=criterion.quote,
                disposition="required-question",
            )
        )
    if disposition == "safely-rejected":
        updated_case["required_project_rejection_pointers"] = [source.pointer]
    case = AssessmentCaseV3.model_validate(updated_case)
    rubric_ = rubric()
    review = human_review(case, rubric_, analysis) if reviewed else None
    if review and disposition == "blocked":
        review.coverage = [
            *review.coverage,
            type(review.coverage[0])(obligation_id="material-question", finding_id="issue-1"),
        ]
    return assess_v4(case, rubric_, analysis, review)


def run(tmp_path, snapshot, *, assignments=(), override=None, ok=True):
    payload = snapshot.model_dump()
    (tmp_path / "assessment.json").write_text(json.dumps(payload), encoding="utf-8")
    digest = canonical_project_digest(payload)
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/draft_functional_change.py"),
            "--repository",
            str(tmp_path),
            "--assessment",
            "assessment.json",
            "--expected-assessment",
            override or digest,
            "--change-id",
            "test-draft",
            "--intent",
            "Clarify display requirements",
            "--capability",
            "store-record",
            "--rule",
            "criterion-1",
            "--output",
            "draft.json",
            *assignments,
        ],
        capture_output=True,
        text=True,
        timeout=35,
        check=False,
    )
    if ok:
        assert result.returncode == 0, result.stderr
        draft = FunctionalChangeV1.model_validate_json((tmp_path / "draft.json").read_bytes())
        assert json.loads(result.stdout) == dict(
            assessment_sha256=digest, change_sha256=draft.sha256
        )
        return draft
    assert result.returncode != 0 and "FUNCTIONAL_DRAFT_FAILED" in result.stderr
    assert not (tmp_path / "draft.json").exists()
    return None


def test_reviewed_analysis_produces_hypothesis_and_preserves_exact_open_question(tmp_path):
    snapshot = assessment()
    assert snapshot.status == "pass"
    draft = run(
        tmp_path,
        snapshot,
        assignments=["--question", "issue-1", "product-owner", "criterion-1"],
    )
    assert draft.rules[0].origin == "hypothesis"
    assert draft.confirmations == draft.decisions == []
    assert "During recovery" in draft.rules[0].statement
    assert draft.questions[0].text == "What completes the display?"
    assert draft.questions[0].impact == "outcome" and draft.questions[0].owner == "product-owner"
    assert draft.source.references[0].pointer == "/backlog/0/acceptance_criteria/0"
    report = assess_functional_change(draft)
    assert report.status == "blocked"
    assert "unresolved-question" in {blocker.code for blocker in report.blockers}
    (tmp_path / "archive").mkdir()
    stored = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/archive_functional_change.py"),
            "--repository",
            str(tmp_path),
            "--archive",
            "archive",
            "append",
            "--input",
            "draft.json",
            "--expected-head",
            "empty",
        ],
        capture_output=True,
        text=True,
        timeout=35,
        check=False,
    )
    assert stored.returncode == 0, stored.stderr
    assert stored.stdout.strip() == draft.sha256


@pytest.mark.parametrize(
    "failure", ["unreviewed", "digest", "missing-owner", "rejected-source", "conflict", "rejection"]
)
def test_refuses_unreviewed_mismatched_or_lossy_projection(tmp_path, failure):
    disposition = "ready" if failure == "rejected-source" else "blocked"
    if failure == "rejection":
        disposition = "safely-rejected"
    snapshot = assessment(
        disposition,
        reviewed=failure != "unreviewed",
        rejected_source=failure == "rejected-source",
        conflict=failure == "conflict",
    )
    assert snapshot.status == ("not-run" if failure == "unreviewed" else "pass")
    assignments = (
        ["--question", "issue-1", "product-owner", "criterion-1"]
        if disposition == "blocked" and failure != "missing-owner"
        else []
    )
    run(
        tmp_path,
        snapshot,
        assignments=assignments,
        override="0" * 64 if failure == "digest" else None,
        ok=False,
    )
