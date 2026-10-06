"""Input and canonical project model; declarations are not inferred facts."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.domain import DomainProfile
from ai_harness_compiler.models.evidence import (
    Evidence,
    EvidencePack,
    EvidenceRegistry,
    canonical_project_digest,
)


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
    evidence_pack: EvidencePack | None = None
    domain_profile: DomainProfile | None = None

    @model_validator(mode="after")
    def unique_backlog_ids(self) -> Self:
        ids = [item.id for item in self.backlog]
        if len(ids) != len(set(ids)):
            raise ValueError("Backlog IDs must be unique")
        if self.evidence_pack:
            for item in self.evidence_pack.evidence:
                if item.capability_id and item.capability_id not in ids:
                    raise ValueError("Evidence capability must exist in the backlog")
        if self.domain and self.domain_profile:
            if (
                self.domain_profile.status != "declared"
                or self.domain_profile.primary != self.domain
            ):
                raise ValueError("Legacy domain and supplied profile must agree as declarations")
        return self


class ProjectDNA(EvidenceRegistry):
    schema_version: Literal["ProjectDNA/v3"] = "ProjectDNA/v3"
    project: ProjectInput
    domain: DomainProfile
    evidence: list[Evidence] = Field(min_length=1)
    unknowns: list[Text] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_evidence_scope(self) -> Self:
        evidence = {item.id: item for item in self.evidence}
        source_records = {item.id: item for item in self.sources}
        manifest = source_records.get("project-manifest")
        if manifest is None or (
            manifest.location != "project.yaml"
            or manifest.origin != "user-declaration"
            or manifest.sha256 != canonical_project_digest(self.project.model_dump())
        ):
            raise ValueError("Canonical manifest provenance does not match the project input")
        declared = {
            "project-intent": (
                "project.yaml#/conception",
                self.project.conception,
                "project",
                None,
            ),
            **{
                f"backlog-{index + 1}": (
                    f"project.yaml#/backlog/{index}",
                    item.description,
                    "capability",
                    item.id,
                )
                for index, item in enumerate(self.project.backlog)
            },
        }
        if self.project.domain:
            declared["domain-declaration"] = (
                "project.yaml#/domain",
                self.project.domain,
                "domain",
                None,
            )
        if self.project.domain_profile:
            declared["domain-profile"] = (
                "project.yaml#/domain_profile",
                self.project.domain_profile.model_dump_json(),
                "domain",
                None,
            )
            if self.domain != self.project.domain_profile:
                raise ValueError("Canonical profile must preserve the supplied domain profile")
        elif self.project.domain:
            expected_profile = DomainProfile(
                primary=self.project.domain,
                status="declared",
                origin="user-declaration",
                evidence_ids=["domain-declaration"],
            )
            if self.domain.model_dump(exclude={"evidence_ids"}) != expected_profile.model_dump(
                exclude={"evidence_ids"}
            ):
                raise ValueError("Legacy declaration cannot imply additional classifications")
        elif self.domain != DomainProfile(status="DOMAIN_UNCERTAIN", origin="unknown"):
            raise ValueError("No supplied classification must remain DOMAIN_UNCERTAIN")
        for identifier, expected in declared.items():
            entry = evidence.get(identifier)
            if entry is None or (
                entry.source_id != "project-manifest"
                or entry.kind != "declared"
                or (entry.source, entry.claim, entry.scope, entry.capability_id) != expected
            ):
                raise ValueError("Canonical evidence differs from its declared input")
        for entry in self.evidence:
            if entry.source_id == "project-manifest" and entry.id not in declared:
                raise ValueError("Canonical manifest only supports known declarations")
        ids = {item.id for item in self.project.backlog}
        for item in self.evidence:
            if item.capability_id and item.capability_id not in ids:
                raise ValueError("Evidence capability must exist in the project")
        references = list(self.domain.evidence_ids)
        for hypothesis in self.domain.hypotheses:
            references.extend(hypothesis.evidence_ids)
        if self.domain.status == "declared" and not references:
            raise ValueError("Declared domain requires evidence")
        for reference in references:
            if reference not in evidence or evidence[reference].scope != "domain":
                raise ValueError("Domain evidence reference is missing or incompatible")
            if (
                reference in self.domain.evidence_ids
                and self.domain.status == "declared"
                and evidence[reference].kind != "declared"
            ):
                raise ValueError("Declared domain requires declared evidence")
            source = source_records[evidence[reference].source_id]
            if source.verification_status == "rejected":
                raise ValueError("Rejected source cannot support a domain reference")
        return self
