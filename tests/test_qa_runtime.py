"""Trusted-root capture and runner budgets; no paid/network calls in tests."""

import json
import subprocess
import sys
from datetime import timedelta

import pytest
from test_scrum_collection import REPO, repository

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.qa import QAInspection, QAReviewReport
from ai_harness_compiler.models.scrum import instant
from ai_harness_compiler.models.team import POReview, TeamConfig
from ai_harness_compiler.qa import project_for, review_report
from ai_harness_compiler.qa_collection import assert_current_request, bounded_process, capture
from ai_harness_compiler.qa_runner import run_checks
from ai_harness_compiler.scrum_collection import collect, timestamp
from ai_harness_compiler.scrum_observer import observe


def git(root, *args):
    result = subprocess.run(["git", *args], cwd=root, capture_output=True, check=True)
    return result.stdout.decode().strip()


def repo_request(tmp_path):
    root = repository(tmp_path / "repo")
    (root / "src").mkdir()
    (root / "src/approval.py").write_text(
        "def authorize(approved):\n    return True\n", encoding="utf-8", newline="\n"
    )
    (root / ".gitignore").write_text(".factory/\n", newline="\n")
    git(root, "init")
    git(root, "config", "user.name", "QA Fixture")
    git(root, "config", "user.email", "fixture@example.invalid")
    git(root, "config", "core.autocrlf", "false")
    git(root, "add", ".")
    git(root, "commit", "-m", "fixture")
    head = git(root, "rev-parse", "HEAD")
    snapshot = observe(collect(root, "demo", REPO, "sprint-2-5"))
    return root, capture(
        root, snapshot, head, head, "engineer", ["src/approval.py"], check_ids=["tests"]
    )


def test_capture_and_default_runner_never_execute_project_code(tmp_path, monkeypatch):
    root, req = repo_request(tmp_path)
    monkeypatch.setattr(
        "ai_harness_compiler.qa_runner.bounded_process", lambda *args: pytest.fail("Executed")
    )
    checks = run_checks(req, root)
    assert len(checks) == 1 and checks[0].status == "not-run"
    assert checks[0].exit_code is None


