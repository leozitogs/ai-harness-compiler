"""Evidence provenance and scope are contracts, never proof of truth or network actions."""

import hashlib
import json
import re
from datetime import datetime
from typing import Annotated, Any, Literal, Self

from pydantic import Field, StringConstraints, field_validator, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text

Digest = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]


def canonical_project_digest(payload: dict[str, Any]) -> str:
    content = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


class SourceRecord(Contract):
    id: Identifier
    location: Text
    origin: Literal["user-declaration", "external-research", "compiler-derived"]
    sha256: Digest | None = None
    verification_status: Literal["unverified", "verified", "rejected"] = "unverified"
    collected_at: Text | None = None
    verified_at: Text | None = None
    verified_by: Text | None = None

    @field_validator("collected_at", "verified_at")
    @classmethod
    def timezone_timestamp(cls, value: str | None) -> str | None:
        if value is None:
            return None
        if not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value
        ):
            raise ValueError("Provenance timestamp must be RFC3339 with a timezone")
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    @model_validator(mode="after")
    def validate_verification(self) -> Self:
        if self.origin == "external-research" and not self.collected_at:
            raise ValueError("External research requires a collection timestamp")
        if self.verification_status == "verified":
            if not (self.sha256 and self.verified_by and self.verified_at):
                raise ValueError("Verified source requires digest, reviewer and review timestamp")
        elif self.verified_by or self.verified_at:
            raise ValueError("Unverified/rejected sources cannot carry verification approval")
        if self.collected_at and self.verified_at:
            collected = datetime.fromisoformat(self.collected_at.replace("Z", "+00:00"))
            verified = datetime.fromisoformat(self.verified_at.replace("Z", "+00:00"))
            if verified < collected:
                raise ValueError("Source verification cannot precede collection")
        return self


class Evidence(Contract):
    id: Identifier
    source_id: Identifier
    source: Text
    claim: Text
    kind: Literal["declared", "derived", "research"]
    scope: Literal["project", "domain", "capability"]
    capability_id: Identifier | None = None

    @model_validator(mode="after")
    def validate_scope(self) -> Self:
        if (self.scope == "capability") != (self.capability_id is not None):
            raise ValueError("Only capability-scoped evidence requires a capability ID")
        return self


class EvidenceRegistry(Contract):
    sources: list[SourceRecord] = Field(min_length=1)
    evidence: list[Evidence] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_sources(self) -> Self:
        sources = {item.id: item for item in self.sources}
        if len(sources) != len(self.sources):
            raise ValueError("Source IDs must be unique")
        if len({item.id for item in self.evidence}) != len(self.evidence):
            raise ValueError("Evidence IDs must be unique")
        origins = {
            "declared": "user-declaration",
            "research": "external-research",
            "derived": "compiler-derived",
        }
        for item in self.evidence:
            if item.source_id not in sources:
                raise ValueError("Unresolved source reference")
            source = sources[item.source_id]
            if origins[item.kind] != source.origin:
                raise ValueError("Evidence kind is incompatible with source origin")
            if item.source.partition("#")[0] != source.location.partition("#")[0]:
                raise ValueError("Evidence locator is incompatible with source location")
        return self


class EvidencePack(EvidenceRegistry):
    schema_version: Literal["EvidencePack/v1"] = "EvidencePack/v1"
