"""Crash boundaries and explicit authority, exercised without network or models."""

import json
import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta

import pytest
from pydantic import ValidationError
from test_scrum_planning import config_for

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.scrum import instant
from ai_harness_compiler.models.scrum_operations import (
    OperationAuthorization,
    RemoteIssueState,
    ScrumOperationPlan,
)
from ai_harness_compiler.scrum_collection import timestamp
from ai_harness_compiler.scrum_operations import OperationJournal, OperationRunner
from ai_harness_compiler.scrum_planning import propose


class SimulatedCrash(BaseException):
    pass


class FakeAdapter:
    def __init__(self, plan, clock=timestamp):
        self.remote = plan.expected.model_copy(deep=True)
        self.clock = clock
        self.reads = self.writes = self.dispatches = 0
        self.failure = None
        self.on_preflight = None
        self.on_write = None

    def read_issue(self, repository, number, timeout_seconds):
        assert timeout_seconds == 10
        self.reads += 1
        if self.reads == 1 and self.on_preflight:
            self.on_preflight()
        if self.failure == "read" or (self.reads > 1 and self.failure == "post-read"):
            raise TimeoutError("PRIVATE provider failure detail")
        return self.remote.model_copy(update={"observed_at": self.clock()})

    def add_label(self, plan, timeout_seconds, before_write):
        self.dispatches += 1
        if self.on_write:
            self.on_write()
        before_write()
        if self.failure == "crash-before":
            raise SimulatedCrash()
        if self.failure == "timeout-before":
            raise TimeoutError("PRIVATE dispatch detail")
        self.writes += 1
        self.remote = self.remote.model_copy(
            update={
                "labels": sorted([*self.remote.labels, plan.label]),
                "updated_at": self.clock(),
            }
        )
        if self.failure == "crash-after":
            raise SimulatedCrash()
        if self.failure == "timeout-after":
            raise TimeoutError("PRIVATE response lost")


def plan_for(tmp_path):
    config = config_for(tmp_path)
    report = propose(config.scrum_snapshot)
    issue = next(
        s for s in report.snapshot.observation.sources if s.kind == "issue" and s.number == 1
    )
    raw = json.loads(issue.content)
    expected = RemoteIssueState(
        repository="owner/repo",
        number=1,
        node_id="issue-node-1",
        observed_at=timestamp(),
        updated_at=raw["updatedAt"],
        state="open",
        title_sha256="a" * 64,
        body_sha256="b" * 64,
        labels=["existing"],
    )
    return ScrumOperationPlan(
        report=report,
        proposal_id="refine-1",
        story_id="alpha",
        label="nexo:needs-refinement",
        expected=expected,
    )


def authorized(tmp_path, *, clock=timestamp):
    plan = plan_for(tmp_path)
    journal = OperationJournal(tmp_path / "operations.sqlite")
    first = journal.prepare(plan, clock())
    now = clock()
    auth = OperationAuthorization(
        operation_sha256=plan.operation_sha256,
        issued_at=now,
        expires_at=(instant(now) + timedelta(minutes=10)).isoformat(),
        comment="Approve only this label diff",
    )
    journal.append(
        plan.operation_sha256,
        first.sequence,
        "authorized",
        "human-authorized",
        now,
        authorization=auth,
    )
    adapter = FakeAdapter(plan, clock)
    runner = OperationRunner(journal, tmp_path / "repo", adapter, clock)
    return plan, journal, adapter, runner


