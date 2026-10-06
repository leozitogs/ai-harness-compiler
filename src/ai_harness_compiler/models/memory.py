"""Engineering memory contracts: decisions, documents and evidence-backed experiences."""

from typing import Annotated, Literal, Self

from pydantic import Field, StringConstraints, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text

RecordID = Annotated[str, StringConstraints(pattern=r"^(DE|DOC|ADR|INC|LES|RUN|EXP)-[0-9]{4}$")]
Kind = Literal["DE", "DOC", "ADR", "INC", "LES", "RUN", "EXP"]
Status = Literal["draft", "active", "verified", "superseded"]


class MemoryEvidence(Contract):
    source: Text
    note: Text
    outcome: Literal["not-run", "observed", "passed", "failed"] = "not-run"
    command: str | None = None
    sha256: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")] | None = None


class RecordDraft(Contract):
    id: RecordID
    kind: Kind
    project_id: Identifier
    title: Text = Field(max_length=200)
    summary: Text = Field(max_length=2000)
    context: Text = Field(max_length=8000)
    author: Text
    tags: list[Text] = Field(default_factory=list, max_length=20)
    decision: str | None = Field(default=None, max_length=8000)
    alternatives: list[Text] = Field(default_factory=list)
    consequences: list[Text] = Field(default_factory=list)
    challenge: str | None = Field(default=None, max_length=8000)
    root_cause: str | None = Field(default=None, max_length=8000)
    attempts: list[Text] = Field(default_factory=list)
    resolution: str | None = Field(default=None, max_length=8000)
    lesson: str | None = Field(default=None, max_length=8000)
    applicability: list[Text] = Field(default_factory=list)
    limitations: list[Text] = Field(default_factory=list)
    procedure: list[Text] = Field(default_factory=list)
    evidence: list[MemoryEvidence] = Field(default_factory=list, max_length=20)
    related: list[RecordID] = Field(default_factory=list)
    supersedes: RecordID | None = None

    @model_validator(mode="after")
    def validate_content(self) -> Self:
        if not self.id.startswith(self.kind + "-"):
            raise ValueError("Record ID prefix must match its kind")
        if self.kind in {"DE", "ADR"} and not (self.decision or "").strip():
            raise ValueError("Decisions require an explicit decision")
        if self.kind == "INC" and not (self.challenge or "").strip():
            raise ValueError("Incidents require a challenge/problem")
        if self.kind == "LES" and not all(
            [
                (self.lesson or "").strip(),
                (self.resolution or "").strip(),
                self.applicability,
                self.limitations,
                self.evidence,
            ]
        ):
            raise ValueError("Lessons require resolution, applicability, limitations and evidence")
        if self.kind == "RUN" and not self.procedure:
            raise ValueError("Runbooks require procedure steps")
        links = self.related + ([self.supersedes] if self.supersedes else [])
        if self.id in links or len(self.related) != len(set(self.related)):
            raise ValueError("Self references and duplicate relationships are forbidden")
        return self


class MemoryRecord(RecordDraft):
    schema_version: Literal["EngineeringMemory/v1"] = "EngineeringMemory/v1"
    revision: int = Field(ge=1)
    status: Status = "draft"
    created_at: Text
    updated_at: Text
    reviewed_by: Text | None = None
    review_note: Text | None = None

    @model_validator(mode="after")
    def validate_promotion(self) -> Self:
        if self.status != "draft" and not (self.reviewed_by and self.review_note):
            raise ValueError("Promoted records require an explicit reviewer and review note")
        if self.status == "verified":
            if self.kind not in {"INC", "LES", "RUN", "EXP"}:
                raise ValueError("Verified is reserved for experiences, procedures and experiments")
            if not any(
                item.outcome in {"passed", "observed"} and item.sha256 for item in self.evidence
            ):
                raise ValueError(
                    "Verification requires observed/passed evidence with a source digest"
                )
            if self.kind == "INC" and not (self.root_cause and self.resolution):
                raise ValueError("Verified incidents require a cause and resolution")
        if self.status == "active" and self.kind in {"INC", "LES"}:
            raise ValueError("Incidents and lessons must be verified, not merely active")
        return self
