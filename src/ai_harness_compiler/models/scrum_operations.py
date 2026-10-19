"""Narrow, explicit operation intent; report approval is not authorization."""

from typing import Annotated, Literal, Self

from pydantic import ConfigDict, Field, StringConstraints, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.scrum import RepositoryName, instant
from ai_harness_compiler.models.scrum_planning import ScrumPlanningReport
from ai_harness_compiler.scrum_observer import decode_document

OperationLabel = Literal["nexo:needs-refinement", "nexo:needs-capacity", "nexo:needs-evidence"]
OperationState = Literal[
    "prepared", "authorized", "attempted", "observed", "uncertain", "blocked", "cancelled"
]
Reason = Literal[
    "prepared",
    "human-authorized",
    "human-cancelled",
    "dispatch-recorded",
    "desired-state-observed",
    "remote-changed",
    "authorization-expired",
    "source-changed",
    "preflight-unavailable",
    "write-or-observation-uncertain",
    "effect-not-established",
]
LabelName = Annotated[str, StringConstraints(min_length=1, max_length=100)]


class RemoteIssueState(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["RemoteIssueState/v1"] = "RemoteIssueState/v1"
    repository: RepositoryName
    number: int = Field(ge=1)
    node_id: Text = Field(max_length=160)
    observed_at: Text
    updated_at: Text
    state: Literal["open", "closed"]
    title_sha256: Digest
    body_sha256: Digest
    labels: list[LabelName] = Field(max_length=256)
    milestone_id: int | None = Field(default=None, ge=1)
    assignee_ids: list[int] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def canonical_state(self) -> Self:
        if instant(self.updated_at) > instant(self.observed_at):
            raise ValueError("Remote update is later than observation")
        if self.labels != sorted(set(self.labels)):
            raise ValueError("Remote labels must be sorted and unique")
        if self.assignee_ids != sorted(set(self.assignee_ids)) or any(
            type(value) is not int or value < 1 for value in self.assignee_ids
        ):
            raise ValueError("Remote assignees must be sorted positive IDs")
        return self

    @property
    def revision(self) -> str:
        data = self.model_dump(exclude={"observed_at"})
        return canonical_project_digest(data)


class ScrumOperationPlan(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["ScrumOperationPlan/v1"] = "ScrumOperationPlan/v1"
    kind: Literal["add-issue-label"] = "add-issue-label"
    report: ScrumPlanningReport
    proposal_id: Identifier
    story_id: Identifier
    label: OperationLabel
    expected: RemoteIssueState

    @property
    def operation_sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def scoped_action(self) -> Self:
        report = ScrumPlanningReport.model_validate(self.report.model_dump())
        expected = RemoteIssueState.model_validate(self.expected.model_dump())
        proposals = [p for p in report.proposals if p.id == self.proposal_id]
        labels = {
            "refinement": "nexo:needs-refinement",
            "planning": "nexo:needs-capacity",
            "review": "nexo:needs-evidence",
        }
        if len(proposals) != 1 or self.story_id not in proposals[0].story_ids:
            raise ValueError("Operation target must belong to the referenced proposal")
        if self.label != labels[proposals[0].kind]:
            raise ValueError("Label is outside the referenced proposal's operation policy")
        observation = report.snapshot.observation
        if expected.repository != observation.repository or expected.state != "open":
            raise ValueError("Operation must target an open issue in the observed repository")
        story = next(s for s in report.snapshot.stories if s.id == self.story_id)
        issues = [
            s
            for s in observation.sources
            if s.kind == "issue"
            and s.number == expected.number
            and s.id in story.evidence_ids
            and s.status == "observed"
        ]
        if len(issues) != 1:
            raise ValueError("Operation requires the story's captured issue evidence")
        issue = decode_document(issues[0].content or "")
        if issue["state"] != "OPEN" or instant(issue["updatedAt"]) != instant(expected.updated_at):
            raise ValueError("Expected issue revision differs from captured lifecycle evidence")
        if self.label in expected.labels:
            raise ValueError("Proposed label already exists; no operation is required")
        if instant(expected.observed_at) < instant(issues[0].observed_at):
            raise ValueError("Expected remote state predates the captured issue")
        return self


class OperationAuthorization(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["OperationAuthorization/v1"] = "OperationAuthorization/v1"
    operation_sha256: Digest
    actor: Literal["human-product-owner"] = "human-product-owner"
    issued_at: Text
    expires_at: Text
    comment: Text = Field(max_length=1000)

    @model_validator(mode="after")
    def bounded_lifetime(self) -> Self:
        seconds = (instant(self.expires_at) - instant(self.issued_at)).total_seconds()
        if not 0 < seconds <= 3600:
            raise ValueError("Authorization lifetime must be positive and at most one hour")
        return self


class OperationReceipt(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["OperationReceipt/v1"] = "OperationReceipt/v1"
    operation_sha256: Digest
    sequence: int = Field(ge=1)
    previous_sha256: Digest | None = None
    state: OperationState
    recorded_at: Text
    reason: Reason
    authorization: OperationAuthorization | None = None
    remote: RemoteIssueState | None = None

    @property
    def receipt_sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def scoped_receipt(self) -> Self:
        instant(self.recorded_at)
        if (self.sequence == 1) != (self.previous_sha256 is None):
            raise ValueError("Only the first receipt has no predecessor")
        if self.authorization is not None:
            auth = OperationAuthorization.model_validate(self.authorization.model_dump())
            if self.state != "authorized" or auth.operation_sha256 != self.operation_sha256:
                raise ValueError("Authorization must bind the authorized operation")
            if auth.issued_at != self.recorded_at:
                raise ValueError("Authorization receipt must use its issue time")
        elif self.state == "authorized":
            raise ValueError("Authorized receipts require explicit action authorization")
        if self.state == "observed" and self.remote is None:
            raise ValueError("Observed receipts require remote evidence")
        return self
