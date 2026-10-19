"""Transactional local journal and bounded, additive remote operation runner."""

import sqlite3
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Protocol

from ai_harness_compiler.models.scrum import instant
from ai_harness_compiler.models.scrum_operations import (
    OperationAuthorization,
    OperationReceipt,
    OperationState,
    Reason,
    RemoteIssueState,
    ScrumOperationPlan,
)
from ai_harness_compiler.scrum_collection import timestamp
from ai_harness_compiler.scrum_planning import assert_current

TRANSITIONS: dict[str, set[str]] = {
    "prepared": {"authorized", "cancelled"},
    "authorized": {"attempted", "blocked", "cancelled"},
    "attempted": {"observed", "uncertain"},
    "uncertain": {"observed", "uncertain"},
    "observed": set(),
    "blocked": set(),
    "cancelled": set(),
}
REASONS: dict[str, set[str]] = {
    "prepared": {"prepared"},
    "authorized": {"human-authorized"},
    "attempted": {"dispatch-recorded"},
    "observed": {"desired-state-observed"},
    "uncertain": {"write-or-observation-uncertain", "effect-not-established"},
    "blocked": {
        "remote-changed",
        "authorization-expired",
        "source-changed",
        "preflight-unavailable",
    },
    "cancelled": {"human-cancelled"},
}


def effect_matches(plan: ScrumOperationPlan, remote: RemoteIssueState) -> bool:
    expected = plan.expected.model_dump(exclude={"observed_at", "updated_at", "labels"})
    actual = remote.model_dump(exclude={"observed_at", "updated_at", "labels"})
    return (
        actual == expected
        and remote.labels == sorted([*plan.expected.labels, plan.label])
        and instant(remote.updated_at) >= instant(plan.expected.updated_at)
    )


class OperationAdapter(Protocol):
    def read_issue(
        self, repository: str, number: int, timeout_seconds: float
    ) -> RemoteIssueState: ...
    def add_label(
        self,
        plan: ScrumOperationPlan,
        timeout_seconds: float,
        before_write: Callable[[], None],
    ) -> None: ...


