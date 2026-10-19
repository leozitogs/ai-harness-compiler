"""Read-only Scrum observation contracts; captured sources do not confer authority."""

import hashlib
import re
from datetime import datetime
from pathlib import PurePosixPath
from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest

RepositoryName = Annotated[
    str,
    StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,99}/[A-Za-z0-9][A-Za-z0-9_.-]{0,99}$"),
]
SprintID = Annotated[
    str, StringConstraints(pattern=r"^sprint-[1-9][0-9]*(?:-[1-9][0-9]*){0,2}$", max_length=64)
]
SourceKind = Literal[
    "project", "plan", "work-items", "policy", "memory-index", "issue", "pull-request"
]
LOCAL_KINDS = {"project", "plan", "work-items", "policy", "memory-index"}
MAX_SOURCE_BYTES = 256 * 1024


def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Observation timestamps require an explicit timezone")
    return parsed


class DeliveryEvidence(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["DeliveryEvidence/v1"] = "DeliveryEvidence/v1"
    id: Identifier
    project_id: Identifier
    repository: RepositoryName
    kind: SourceKind
    locator: Text = Field(max_length=512)
    observed_at: Text = Field(max_length=40)
    status: Literal["observed", "unavailable"]
    content: str | None = Field(default=None, max_length=MAX_SOURCE_BYTES)
    content_sha256: Digest | None = None
    revision: Text | None = Field(default=None, max_length=200)
    number: int | None = Field(default=None, ge=1)
    reason: Literal["not-requested", "read-failed", "limit-exceeded", "provider-failed"] | None = (
        None
    )
    content_trust: Literal["untrusted-reference-data"] = "untrusted-reference-data"

    @model_validator(mode="after")
    def bounded_source(self) -> Self:
        instant(self.observed_at)
        if self.kind in LOCAL_KINDS:
            path = PurePosixPath(self.locator)
            if (
                path.is_absolute()
                or ".." in path.parts
                or "\\" in self.locator
                or ":" in self.locator
                or str(path) != self.locator
                or self.number is not None
            ):
                raise ValueError("Local evidence requires a normalized repository-relative path")
        else:
            category = "issues" if self.kind == "issue" else "pull"
            if (
                self.number is None
                or self.locator != f"https://github.com/{self.repository}/{category}/{self.number}"
            ):
                raise ValueError("Remote evidence requires an exact scoped GitHub locator")
        if self.status == "observed":
            if self.content is None or self.reason is not None:
                raise ValueError(
                    "Observed evidence requires captured content and no failure reason"
                )
            raw = self.content.encode("utf-8")
            if (
                len(raw) > MAX_SOURCE_BYTES
                or hashlib.sha256(raw).hexdigest() != self.content_sha256
            ):
                raise ValueError("Evidence content bytes exceed limit or differ from digest")
        elif (
            self.content is not None
            or self.content_sha256 is not None
            or self.revision is not None
            or self.reason is None
        ):
            raise ValueError(
                "Unavailable evidence has a reason and no observed content or revision"
            )
        return self


class StoryPRLink(Contract):
    story_id: Identifier
    number: int = Field(ge=1)


class ScrumObservation(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["ScrumObservation/v1"] = "ScrumObservation/v1"
    project_id: Identifier
    repository: RepositoryName
    sprint_id: SprintID
    observed_at: Text
    max_age_seconds: int = Field(default=3600, ge=1, le=86400)
    sources: list[DeliveryEvidence] = Field(min_length=5, max_length=256)
    pull_request_links: list[StoryPRLink] = Field(default_factory=list, max_length=128)

    @property
    def snapshot_sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def scoped_inventory(self) -> Self:
        now = instant(self.observed_at)
        sources = [DeliveryEvidence.model_validate(s.model_dump()) for s in self.sources]
        if len({s.id for s in sources}) != len(sources):
            raise ValueError("Evidence IDs must be unique")
        for kind in LOCAL_KINDS:
            if sum(s.kind == kind for s in sources) != 1:
                raise ValueError("Exactly one observation of each local source kind is required")
        if len({(s.kind, s.number) for s in sources if s.kind not in LOCAL_KINDS}) != sum(
            s.kind not in LOCAL_KINDS for s in sources
        ):
            raise ValueError("Remote resource observations must be unique")
        for source in sources:
            if source.project_id != self.project_id or source.repository != self.repository:
                raise ValueError("Evidence belongs to another project or repository")
            if instant(source.observed_at) > now:
                raise ValueError("Evidence observation cannot be later than snapshot time")
        if sum(len((s.content or "").encode()) for s in sources) > 4 * 1024 * 1024:
            raise ValueError("Observation content exceeds 4 MiB")
        if len(self.model_dump_json().encode()) > 6 * 1024 * 1024:
            raise ValueError("Serialized observation exceeds 6 MiB")
        links = [(p.story_id, p.number) for p in self.pull_request_links]
        if len(set(links)) != len(links):
            raise ValueError("Story/PR links cannot be duplicated")
        if any(
            not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", p.story_id) for p in self.pull_request_links
        ):
            raise ValueError("Invalid story identifier")
        return self


class ObservedPullRequest(Contract):
    number: int = Field(ge=1)
    state: Literal["OPEN", "CLOSED", "MERGED"]
    head_sha: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{40}$")]
    checks: Literal["all-success", "failure", "pending", "unknown"]
    evidence_id: Identifier


class ObservedStory(Contract):
    id: Identifier
    declared_status: Text
    issue_state: Literal["OPEN", "CLOSED", "unknown"]
    pull_requests: list[ObservedPullRequest] = Field(default_factory=list, max_length=128)
    dependencies: list[Identifier] = Field(default_factory=list, max_length=128)
    evidence_ids: list[Identifier] = Field(min_length=1, max_length=256)
    acceptance: Literal["not-established"] = "not-established"


class Impediment(Contract):
    schema_version: Literal["Impediment/v1"] = "Impediment/v1"
    id: Identifier
    code: Identifier
    severity: Literal["info", "warning", "blocker"]
    story_id: Identifier | None = None
    message: Text
    evidence_ids: list[Identifier] = Field(min_length=1, max_length=256)


class SprintSnapshot(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["SprintSnapshot/v1"] = "SprintSnapshot/v1"
    observation: ScrumObservation
    observation_sha256: Digest
    declared_state: Text
    declared_goal_outcome: Literal["achieved", "not-achieved", "unknown"]
    stories: list[ObservedStory] = Field(default_factory=list, max_length=64)
    impediments: list[Impediment] = Field(default_factory=list, max_length=1024)
    authority: Literal["read-only-diagnostic"] = "read-only-diagnostic"
    completion_authority: Literal["none"] = "none"

    @model_validator(mode="after")
    def derived_from_captured_evidence(self) -> Self:
        from ai_harness_compiler.scrum_observer import derive

        observation = ScrumObservation.model_validate(self.observation.model_dump())
        if self.observation_sha256 != observation.snapshot_sha256:
            raise ValueError("Snapshot belongs to a different observation")
        state, goal, stories, impediments = derive(observation)
        if (self.declared_state, self.declared_goal_outcome, self.stories, self.impediments) != (
            state,
            goal,
            stories,
            impediments,
        ):
            raise ValueError("Snapshot facts and diagnostics differ from captured sources")
        return self
