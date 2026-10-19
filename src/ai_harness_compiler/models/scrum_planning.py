"""Proposals are derived advice, never commands or human acceptance."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.scrum import SprintSnapshot


class ScrumActionProposal(Contract):
    schema_version: Literal["ScrumActionProposal/v1"] = "ScrumActionProposal/v1"
    id: Identifier
    kind: Literal["refinement", "planning", "review"]
    goal: Text
    story_ids: list[Identifier] = Field(max_length=64)
    dependencies: list[Identifier] = Field(default_factory=list, max_length=128)
    acceptance_criteria: list[Text] = Field(default_factory=list, max_length=512)
    evidence_ids: list[Identifier] = Field(min_length=1, max_length=256)
    diagnostic_ids: list[Identifier] = Field(default_factory=list, max_length=1024)
    recommendation: Text
    alternatives: list[Text] = Field(min_length=2, max_length=4)
    decision_recipient: Literal["human-product-owner", "developers"]
    capacity: Literal["unknown"] = "unknown"
    execution: Literal["not-authorized"] = "not-authorized"
    acceptance: Literal["not-established"] = "not-established"


class ScrumPlanningReport(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["ScrumPlanningReport/v1"] = "ScrumPlanningReport/v1"
    snapshot: SprintSnapshot
    proposals: list[ScrumActionProposal] = Field(min_length=2, max_length=66)
    authority: Literal["proposal-only"] = "proposal-only"
    sprint_started: Literal[False] = False
    backlog_modified: Literal[False] = False

    @model_validator(mode="after")
    def grounded_proposals(self) -> Self:
        from ai_harness_compiler.scrum_planning import derive_proposals

        snapshot = SprintSnapshot.model_validate(self.snapshot.model_dump())
        if self.proposals != derive_proposals(snapshot):
            raise ValueError("Scrum proposals differ from captured evidence")
        return self
