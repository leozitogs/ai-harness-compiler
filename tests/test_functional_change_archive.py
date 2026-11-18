import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from ai_harness_compiler.models.functional_change import FunctionalChangeV1

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/archive_functional_change.py"
FIXTURE = ROOT / "examples/functional-change/change.json"


@pytest.fixture
def archive(tmp_path):
    (tmp_path / "archive").mkdir()

    def write(name, payload):
        (tmp_path / name).write_text(json.dumps(payload), encoding="utf-8")

    def run(*args, ok=True):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--repository",
                str(tmp_path),
                "--archive",
                "archive",
                *args,
            ],
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )
        if ok:
            assert result.returncode == 0, result.stderr
        else:
            assert result.returncode != 0
            assert "FUNCTIONAL_ARCHIVE_FAILED" in result.stderr
        return result.stdout.strip()

    return run, write


def _change(**updates):
    return json.loads(FIXTURE.read_bytes()) | updates


def _review(change, decision="approved"):
    model = FunctionalChangeV1.model_validate(change)
    return dict(
        reviewer="synthetic-reviewer",
        note="Synthetic review for the archive test.",
        project_id=model.source.original_input.id,
        change_id=model.id,
        revision=model.revision,
        content_sha256=model.sha256,
        decision=decision,
    )


def test_history_preserves_previous_acceptance_and_requires_new_review(archive):
    run, write = archive
    first = _change(questions=[])
    write("first.json", first)
    old_digest = run("append", "--input", "first.json", "--expected-head", "empty")
    old_review = _review(first)
    write("review.json", old_review)
    assert run("review", "--input", "review.json") == "approved"
    run("review", "--input", "review.json", ok=False)

    new = _change(revision=2, questions=[], intent="Investigate cases with five entries.")
    write("new.json", new)
    run("append", "--input", "new.json", "--expected-head", "empty", ok=False)
    new_digest = run("append", "--input", "new.json", "--expected-head", old_digest)
    write("review.json", old_review | dict(revision=2))
    run("review", "--input", "review.json", ok=False)
    assert json.loads(run("history")) == [
        dict(revision=1, sha256=old_digest),
        dict(revision=2, sha256=new_digest),
    ]
    assert json.loads(run("show", "--revision", "1"))["status"] == "approved"
    current = json.loads(run("show"))
    assert current["status"] == "ready-for-human-review" and current["review"] is None
    assert current["test_execution_status"] == "not-run"


def test_blocked_revision_refuses_approval_and_records_rejection(archive):
    run, write = archive
    change = _change()
    write("change.json", change)
    run("append", "--input", "change.json", "--expected-head", "empty")
    write("review.json", _review(change))
    run("review", "--input", "review.json", ok=False)
    write("review.json", _review(change, "rejected"))
    assert run("review", "--input", "review.json") == "rejected"
    report = json.loads(run("show"))
    assert report["status"] == "blocked"
    assert report["review"]["decision"] == "rejected"


def test_archive_detects_content_tampering(archive, tmp_path):
    run, write = archive
    write("change.json", _change())
    run("append", "--input", "change.json", "--expected-head", "empty")
    path = tmp_path / "archive/revision-000000000001.json"
    entry = json.loads(path.read_bytes())
    entry["change"]["intent"] = "Changed without a new entry."
    path.write_text(json.dumps(entry), encoding="utf-8")
    run("history", ok=False)


def test_archive_detects_wrong_parent_even_with_intact_content(archive, tmp_path):
    run, write = archive
    write("change.json", _change())
    head = run("append", "--input", "change.json", "--expected-head", "empty")
    write("change.json", _change(revision=2))
    run("append", "--input", "change.json", "--expected-head", head)
    path = tmp_path / "archive/revision-000000000002.json"
    entry = json.loads(path.read_bytes()) | dict(parent_sha256="0" * 64)
    path.write_text(json.dumps(entry), encoding="utf-8")
    run("show", "--revision", "1", ok=False)


def test_archive_rejects_skipped_revision_and_foreign_change(archive):
    run, write = archive
    write("change.json", _change())
    head = run("append", "--input", "change.json", "--expected-head", "empty")
    for change in [_change(revision=3), _change(revision=2, id="other-change")]:
        write("change.json", change)
        run("append", "--input", "change.json", "--expected-head", head, ok=False)
    assert len(json.loads(run("history"))) == 1


def test_competing_writers_cannot_replace_one_another(archive, tmp_path):
    run, write = archive
    for name in ("first", "second"):
        write(f"{name}.json", _change(intent=f"Intent from {name}."))
    with ThreadPoolExecutor(max_workers=2) as pool:
        calls = [
            pool.submit(
                subprocess.run,
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repository",
                    str(tmp_path),
                    "--archive",
                    "archive",
                    "append",
                    "--input",
                    f"{name}.json",
                    "--expected-head",
                    "empty",
                ],
                capture_output=True,
                timeout=25,
                check=False,
            )
            for name in ("first", "second")
        ]
    results = [call.result() for call in calls]
    assert sorted(result.returncode for result in results) == [0, 1]
    winner = next(result for result in results if result.returncode == 0)
    assert json.loads(run("history")) == [dict(revision=1, sha256=winner.stdout.decode().strip())]
    assert len(list((tmp_path / "archive").iterdir())) == 1