def test_success_replay_and_journal_reopen_preserve_one_effect_and_receipt(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    receipt = runner.apply(plan.operation_sha256)
    assert receipt.state == "observed"
    assert adapter.writes == 1 and adapter.reads == 2
    journal2 = OperationJournal(journal.path)
    replay = OperationRunner(journal2, tmp_path / "repo", adapter).apply(plan.operation_sha256)
    assert replay == receipt
    assert adapter.writes == 1 and adapter.reads == 2
    assert [e.state for e in journal2.load(plan.operation_sha256)[1]] == [
        "prepared",
        "authorized",
        "attempted",
        "observed",
    ]


@pytest.mark.parametrize(
    "failure,expected_writes",
    [
        ("timeout-after", 1),
        ("post-read", 1),
        ("timeout-before", 0),
    ],
)
def test_uncertain_result_never_retries_write(tmp_path, failure, expected_writes):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.failure = failure
    result = runner.apply(plan.operation_sha256)
    assert result.state == "uncertain"
    assert adapter.writes == expected_writes
    with pytest.raises(ValueError, match="reconciliation"):
        runner.apply(plan.operation_sha256)
    adapter.failure = None
    receipt = runner.reconcile(plan.operation_sha256)
    assert receipt.state == ("observed" if expected_writes else "uncertain")
    assert adapter.writes == expected_writes
    assert "PRIVATE" not in journal.path.read_bytes().decode("utf-8", errors="ignore")


@pytest.mark.parametrize("failure,expected_writes", [("crash-before", 0), ("crash-after", 1)])
def test_crash_keeps_attempt_durable_and_requires_read_only_reconciliation(
    tmp_path, failure, expected_writes
):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.failure = failure
    with pytest.raises(SimulatedCrash):
        runner.apply(plan.operation_sha256)
    assert OperationJournal(journal.path).load(plan.operation_sha256)[1][-1].state == "attempted"
    with pytest.raises(ValueError, match="reconciliation"):
        runner.apply(plan.operation_sha256)
    adapter.failure = None
    result = runner.reconcile(plan.operation_sha256)
    assert result.state == ("observed" if expected_writes else "uncertain")
    assert adapter.writes == expected_writes


def test_prepared_is_not_authorized_and_report_approval_is_insufficient(tmp_path):
    plan = plan_for(tmp_path)
    journal = OperationJournal(tmp_path / "journal.sqlite")
    prepared = journal.prepare(plan, timestamp())
    assert journal.prepare(plan, timestamp()) == prepared
    adapter = FakeAdapter(plan)
    with pytest.raises(ValueError, match="authorization"):
        OperationRunner(journal, tmp_path / "repo", adapter).apply(plan.operation_sha256)
    assert adapter.reads == adapter.writes == 0


def test_expired_authorization_blocks_before_network(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    runner.clock = lambda: (instant(timestamp()) + timedelta(minutes=11)).isoformat()
    result = runner.apply(plan.operation_sha256)
    assert result.state == "blocked" and result.reason == "authorization-expired"
    assert adapter.reads == adapter.writes == 0


def test_expiry_immediately_before_write_is_uncertain_without_effect(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.on_write = lambda: setattr(
        runner, "clock", lambda: (instant(timestamp()) + timedelta(minutes=11)).isoformat()
    )
    result = runner.apply(plan.operation_sha256)
    assert result.state == "uncertain" and adapter.writes == 0
    assert journal.load(plan.operation_sha256)[1][-2].state == "attempted"


@pytest.mark.parametrize(
    "field,value",
    [
        ("body_sha256", "c" * 64),
        ("labels", ["concurrent", "existing"]),
        ("state", "closed"),
        ("milestone_id", 42),
        ("node_id", "different-node"),
    ],
)
def test_changed_remote_revision_blocks_without_write(tmp_path, field, value):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.remote = adapter.remote.model_copy(update={field: value})
    receipt = runner.apply(plan.operation_sha256)
    assert receipt.state == "blocked" and receipt.reason == "remote-changed"
    assert adapter.writes == 0


def test_changed_local_source_blocks_before_network(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    path = tmp_path / "repo/planning/sprint-2-5.json"
    path.write_text(path.read_text() + "\n")
    assert runner.apply(plan.operation_sha256).reason == "source-changed"
    assert adapter.reads == adapter.writes == 0


def test_preflight_timeout_never_dispatches(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.failure = "read"
    assert runner.apply(plan.operation_sha256).reason == "preflight-unavailable"
    assert adapter.dispatches == adapter.writes == 0


def test_local_change_immediately_before_write_is_not_dispatched(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.on_write = lambda: (tmp_path / "repo/docs/delivery/scrum.md").write_text("changed")
    assert runner.apply(plan.operation_sha256).state == "uncertain"
    assert adapter.writes == 0


def test_concurrent_change_after_preflight_is_preserved_and_result_uncertain(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.on_write = lambda: setattr(
        adapter,
        "remote",
        adapter.remote.model_copy(
            update={"body_sha256": "d" * 64, "labels": ["concurrent", "existing"]}
        ),
    )
    receipt = runner.apply(plan.operation_sha256)
    assert receipt.state == "uncertain"
    assert adapter.remote.body_sha256 == "d" * 64
    assert receipt.remote.body_sha256 == "d" * 64
    assert adapter.remote.labels == ["concurrent", "existing", plan.label]
    assert adapter.writes == 1


def test_crash_before_result_receipt_still_reconciles_without_writing(tmp_path, monkeypatch):
    plan, journal, adapter, runner = authorized(tmp_path)
    append = journal.append

    def fail_on_observed(key, version, state, *args, **kwargs):
        if state == "observed":
            raise SimulatedCrash()
        return append(key, version, state, *args, **kwargs)

    monkeypatch.setattr(journal, "append", fail_on_observed)
    with pytest.raises(SimulatedCrash):
        runner.apply(plan.operation_sha256)
    monkeypatch.setattr(journal, "append", append)
    assert journal.load(plan.operation_sha256)[1][-1].state == "attempted"
    assert runner.reconcile(plan.operation_sha256).state == "observed"
    assert adapter.writes == 1


def test_unrelated_database_is_not_reused(tmp_path):
    path = tmp_path / "other.sqlite"
    with sqlite3.connect(path) as db:
        db.execute("PRAGMA user_version=1")
        db.execute("CREATE TABLE unrelated (id INTEGER)")
    before = path.read_bytes()
    with pytest.raises(ValueError, match="Not an operation journal"):
        OperationJournal(path)
    assert path.read_bytes() == before


def test_cancellation_is_terminal_and_version_checked(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    key = plan.operation_sha256
    with pytest.raises(ValueError, match="changed"):
        journal.append(key, 1, "cancelled", "human-cancelled", timestamp())
    receipt = journal.append(key, 2, "cancelled", "human-cancelled", timestamp())
    assert receipt.state == "cancelled"
    with pytest.raises(ValueError):
        runner.apply(key)
    assert adapter.writes == adapter.reads == 0


def test_cancel_during_preflight_prevents_dispatch(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.on_preflight = lambda: journal.append(
        plan.operation_sha256, 2, "cancelled", "human-cancelled", timestamp()
    )
    with pytest.raises(ValueError, match="changed"):
        runner.apply(plan.operation_sha256)
    assert adapter.writes == 0


def test_concurrent_workers_cannot_dispatch_same_operation_twice(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    entered, release = threading.Event(), threading.Event()

    def pause():
        entered.set()
        assert release.wait(timeout=10)

    adapter.on_write = pause
    with ThreadPoolExecutor(max_workers=2) as pool:
        future = pool.submit(runner.apply, plan.operation_sha256)
        try:
            assert entered.wait(timeout=10)
            with pytest.raises(ValueError, match="reconciliation"):
                runner.apply(plan.operation_sha256)
        finally:
            release.set()
        assert future.result(timeout=10).state == "observed"
    assert adapter.writes == adapter.dispatches == 1


def test_uncertain_target_blocks_a_different_authorized_operation(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    adapter.failure = "timeout-before"
    runner.apply(plan.operation_sha256)
    other = ScrumOperationPlan.model_validate(
        {**plan.model_dump(), "proposal_id": "review-evidence", "label": "nexo:needs-evidence"}
    )
    journal.prepare(other, timestamp())
    now = timestamp()
    auth = OperationAuthorization(
        operation_sha256=other.operation_sha256,
        issued_at=now,
        expires_at=(instant(now) + timedelta(minutes=10)).isoformat(),
        comment="Different action, still blocked by uncertain target",
    )
    journal.append(
        other.operation_sha256, 1, "authorized", "human-authorized", now, authorization=auth
    )
    with pytest.raises(ValueError, match="unresolved operation"):
        runner.apply(other.operation_sha256)
    assert adapter.dispatches == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("label", "done"),
        ("kind", "close-issue"),
        ("story_id", "missing"),
        ("proposal_id", "missing"),
        ("label", "nexo:needs-capacity"),
    ],
)
def test_scope_and_operation_allowlist_cannot_be_overridden(tmp_path, field, value):
    plan = plan_for(tmp_path)
    with pytest.raises(ValidationError):
        ScrumOperationPlan.model_validate({**plan.model_dump(), field: value})


def test_authorization_binds_exact_diff(tmp_path):
    plan = plan_for(tmp_path)
    journal = OperationJournal(tmp_path / "journal.sqlite")
    journal.prepare(plan, timestamp())
    now = timestamp()
    auth = OperationAuthorization(
        operation_sha256="c" * 64,
        issued_at=now,
        expires_at=(instant(now) + timedelta(minutes=10)).isoformat(),
        comment="Wrong diff",
    )
    with pytest.raises(ValidationError, match="bind"):
        journal.append(
            plan.operation_sha256, 1, "authorized", "human-authorized", now, authorization=auth
        )
    assert len(journal.load(plan.operation_sha256)[1]) == 1


def test_receipts_are_immutable_and_projection_tampering_is_detected(tmp_path):
    plan, journal, adapter, runner = authorized(tmp_path)
    with sqlite3.connect(journal.path) as db:
        with pytest.raises(sqlite3.IntegrityError, match="Immutable"):
            db.execute("DELETE FROM events")
        db.execute("UPDATE operations SET state='observed'")
    with pytest.raises(ValueError, match="projection"):
        journal.load(plan.operation_sha256)


def test_cli_prepare_show_authorize_cancel_without_remote_calls(tmp_path, capsys):
    plan = plan_for(tmp_path)
    report, expected, journal = [
        tmp_path / p for p in ["report.json", "expected.json", "journal.sqlite"]
    ]
    report.write_text(plan.report.model_dump_json(), encoding="utf-8")
    expected.write_text(plan.expected.model_dump_json(), encoding="utf-8")
    assert (
        main(
            [
                "scrum",
                "operation",
                "prepare",
                "--report",
                str(report),
                "--expected",
                str(expected),
                "--proposal",
                "refine-1",
                "--story",
                "alpha",
                "--label",
                plan.label,
                "--journal",
                str(journal),
            ]
        )
        == 0
    )
    output = json.loads(capsys.readouterr().out)
    key = output["operation_sha256"]
    assert output["after_labels"] == ["existing", plan.label]
    shared = ["--journal", str(journal), "--operation", key]
    expires = (instant(timestamp()) + timedelta(minutes=5)).isoformat()
    assert (
        main(
            [
                "scrum",
                "operation",
                "authorize",
                *shared,
                "--expected-version",
                "1",
                "--expires-at",
                expires,
                "--comment",
                "Approve exact diff",
            ]
        )
        == 0
    )
    assert main(["scrum", "operation", "cancel", *shared, "--expected-version", "2"]) == 0
    assert main(["scrum", "operation", "show", *shared]) == 0
    assert OperationJournal(journal).load(key)[1][-1].state == "cancelled"
