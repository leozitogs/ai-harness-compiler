"""Append-only JSON revisions are authoritative; SQLite FTS5 is a disposable index."""

import hashlib
import os
import re
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.memory import MemoryRecord, RecordDraft, Status

METADATA = {
    "schema_version",
    "revision",
    "status",
    "created_at",
    "updated_at",
    "reviewed_by",
    "review_note",
}


class MemoryStore:
    def __init__(self, repository: Path, project_id: str = "ai-harness-compiler") -> None:
        self.root = repository.resolve()
        self.project_id = project_id
        self.records = self.safe_path("knowledge/records")
        digest = hashlib.sha256(project_id.encode()).hexdigest()[:16]
        self.database = self.safe_path(f".factory/memory/{digest}.sqlite")

    def safe_path(self, relative: str) -> Path:
        candidate = (self.root / relative).resolve()
        if not candidate.is_relative_to(self.root):
            raise ValueError("Memory path escapes repository")
        return candidate

    def latest(self) -> dict[str, MemoryRecord]:
        result: dict[str, MemoryRecord] = {}
        revisions: dict[str, list[int]] = {}
        for candidate in sorted(self.records.glob("*/*/*.json")):
            path = candidate.resolve()
            if not path.is_relative_to(self.root) or path.stat().st_size > 64 * 1024:
                raise ValueError("Memory record escapes repository or exceeds 64 KiB")
            record = MemoryRecord.model_validate_json(path.read_text(encoding="utf-8"))
            if candidate.parent.name != record.id or candidate.parent.parent.name != record.kind:
                raise ValueError("Record path must match its ID and kind")
            if candidate.name != f"{record.revision:04d}.json":
                raise ValueError("Revision filename must match record metadata")
            if record.project_id != self.project_id:
                continue
            revisions.setdefault(record.id, []).append(record.revision)
            if record.id not in result or record.revision > result[record.id].revision:
                result[record.id] = record
        for identifier, sequence in revisions.items():
            if sequence != list(range(1, max(sequence) + 1)):
                raise ValueError(f"Non-contiguous revisions for {identifier}")
        for record in result.values():
            links = record.related + ([record.supersedes] if record.supersedes else [])
            if set(links) - result.keys():
                raise ValueError(f"Unresolved/cross-project relationships for {record.id}")
        return result

    @contextmanager
    def writer(self) -> Iterator[None]:
        self.records.mkdir(parents=True, exist_ok=True)
        lock = self.safe_path("knowledge/records/.writer.lock")
        try:
            with lock.open("x", encoding="utf-8") as stream:
                stream.write(str(os.getpid()))
        except FileExistsError as exc:
            raise ValueError(
                "Memory writer is locked; confirm no active writer before recovery"
            ) from exc
        try:
            yield
        finally:
            lock.unlink()

    def append(self, record: MemoryRecord) -> MemoryRecord:
        target = self.safe_path(
            f"knowledge/records/{record.kind}/{record.id}/{record.revision:04d}.json"
        )
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists():
            raise ValueError("A memory revision is immutable")
        text = json_text(record.model_dump())
        if len(text.encode("utf-8")) > 64 * 1024:
            raise ValueError("Memory record exceeds 64 KiB")
        temporary = target.with_name(f".{uuid4().hex}.tmp")
        try:
            with temporary.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return record

    def add(self, draft: RecordDraft) -> MemoryRecord:
        draft = RecordDraft.model_validate(draft.model_dump())
        if draft.project_id != self.project_id:
            raise ValueError("Record belongs to a different project")
        with self.writer():
            current = self.latest()
            if draft.id in current:
                raise ValueError("Record already exists; use revise with expected revision")
            links = draft.related + ([draft.supersedes] if draft.supersedes else [])
            if set(links) - current.keys():
                raise ValueError("Relationships must resolve within this project")
            now = datetime.now(UTC).isoformat()
            record = MemoryRecord(**draft.model_dump(), revision=1, created_at=now, updated_at=now)
            return self.append(record)

    def revise(self, draft: RecordDraft, expected: int) -> MemoryRecord:
        with self.writer():
            current = self.latest()
            previous = current[draft.id]
            if previous.revision != expected:
                raise ValueError("Revision conflict: reload before editing")
            if (draft.kind, draft.project_id) != (previous.kind, previous.project_id):
                raise ValueError("Kind and project are immutable")
            links = draft.related + ([draft.supersedes] if draft.supersedes else [])
            if set(links) - current.keys():
                raise ValueError("Relationships must resolve")
            return self.append(
                MemoryRecord(
                    **draft.model_dump(),
                    revision=expected + 1,
                    created_at=previous.created_at,
                    updated_at=datetime.now(UTC).isoformat(),
                )
            )

    def review(
        self, identifier: str, expected: int, status: Status, reviewer: str, note: str
    ) -> MemoryRecord:
        with self.writer():
            previous = self.latest()[identifier]
            if previous.revision != expected or previous.status == "superseded":
                raise ValueError("Revision conflict or already superseded record")
            payload = previous.model_dump()
            payload.update(
                revision=expected + 1,
                status=status,
                reviewed_by=reviewer,
                review_note=note,
                updated_at=datetime.now(UTC).isoformat(),
            )
            record = MemoryRecord.model_validate(payload)
            if status in {"active", "verified"} and not self.evidence_current(record):
                raise ValueError("Evidence is missing, changed or lacks a local source digest")
            return self.append(record)

    def evidence_current(self, record: MemoryRecord) -> bool:
        if not record.evidence:
            return record.status == "draft"
        for evidence in record.evidence:
            if not evidence.sha256:
                return False
            source = evidence.source.split("#", 1)[0]
            if "://" in source:
                return False  # External sources need a local verified evidence snapshot.
            path = self.safe_path(source)
            if not path.is_file() or path.stat().st_size > 1024 * 1024:
                return False
            if hashlib.sha256(path.read_bytes()).hexdigest() != evidence.sha256:
                return False
        return True

    def reusable(self) -> list[MemoryRecord]:
        current = self.latest()
        replaced = {
            record.supersedes
            for record in current.values()
            if record.status in {"active", "verified"} and record.supersedes
        }
        return [
            record
            for record in current.values()
            if record.status in {"active", "verified"}
            and record.id not in replaced
            and self.evidence_current(record)
        ]

    def search(
        self, query: str, limit: int = 5, include_drafts: bool = False
    ) -> list[dict[str, object]]:
        if not 1 <= limit <= 20 or len(query) > 2000:
            raise ValueError("Search limit must be 1..20 and query at most 2000 characters")
        records = list(self.latest().values()) if include_drafts else self.reusable()
        records = [record for record in records if record.status != "superseded"]
        tokens = re.findall(r"\w+", query, flags=re.UNICODE)[:20]
        if not records or not tokens:
            return []
        self.database.parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.database, timeout=10)
        try:
            connection.execute(
                "CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts "
                "USING fts5(id UNINDEXED, title, body)"
            )
            # The index is rebuilt from a validated snapshot, never trusted as source data.
            with connection:
                connection.execute("DELETE FROM memory_fts")
                connection.executemany(
                    "INSERT INTO memory_fts(id,title,body) VALUES(?,?,?)",
                    [
                        (record.id, record.title, json_text(record.model_dump()))
                        for record in records
                    ],
                )
                expression = " OR ".join('"' + token.replace('"', '""') + '"' for token in tokens)
                rows = connection.execute(
                    "SELECT id, bm25(memory_fts,0,4,1) FROM memory_fts "
                    "WHERE memory_fts MATCH ? ORDER BY 2,id LIMIT ?",
                    (expression, limit),
                ).fetchall()
        finally:
            connection.close()
        by_id = {record.id: record for record in records}
        reusable_ids = {record.id for record in self.reusable()}
        return [
            {
                "record": by_id[identifier].model_dump(),
                "bm25": score,
                "reusable": identifier in reusable_ids,
            }
            for identifier, score in rows
        ]

    def context(self, query: str, budget: int = 6000) -> list[dict[str, object]]:
        selected: list[dict[str, object]] = []
        for hit in self.search(query, limit=3):
            text = json_text(hit)
            if len(text) <= budget:
                selected.append(hit)
                budget -= len(text)
        return selected

    def render_index(self) -> str:
        records = self.latest()
        lines = [
            "# Engineering memory index",
            "",
            "Generated from immutable JSON revisions. Do not hand-edit.",
            "",
            "Drafts are proposals; reusable records still require scope and evidence checks.",
            "",
        ]
        for record in sorted(records.values(), key=lambda item: item.id):
            path = f"records/{record.kind}/{record.id}/{record.revision:04d}.json"
            title = record.title.replace("[", "\\[").replace("]", "\\]").replace("\n", " ")
            lines.append(
                f"- [{record.id} — {title}]({path}) · {record.status} · revision {record.revision}"
            )
        return "\n".join(lines) + "\n"

    def digests(self) -> dict[str, str]:
        result = {}
        for record in self.latest().values():
            source = f"knowledge/records/{record.kind}/{record.id}/{record.revision:04d}.json"
            result[source] = hashlib.sha256(
                json_text(record.model_dump()).encode("utf-8")
            ).hexdigest()
            result[source + "#evidence-current"] = hashlib.sha256(
                str(self.evidence_current(record)).encode("utf-8")
            ).hexdigest()
        return result