@pytest.mark.parametrize(
    "termination,code,status",
    [
        ("completed", 0, "passed"),
        ("completed", 1, "failed"),
        ("timed-out", -1, "timed-out"),
        ("output-limit", -1, "output-limit"),
    ],
)
def test_runner_uses_fixed_commands_and_records_actual_outcome(
    tmp_path, monkeypatch, termination, code, status
):
    root, req = repo_request(tmp_path)
    calls = []

    def fixed(command, cwd, timeout, limit):
        calls.append((command, cwd, timeout, limit))
        return code, "Observed output", termination

    monkeypatch.setattr("ai_harness_compiler.qa_runner.bounded_process", fixed)
    results = run_checks(req, root, req.head_commit)
    assert results[0].status == status
    assert calls[0][0] == [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
    assert calls[0][2] <= req.check_timeout_seconds and calls[0][3] == 32768


def test_wrong_trusted_revision_cannot_execute(tmp_path, monkeypatch):
    root, req = repo_request(tmp_path)
    monkeypatch.setattr(
        "ai_harness_compiler.qa_runner.bounded_process", lambda *args: pytest.fail("Executed")
    )
    with pytest.raises(ValueError, match="Trusted"):
        run_checks(req, root, "a" * 40)


def test_total_budget_exhausted_by_guard_does_not_start_a_check(tmp_path, monkeypatch):
    root, req = repo_request(tmp_path)
    times = iter([0, 0, 301])
    monkeypatch.setattr("ai_harness_compiler.qa_runner.monotonic", lambda: next(times))
    monkeypatch.setattr(
        "ai_harness_compiler.qa_runner.bounded_process", lambda *args: pytest.fail("Executed")
    )
    assert run_checks(req, root, req.head_commit)[0].status == "not-run"


def test_model_failure_is_recorded_without_fallback_or_false_zero_calls(tmp_path, monkeypatch):
    import httpx

    root, req = repo_request(tmp_path)
    path = tmp_path / "request.json"
    path.write_text(req.model_dump_json(), encoding="utf-8")

    def unavailable(*args):
        raise httpx.ConnectError("PRIVATE provider detail")

    monkeypatch.setattr("ai_harness_compiler.adapters.qa_inspection.inspect", unavailable)
    output = tmp_path / "model-failed"
    assert (
        main(
            [
                "qa",
                "run",
                str(path),
                "--repository",
                str(root),
                "--output",
                str(output),
                "--engine",
                "codex-cli",
                "--model",
                "fixture-model",
            ]
        )
        == 0
    )
    report = QAReviewReport.model_validate_json((output / "qa-report.json").read_bytes())
    assert report.engine == "codex-cli" and report.inspection_status == "rejected"
    assert report.model_attempts == 1 and report.model_calls is None
    assert report.recommendation == "inconclusive"
    assert "PRIVATE" not in report.model_dump_json()


def test_changed_source_or_new_commit_invalidates_review(tmp_path):
    root, req = repo_request(tmp_path)
    path = root / "src/approval.py"
    path.write_text("changed\n")
    with pytest.raises(ValueError, match="clean"):
        assert_current_request(req, root, timestamp())
    git(root, "add", ".")
    git(root, "commit", "-m", "change")
    with pytest.raises(ValueError, match="head changed"):
        assert_current_request(req, root, timestamp())


def test_expired_request_is_not_reusable(tmp_path):
    root, req = repo_request(tmp_path)
    later = (instant(req.captured_at) + timedelta(hours=2)).isoformat()
    with pytest.raises(ValueError):
        assert_current_request(req, root, later)


def test_forged_capture_cannot_match_a_different_git_revision(tmp_path):
    root, req = repo_request(tmp_path)
    data = req.model_dump()
    data["base_commit"] = "c" * 40
    from ai_harness_compiler.models.qa import QAReviewRequest

    with pytest.raises(ValueError):
        assert_current_request(QAReviewRequest.model_validate(data), root, timestamp())
    # A caller cannot use an expression as a commit or escape through a path.
    with pytest.raises(ValueError):
        capture(root, req.snapshot, "HEAD", req.head_commit, "engineer", ["src/approval.py"])
    with pytest.raises(ValueError):
        capture(root, req.snapshot, req.base_commit, req.head_commit, "engineer", ["../secret.py"])


def test_bounded_process_limits_output_and_time(tmp_path):
    code, output, status = bounded_process(
        [sys.executable, "-c", "print('x' * 100000)"], tmp_path, 10, 1024
    )
    assert status == "output-limit" and len(output.encode()) <= 1024
    code, output, status = bounded_process(
        [sys.executable, "-c", "import time; time.sleep(30)"], tmp_path, 0.1, 1024
    )
    assert status == "timed-out"


def test_cli_capture_run_and_assess_are_functional_without_model(tmp_path, capsys):
    root, req = repo_request(tmp_path)
    snapshot, request_path = tmp_path / "snapshot.json", tmp_path / "request.json"
    snapshot.write_text(req.snapshot.model_dump_json(), encoding="utf-8")
    assert (
        main(
            [
                "qa",
                "capture",
                "--repository",
                str(root),
                "--snapshot",
                str(snapshot),
                "--base",
                req.base_commit,
                "--head",
                req.head_commit,
                "--author",
                "engineer",
                "--source",
                "src/approval.py",
                "--checks",
                "tests",
                "--output",
                str(request_path),
            ]
        )
        == 0
    )
    output = tmp_path / "review"
    args = ["qa", "run", str(request_path), "--repository", str(root), "--output", str(output)]
    assert main(args) == 0
    report = QAReviewReport.model_validate_json((output / "qa-report.json").read_bytes())
    assert report.recommendation == "inconclusive" and report.checks[0].status == "not-run"
    assert main(args) == 1
    assessment = tmp_path / "closure.json"
    assert (
        main(
            [
                "qa",
                "assess",
                str(output / "qa-report.json"),
                "--repository",
                str(root),
                "--output",
                str(assessment),
            ]
        )
        == 0
    )
    assert json.loads(assessment.read_text())["sprint_closed"] is False


def test_vera_and_nexo_run_in_langgraph_and_pause_for_po(tmp_path):
    from ai_harness_compiler.team.runtime import prepare_team, review_team

    root, req = repo_request(tmp_path)
    report = review_report(
        req, QAInspection(limitations=["Unknown business coverage"]), run_checks(req, root)
    )
    config = TeamConfig(
        project=project_for(req),
        selected=[s.id for s in req.snapshot.stories],
        request="Review QA",
        mode="ask",
        repository_root=str(root),
        scrum_snapshot=req.snapshot,
        qa_report=report,
    )
    output = tmp_path / "team"
    assert prepare_team(config, output)["status"] == "awaiting_po"
    data = json.loads((output / "team-report.json").read_text(encoding="utf-8"))
    assert {r["agent_id"] for r in data["reports"]} == {"quality", "delivery"}
    nexo = next(r for r in data["reports"] if r["agent_id"] == "delivery")
    assert nexo["observations"][-1]["data"]["closure_assessment"]["sprint_closed"] is False
    assert (
        review_team(output, POReview(decision="approve", comment="Report only"))["sprint_started"]
        is False
    )


def test_changed_qa_report_metadata_is_bound_to_checkpoint(tmp_path):
    from ai_harness_compiler.team.runtime import prepare_team, review_team

    root, req = repo_request(tmp_path)
    report = review_report(req, QAInspection(limitations=["Unknown"]), run_checks(req, root))
    config = TeamConfig(
        project=project_for(req),
        selected=[s.id for s in req.snapshot.stories],
        request="Review",
        mode="ask",
        repository_root=str(root),
        scrum_snapshot=req.snapshot,
        qa_report=report,
    )
    output = tmp_path / "team"
    prepare_team(config, output)
    path = output / "run.json"
    data = json.loads(path.read_text())
    data["config"]["qa_report"]["inspection"]["limitations"] = ["Changed metadata"]
    path.write_text(json.dumps(data))
    with pytest.raises(ValueError, match="context changed"):
        review_team(output, POReview(decision="approve", comment="Must reject"))
