"""Operational model preference is distinct from semantic qualification."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Text


class ModelEndpoint(Contract):
    provider: Literal["codex-cli", "ollama"]
    model: str = Field(pattern=r"^[A-Za-z0-9][\w./:-]{0,199}$")


class ModelPolicy(Contract):
    schema_version: Literal["ModelPolicy/v1"] = "ModelPolicy/v1"
    primary: ModelEndpoint
    local_alternative: ModelEndpoint
    selection_status: Literal["preferred-development"] = "preferred-development"
    model_qualification: Literal["not-established"] = "not-established"
    fallback_policy: Literal["explicit-only"] = "explicit-only"
    role_policy: Literal["inherit-primary"] = "inherit-primary"
    rationale: Text
    evidence_sources: list[Text] = Field(min_length=1, max_length=20)
    limitations: list[Text] = Field(min_length=1, max_length=20)

    @model_validator(mode="after")
    def consistent_alternative(self) -> Self:
        if self.local_alternative.provider != "ollama":
            raise ValueError("Local alternative must use the local provider")
        if self.local_alternative == self.primary:
            raise ValueError("Alternative must differ from primary")
        return self

    def for_role(self, role: str) -> ModelEndpoint:
        if role not in {
            "understanding",
            "analyst",
            "architect",
            "engineer",
            "quality",
            "security",
            "delivery",
        }:
            raise ValueError("Unknown model role")
        policy = ModelPolicy.model_validate(self.model_dump())
        return ModelEndpoint.model_validate(policy.primary.model_dump())

    def endpoint(self, provider: str) -> ModelEndpoint:
        policy = ModelPolicy.model_validate(self.model_dump())
        for endpoint in (policy.primary, policy.local_alternative):
            if endpoint.provider == provider:
                return ModelEndpoint.model_validate(endpoint.model_dump())
        raise ValueError("No default model registered for the requested provider")
