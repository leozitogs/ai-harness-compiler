import json
import subprocess
import sys
from pathlib import Path

import pytest

from ai_harness_compiler.functional_changes import assess_functional_change
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.functional_change import (
    FunctionalChangeReviewV1,
    FunctionalChangeV1,
)

ROOT = Path(__file__).resolve().parents[1]


def readiness(*, revision=1, decision="approved", blocked=False, stale=False):
    data = json.loads((ROOT / "examples/functional-change/change.json").read_bytes())
    data["revision"] = revision
    change = FunctionalChangeV1.model_validate(data)
    if not blocked:
        question = change.questions[0]
        data["decisions"] = [
            dict(
                reviewer="synthetic-qa",
                note="Synthetic answer",
                question_id=question.id,
                question_sha256=question.sha256,
                source_sha256=canonical_project_digest(change.source.model_dump()),
                answer="Keep the batch incomplete and record overflow.",
            )
        ]
        change = FunctionalChangeV1.model_validate(data)
    review = FunctionalChangeReviewV1(
        reviewer="synthetic-qa",
        note="Synthetic archive fixture",
        project_id=change.source.original_input.id,
        change_id=change.id,
        revision=revision,
        content_sha256=change.sha256 if not stale else "0" * 64,
        decision=decision,
    )
    return assess_functional_change(change, review)


def plan_command(root, command, *, ok=True):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/plan_functional_tests.py"),
            "--repository",
            str(root),
            "--readiness",
            "readiness.json",
            command,
            "--plan",
            "plan.json",
        ],
        capture_output=True,
        text=True,
        timeout=25,
        check=False,
    )
    if ok:
        assert result.returncode == 0, result.stderr
    else:
        assert result.returncode != 0 and "BUSINESS_TEST_PLAN_FAILED" in result.stderr
    return result


def test_export_preserves_scenarios_and_expected_outcomes_without_executing(tmp_path):
    report = readiness()
    (tmp_path / "readiness.json").write_bytes(report.model_dump_json().encode())
    plan_command(tmp_path, "export")
    plan_path = tmp_path / "plan.json"
    original = plan_path.read_bytes()
    plan = json.loads(original)
    change = report.change
    assert plan["change_sha256"] == change.sha256
    assert plan["scenarios"] == [row.model_dump() for row in change.scenarios]
    assert plan["examples"] == [row.model_dump() for row in change.examples]
    assert plan["requirements"] == [row.model_dump() for row in change.requirements]
    assert plan["questions"] == [row.model_dump() for row in change.questions]
    assert plan["answers"] == [
        {"question_id": row.question_id, "answer": row.answer} for row in change.decisions
    ]
    assert plan["source_pointers"] == [
        {"id": ref.id, "pointer": ref.pointer}
        for ref in change.source.references
        if ref.id in {*change.rules[0].source_refs, *change.questions[0].source_refs}
    ]
    assert plan["test_execution_status"] == "not-run"
    assert "review" not in plan and "original_input" not in plan
    # The fixture locators point to files absent from this target directory.
    assert not (tmp_path / "tests").exists()
    assert "not-run" in plan_command(tmp_path, "verify").stdout
    plan_command(tmp_path, "export", ok=False)
    assert plan_path.read_bytes() == original


@pytest.mark.parametrize("mode", ["blocked", "rejected", "stale", "forged", "unreviewed"])
def test_export_requires_valid_approved_snapshot(tmp_path, mode):
    report = readiness(
        blocked=mode in {"blocked", "forged"},
        stale=mode == "stale",
        decision="rejected" if mode == "rejected" else "approved",
    )
    if mode == "unreviewed":
        report = assess_functional_change(report.change)
    payload = report.model_dump()
    if mode == "forged":
        payload.update(status="approved", blockers=[])
    (tmp_path / "readiness.json").write_text(json.dumps(payload), encoding="utf-8")
    plan_command(tmp_path, "export", ok=False)
    assert not (tmp_path / "plan.json").exists()


def test_verify_detects_modified_outcome_and_plan_from_another_revision(tmp_path):
    report_path = tmp_path / "readiness.json"
    report_path.write_bytes(readiness().model_dump_json().encode())
    plan_command(tmp_path, "export")
    plan_path = tmp_path / "plan.json"
    original = plan_path.read_bytes()
    tampered = json.loads(original)
    tampered["examples"][0]["then"] = "Invented outcome"
    plan_path.write_text(json.dumps(tampered, indent=2) + "\n", encoding="utf-8")
    plan_command(tmp_path, "verify", ok=False)
    plan_path.write_bytes(original)
    report_path.write_bytes(readiness(revision=2).model_dump_json().encode())
    plan_command(tmp_path, "verify", ok=False)
