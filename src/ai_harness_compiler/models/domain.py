"""Multidimensional profiles distinguish supplied hypotheses from declarations."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text


class DataProfile(Contract):
    data_types: list[Text] = Field(default_factory=list)
    sensitivity: Literal["unknown", "public", "internal", "confidential", "restricted"] = "unknown"
    contains_pii: bool | None = None

    @model_validator(mode="after")
    def unique_types(self) -> Self:
        if len(self.data_types) != len(set(self.data_types)):
            raise ValueError("Data types must be unique")
        return self


class RiskProfile(Contract):
    level: Literal["unknown", "low", "medium", "high"] = "unknown"
    categories: list[
        Literal[
            "privacy",
            "security",
            "regulatory",
            "hallucination",
            "excessive-agency",
            "availability",
            "cost",
        ]
    ] = Field(default_factory=list)

    @model_validator(mode="after")
    def unique_categories(self) -> Self:
        if len(self.categories) != len(set(self.categories)):
            raise ValueError("Risk categories must be unique")
        return self


class DomainHypothesis(Contract):
    domain: Text
    rationale: Text
    evidence_ids: list[Identifier] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_evidence(self) -> Self:
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("Hypothesis evidence references must be unique")
        return self


class DomainProfile(Contract):
    schema_version: Literal["DomainProfile/v1"] = "DomainProfile/v1"
    primary: Text | None = None
    secondary: list[Text] = Field(default_factory=list)
    archetype: Text | None = None
    data: DataProfile = Field(default_factory=DataProfile)
    risk: RiskProfile = Field(default_factory=RiskProfile)
    status: Literal["declared", "hypothesis", "DOMAIN_UNCERTAIN"]
    origin: Literal["user-declaration", "supplied-hypothesis", "unknown"]
    confidence: None = None
    rationale: Text | None = None
    evidence_ids: list[Identifier] = Field(default_factory=list)
    hypotheses: list[DomainHypothesis] = Field(default_factory=list)

    @model_validator(mode="after")
    def classification_invariants(self) -> Self:
        origins = {
            "declared": "user-declaration",
            "hypothesis": "supplied-hypothesis",
            "DOMAIN_UNCERTAIN": "unknown",
        }
        if self.origin != origins[self.status]:
            raise ValueError("Classification status and origin are incompatible")
        if self.status == "DOMAIN_UNCERTAIN":
            if self.primary is not None:
                raise ValueError("Uncertain domain cannot assert a primary classification")
        elif self.primary is None or not self.evidence_ids:
            raise ValueError("Declared/hypothesis profile requires primary domain and evidence")
        if self.status == "hypothesis" and self.rationale is None:
            raise ValueError("Hypothesis requires a rationale")
        if len(self.secondary) != len(set(self.secondary)) or self.primary in self.secondary:
            raise ValueError("Secondary domains must be unique and different from primary")
        if len(self.evidence_ids) != len(set(self.evidence_ids)):
            raise ValueError("Domain evidence references must be unique")
        candidates = [item.domain for item in self.hypotheses]
        if len(candidates) != len(set(candidates)):
            raise ValueError("Domain hypotheses must be unique")
        return self
