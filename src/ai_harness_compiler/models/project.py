"""Input and canonical project model; declarations are not inferred facts."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text


class Branding(Contract):
    audience: list[Text] = Field(default_factory=list)
    tone: list[Text] = Field(default_factory=list)
    principles: list[Text] = Field(default_factory=list)
    visual_constraints: list[Text] = Field(default_factory=list)


class Constraints(Contract):
    technical: list[Text] = Field(default_factory=list)
    security: list[Text] = Field(default_factory=list)
    business: list[Text] = Field(default_factory=list)
    max_build_cost_usd: float = Field(default=0, ge=0, allow_inf_nan=False)


class BacklogItem(Contract):
    id: Identifier
    title: Text
    description: Text
    acceptance_criteria: list[Text] = Field(min_length=1)
    depends_on: list[Identifier] = Field(default_factory=list)
    inputs: list[Text] = Field(default_factory=list)
    outputs: list[Text] = Field(default_factory=list)
    data_owner: Text | None = None
    side_effects: list[Text] = Field(default_factory=list)
    risk: Literal["unknown", "low", "medium", "high"] = "unknown"
    implementation: Literal["undecided", "deterministic", "llm", "rag", "agent"] = "undecided"


class Asset(Contract):
    path: Text
    description: Text


class ProjectInput(Contract):
    schema_version: Literal["ProjectInput/v1"] = "ProjectInput/v1"
    id: Identifier
    name: Text
    conception: Text
    domain: Text | None = None
    branding: Branding = Field(default_factory=Branding)
    backlog: list[BacklogItem] = Field(min_length=1)
    constraints: Constraints = Field(default_factory=Constraints)
    assets: list[Asset] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_backlog_ids(self) -> Self:
        ids = [item.id for item in self.backlog]
        if len(ids) != len(set(ids)):
            raise ValueError("Backlog IDs must be unique")
        return self


class Evidence(Contract):
    id: Identifier
    source: Text
    claim: Text
    kind: Literal["declared", "derived", "research"]


class DomainProfile(Contract):
    primary: Text | None = None
    status: Literal["declared", "DOMAIN_UNCERTAIN"]
    confidence: float | None = Field(default=None, ge=0, le=1, allow_inf_nan=False)
    evidence_ids: list[Identifier] = Field(default_factory=list)


class ProjectDNA(Contract):
    schema_version: Literal["ProjectDNA/v1"] = "ProjectDNA/v1"
    project: ProjectInput
    domain: DomainProfile
    evidence: list[Evidence] = Field(min_length=1)
    unknowns: list[Text] = Field(default_factory=list)
