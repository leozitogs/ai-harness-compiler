"""Bounded filesystem/GitHub read boundary for Scrum observations. Never writes remotely."""

import hashlib
import re
import shutil
import subprocess
import threading
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Literal, Protocol

from ai_harness_compiler.intake import parse_project_manifest
from ai_harness_compiler.models.scrum import (
    MAX_SOURCE_BYTES,
    DeliveryEvidence,
    ScrumObservation,
    SourceKind,
    StoryPRLink,
)
from ai_harness_compiler.scrum_observer import PlanProjection, decode_document, issue_links


def timestamp() -> str:
    return datetime.now(UTC).isoformat()


class GitHubReader(Protocol):
    def read(
        self,
        kind: Literal["issue", "pull-request"],
        repository: str,
        number: int,
        timeout_seconds: float,
    ) -> str: ...


class GitHubCLIReader:
    """Fixed read-only gh commands, explicit host, bounded stdout and timeout."""

    def read(
        self,
        kind: Literal["issue", "pull-request"],
        repository: str,
        number: int,
        timeout_seconds: float,
    ) -> str:
        if kind not in {"issue", "pull-request"} or type(number) is not int or number < 1:
            raise ValueError("Invalid read-only GitHub request")
        if not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}", repository
        ):
            raise ValueError("Invalid repository")
        if not 0 < timeout_seconds <= 10:
            raise ValueError("GitHub read timeout must be within 10 seconds")
        executable = shutil.which("gh")
        if executable is None:
            raise ValueError("GitHub CLI unavailable")
        category = "issues" if kind == "issue" else "pull"
        fields = (
            "number,url,state,updatedAt"
            if kind == "issue"
            else "number,url,state,headRefOid,statusCheckRollup"
        )
        process = subprocess.Popen(
            [
                executable,
                "issue" if kind == "issue" else "pr",
                "view",
                f"https://github.com/{repository}/{category}/{number}",
                "--json",
                fields,
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        chunks: list[bytes] = []
        errors: list[str] = []

        def consume() -> None:
            used = 0
            try:
                assert process.stdout is not None
                while chunk := process.stdout.read(16384):
                    used += len(chunk)
                    if used > MAX_SOURCE_BYTES:
                        errors.append("limit")
                        process.kill()
                        return
                    chunks.append(chunk)
            except OSError:
                errors.append("read")

        reader = threading.Thread(target=consume, daemon=True)
        reader.start()
        try:
            process.wait(timeout=timeout_seconds)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait()
            raise ValueError("GitHub read timed out") from exc
        finally:
            reader.join(timeout=2)
            if process.stdout is not None and not reader.is_alive():
                process.stdout.close()
        if reader.is_alive() or errors or process.returncode != 0:
            raise ValueError("GitHub read failed or exceeded output limit")
        return b"".join(chunks).decode("utf-8")


def collect(
    root: Path,
    project_id: str,
    repository: str,
    sprint_id: str,
    *,
    reader: GitHubReader | None = None,
    links: list[StoryPRLink] | None = None,
    max_age_seconds: int = 3600,
    max_remote_reads: int = 16,
    session_seconds: int = 120,
) -> ScrumObservation:
    # Validate scope and identifiers before using them in any paths or commands.
    from pydantic import TypeAdapter

    from ai_harness_compiler.models.base import Identifier
    from ai_harness_compiler.models.scrum import RepositoryName, SprintID

    project_id = TypeAdapter(Identifier).validate_python(project_id)
    repository = TypeAdapter(RepositoryName).validate_python(repository)
    sprint_id = TypeAdapter(SprintID).validate_python(sprint_id)
    links = [StoryPRLink.model_validate(p.model_dump()) for p in (links or [])]
    if type(max_remote_reads) is not int or not 0 <= max_remote_reads <= 64:
        raise ValueError("Remote read budget must be 0..64")
    if type(session_seconds) is not int or not 1 <= session_seconds <= 120:
        raise ValueError("Collection session must be 1..120 seconds")
    if type(max_age_seconds) is not int or not 1 <= max_age_seconds <= 86400:
        raise ValueError("Freshness window must be 1..86400 seconds")
    if len(links) > 128 or len({(p.story_id, p.number) for p in links}) != len(links):
        raise ValueError("PR links must be unique and within 128 entries")
    root = root.resolve()
    sources: list[DeliveryEvidence] = []

    def evidence(
        kind: SourceKind,
        locator: str,
        content: str | None,
        reason: Literal["not-requested", "read-failed", "limit-exceeded", "provider-failed"]
        | None = None,
        number: int | None = None,
        revision: str | None = None,
    ) -> None:
        sources.append(
            DeliveryEvidence(
                id=f"source-{len(sources) + 1}",
                project_id=project_id,
                repository=repository,
                kind=kind,
                locator=locator,
                observed_at=timestamp(),
                number=number,
                status="observed" if content is not None else "unavailable",
                content=content,
                content_sha256=hashlib.sha256(content.encode()).hexdigest()
                if content is not None
                else None,
                reason=reason,
                revision=revision,
            )
        )

    locations: list[tuple[SourceKind, str]] = [
        ("project", "project-definition/project.yaml"),
        ("plan", f"planning/{sprint_id}.json"),
        ("work-items", f"planning/{sprint_id}.work-items.json"),
        ("policy", "docs/delivery/scrum.md"),
        ("memory-index", "knowledge/INDEX.md"),
    ]
    for kind, locator in locations:
        path = (root / locator).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Scrum source resolves outside repository")
        try:
            with path.open("rb") as stream:
                raw = stream.read(MAX_SOURCE_BYTES + 1)
            if len(raw) > MAX_SOURCE_BYTES:
                evidence(kind, locator, None, "limit-exceeded")
                continue
            # Normalize the exact captured manifest bytes; revision identifies raw bytes.
            content = (
                parse_project_manifest(raw).model_dump_json()
                if kind == "project"
                else raw.decode("utf-8")
            )
            if len(content.encode()) > MAX_SOURCE_BYTES:
                evidence(kind, locator, None, "limit-exceeded")
            else:
                evidence(kind, locator, content, revision=hashlib.sha256(raw).hexdigest())
        except (OSError, ValueError):
            evidence(kind, locator, None, "read-failed")

    requested: list[tuple[Literal["issue", "pull-request"], int]] = []
    plan_source = sources[1]
    try:
        plan = PlanProjection.model_validate(decode_document(plan_source.content or ""))
        if plan.id != sprint_id:
            raise ValueError("Plan identity differs")
        project_source = sources[0]
        from ai_harness_compiler.models.project import ProjectInput

        if ProjectInput.model_validate_json(project_source.content or "").id != project_id:
            raise ValueError("Project identity differs")
        tracked = issue_links(plan, repository)
        if any(p.story_id not in plan.selected_capabilities for p in links):
            raise ValueError("PR links must refer to selected stories")
        requested = [
            ("issue", n) for story, n in tracked.items() if story in plan.selected_capabilities
        ]
        requested += [("pull-request", p.number) for p in links]
    except ValueError:
        # Invalid plan/project never drives a network lookup; pure reconciliation diagnoses it.
        requested = []
    started = monotonic()
    reads = 0
    for kind, number in dict.fromkeys(requested):
        category = "issues" if kind == "issue" else "pull"
        locator = f"https://github.com/{repository}/{category}/{number}"
        remaining = session_seconds - (monotonic() - started)
        if reader is None:
            evidence(kind, locator, None, "not-requested", number)
        elif reads >= max_remote_reads or remaining <= 0:
            evidence(kind, locator, None, "limit-exceeded", number)
        else:
            reads += 1
            try:
                content = reader.read(kind, repository, number, min(10.0, remaining))
                if len(content.encode()) > MAX_SOURCE_BYTES:
                    evidence(kind, locator, None, "limit-exceeded", number)
                else:
                    evidence(kind, locator, content, number=number)
            except (OSError, ValueError):
                evidence(kind, locator, None, "provider-failed", number)
    return ScrumObservation(
        project_id=project_id,
        repository=repository,
        sprint_id=sprint_id,
        observed_at=timestamp(),
        max_age_seconds=max_age_seconds,
        sources=sources,
        pull_request_links=links,
    )