class OperationJournal:
    """One shared journal per repository; no lock is held across network calls."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()
        try:
            with self.path.open("xb"):
                pass
            created = True
        except FileExistsError:
            created = False
        try:
            self._initialize(created)
        except sqlite3.Error as exc:
            raise ValueError("Invalid or unavailable operation journal") from exc

    def _initialize(self, created: bool) -> None:
        with sqlite3.connect(self.path, timeout=5) as db:
            if created:
                db.executescript("""
                    PRAGMA user_version=1;
                    PRAGMA application_id=1095254863;
                    CREATE TABLE operations (
                        id TEXT PRIMARY KEY, plan TEXT NOT NULL, repository TEXT NOT NULL,
                        number INTEGER NOT NULL, state TEXT NOT NULL, version INTEGER NOT NULL);
                    CREATE UNIQUE INDEX inflight_target ON operations(repository, number)
                        WHERE state IN ('attempted', 'uncertain');
                    CREATE TABLE events (
                        operation_id TEXT NOT NULL REFERENCES operations(id),
                        sequence INTEGER NOT NULL, data TEXT NOT NULL, sha256 TEXT NOT NULL,
                        PRIMARY KEY(operation_id, sequence));
                    CREATE TRIGGER immutable_update BEFORE UPDATE ON events
                        BEGIN SELECT RAISE(ABORT, 'Immutable receipt'); END;
                    CREATE TRIGGER immutable_delete BEFORE DELETE ON events
                        BEGIN SELECT RAISE(ABORT, 'Immutable receipt'); END;
                """)
            elif (
                db.execute("PRAGMA user_version").fetchone()[0] != 1
                or db.execute("PRAGMA application_id").fetchone()[0] != 1095254863
            ):
                raise ValueError("Not an operation journal; choose a new path")

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        db = sqlite3.connect(self.path, timeout=5)
        try:
            db.execute("PRAGMA synchronous=FULL")
            db.execute("PRAGMA foreign_keys=ON")
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except sqlite3.Error as exc:
            db.rollback()
            raise ValueError("Operation journal transaction failed") from exc
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def _load(
        self,
        db: sqlite3.Connection,
        key: str,
    ) -> tuple[ScrumOperationPlan, list[OperationReceipt]]:
        size = db.execute("SELECT length(plan) FROM operations WHERE id=?", (key,)).fetchone()
        if size is None or size[0] > 12 * 1024 * 1024:
            raise ValueError("Operation missing or journal payload exceeds limit")
        row = db.execute(
            "SELECT plan,repository,number,state,version FROM operations WHERE id=?", (key,)
        ).fetchone()
        plan = ScrumOperationPlan.model_validate_json(row[0])
        if plan.operation_sha256 != key or (row[1], row[2]) != (
            plan.expected.repository,
            plan.expected.number,
        ):
            raise ValueError("Journal operation identity differs from plan")
        sizes = db.execute(
            "SELECT length(data) FROM events WHERE operation_id=? LIMIT 129", (key,)
        ).fetchall()
        if not sizes or len(sizes) > 128 or any(s[0] > 512 * 1024 for s in sizes):
            raise ValueError("Journal receipt inventory exceeds limits")
        events: list[OperationReceipt] = []
        for sequence, raw, digest in db.execute(
            "SELECT sequence,data,sha256 FROM events WHERE operation_id=? ORDER BY sequence", (key,)
        ):
            event = OperationReceipt.model_validate_json(raw)
            previous = events[-1] if events else None
            if (
                event.operation_sha256 != key
                or event.sequence != sequence
                or sequence != len(events) + 1
                or event.receipt_sha256 != digest
                or event.previous_sha256 != (previous.receipt_sha256 if previous else None)
                or event.reason not in REASONS[event.state]
                or (previous is None and event.state != "prepared")
                or (previous and event.state not in TRANSITIONS[previous.state])
            ):
                raise ValueError("Invalid journal receipt chain")
            if previous and instant(event.recorded_at) < instant(previous.recorded_at):
                raise ValueError("Receipt time precedes previous event")
            if event.remote is not None and (
                event.remote.repository != plan.expected.repository
                or event.remote.number != plan.expected.number
                or instant(event.remote.observed_at) > instant(event.recorded_at)
                or (
                    previous is not None
                    and instant(event.remote.observed_at) < instant(previous.recorded_at)
                )
            ):
                raise ValueError("Receipt remote evidence is out of scope or in the future")
            if event.state == "observed" and (
                event.remote is None or not effect_matches(plan, event.remote)
            ):
                raise ValueError("Observed receipt does not establish the desired state")
            events.append(event)
        if (row[3], row[4]) != (events[-1].state, len(events)):
            raise ValueError("Journal projection differs from immutable receipts")
        return plan, events

    def load(self, key: str) -> tuple[ScrumOperationPlan, list[OperationReceipt]]:
        with self.transaction() as db:
            return self._load(db, key)

    def prepare(self, plan: ScrumOperationPlan, now: str) -> OperationReceipt:
        plan = ScrumOperationPlan.model_validate(plan.model_dump())
        if instant(plan.expected.observed_at) > instant(now):
            raise ValueError("Cannot prepare from a future remote observation")
        key = plan.operation_sha256
        event = OperationReceipt(
            operation_sha256=key, sequence=1, state="prepared", recorded_at=now, reason="prepared"
        )
        with self.transaction() as db:
            if db.execute("SELECT 1 FROM operations WHERE id=?", (key,)).fetchone():
                return self._load(db, key)[1][-1]
            db.execute(
                "INSERT INTO operations VALUES (?,?,?,?,?,?)",
                (
                    key,
                    plan.model_dump_json(),
                    plan.expected.repository,
                    plan.expected.number,
                    event.state,
                    1,
                ),
            )
            db.execute(
                "INSERT INTO events VALUES (?,?,?,?)",
                (key, 1, event.model_dump_json(), event.receipt_sha256),
            )
        return event

    def append(
        self,
        key: str,
        expected_version: int,
        state: OperationState,
        reason: Reason,
        now: str,
        *,
        authorization: OperationAuthorization | None = None,
        remote: RemoteIssueState | None = None,
    ) -> OperationReceipt:
        with self.transaction() as db:
            plan, events = self._load(db, key)
            previous = events[-1]
            if len(events) != expected_version or state not in TRANSITIONS[previous.state]:
                raise ValueError("Operation changed or transition is not allowed")
            if len(events) >= 128 or instant(now) < instant(previous.recorded_at):
                raise ValueError("Journal event limit or clock regression")
            if reason not in REASONS[state]:
                raise ValueError("Reason differs from operation state")
            if remote is not None:
                remote = RemoteIssueState.model_validate(remote.model_dump())
                if (remote.repository, remote.number) != (
                    plan.expected.repository,
                    plan.expected.number,
                ) or not instant(previous.recorded_at) <= instant(remote.observed_at) <= instant(
                    now
                ):
                    raise ValueError("Remote receipt evidence is out of scope")
            if state == "observed" and (remote is None or not effect_matches(plan, remote)):
                raise ValueError("Remote state does not establish the desired effect")
            if state == "attempted":
                auth = next(e.authorization for e in events if e.authorization is not None)
                if not instant(auth.issued_at) <= instant(now) < instant(auth.expires_at):
                    raise ValueError("Authorization is expired or in the future")
            event = OperationReceipt(
                operation_sha256=key,
                sequence=len(events) + 1,
                previous_sha256=previous.receipt_sha256,
                state=state,
                recorded_at=now,
                reason=reason,
                authorization=authorization,
                remote=remote,
            )
            try:
                db.execute(
                    "UPDATE operations SET state=?,version=? WHERE id=?",
                    (state, event.sequence, key),
                )
            except sqlite3.IntegrityError as exc:
                raise ValueError("Target has an unresolved operation; reconcile it first") from exc
            db.execute(
                "INSERT INTO events VALUES (?,?,?,?)",
                (key, event.sequence, event.model_dump_json(), event.receipt_sha256),
            )
        return event


class OperationRunner:
    def __init__(
        self,
        journal: OperationJournal,
        root: Path,
        adapter: OperationAdapter,
        clock: Callable[[], str] = timestamp,
    ) -> None:
        self.journal, self.root, self.adapter, self.clock = journal, root, adapter, clock

    def _read(self, plan: ScrumOperationPlan, not_before: str) -> RemoteIssueState:
        remote = RemoteIssueState.model_validate(
            self.adapter.read_issue(plan.expected.repository, plan.expected.number, 10).model_dump()
        )
        if (remote.repository, remote.number) != (
            plan.expected.repository,
            plan.expected.number,
        ) or not instant(not_before) <= instant(remote.observed_at) <= instant(self.clock()):
            raise ValueError("Remote observation is out of scope or outside the read interval")
        return remote

    def apply(self, key: str) -> OperationReceipt:
        plan, events = self.journal.load(key)
        last = events[-1]
        if last.state == "observed":
            return last
        if last.state != "authorized":
            raise ValueError(
                "Explicit authorization required; attempted/uncertain needs reconciliation"
            )
        assert last.authorization is not None
        now = self.clock()
        if (
            not instant(last.authorization.issued_at)
            <= instant(now)
            < instant(last.authorization.expires_at)
        ):
            return self.journal.append(key, last.sequence, "blocked", "authorization-expired", now)
        try:
            assert_current(plan.report.snapshot, self.root, now)
            age = (instant(now) - instant(plan.expected.observed_at)).total_seconds()
            if not 0 <= age <= plan.report.snapshot.observation.max_age_seconds:
                raise ValueError("Expected state is expired or in the future")
        except (OSError, ValueError):
            return self.journal.append(
                key, last.sequence, "blocked", "source-changed", self.clock()
            )
        try:
            current = self._read(plan, now)
        except Exception:
            return self.journal.append(
                key, last.sequence, "blocked", "preflight-unavailable", self.clock()
            )
        if current.revision != plan.expected.revision:
            return self.journal.append(
                key, last.sequence, "blocked", "remote-changed", self.clock(), remote=current
            )
        # Recheck local evidence and authorization after the bounded remote preflight.
        try:
            assert_current(plan.report.snapshot, self.root, self.clock())
        except (OSError, ValueError):
            return self.journal.append(
                key, last.sequence, "blocked", "source-changed", self.clock()
            )
        attempt = self.journal.append(
            key, last.sequence, "attempted", "dispatch-recorded", self.clock()
        )

        def before_write() -> None:
            assert last.authorization is not None
            if (
                not instant(last.authorization.issued_at)
                <= instant(self.clock())
                < instant(last.authorization.expires_at)
            ):
                raise ValueError("Authorization expired before write")
            assert_current(plan.report.snapshot, self.root, self.clock())

        remote = None
        try:
            self.adapter.add_label(plan, 10, before_write)
            remote = self._read(plan, attempt.recorded_at)
            if not effect_matches(plan, remote):
                raise ValueError("Remote result differs from desired state")
        except Exception:
            return self.journal.append(
                key,
                attempt.sequence,
                "uncertain",
                "write-or-observation-uncertain",
                self.clock(),
                remote=remote,
            )
        return self.journal.append(
            key, attempt.sequence, "observed", "desired-state-observed", self.clock(), remote=remote
        )

    def reconcile(self, key: str) -> OperationReceipt:
        plan, events = self.journal.load(key)
        last = events[-1]
        if last.state == "observed":
            return last
        if last.state not in {"attempted", "uncertain"}:
            raise ValueError("Only attempted or uncertain operations can be reconciled")
        remote = None
        try:
            remote = self._read(plan, last.recorded_at)
            if not effect_matches(plan, remote):
                raise ValueError("Desired remote state is not established")
        except Exception:
            if last.state == "uncertain" and (
                remote is None
                or (last.remote is not None and remote.revision == last.remote.revision)
            ):
                return last
            return self.journal.append(
                key,
                last.sequence,
                "uncertain",
                "effect-not-established",
                self.clock(),
                remote=remote,
            )
        return self.journal.append(
            key, last.sequence, "observed", "desired-state-observed", self.clock(), remote=remote
        )
