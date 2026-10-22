"""Shared exact evidence inventory for advisory audits and independent human reviews."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import BoundFindingV3
from ai_harness_compiler.models.semantic_analysis_v4 import (
    ContentRejectionV4,
    RequirementV4,
    SemanticAnalysisV4,
)

ComponentName = Literal[
    "content",
    "condition",
    "outcome",
    "exception",
    "normative-force",
    "applicability",
    "rejection-reason",
]
ComponentKey = tuple[str, ComponentName, int | None]


class FindingIdentityV4(Contract):
    finding_id: Identifier
    finding_sha256: Digest
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=512)

    @model_validator(mode="after")
    def distinct_sources(self) -> Self:
        if len(set(self.source_atom_ids)) != len(self.source_atom_ids):
            raise ValueError("Finding sources must be unique")
        return self


class ComponentIdentityV4(Contract):
    finding_id: Identifier
    component_name: ComponentName
    component_index: int | None = Field(default=None, ge=0, le=7)
    component_sha256: Digest
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=512)

    @property
    def key(self) -> ComponentKey:
        return self.finding_id, self.component_name, self.component_index

    @model_validator(mode="after")
    def distinct_identity(self) -> Self:
        if (self.component_name == "exception") != (self.component_index is not None):
            raise ValueError("Only exception components have an index")
        if len(set(self.source_atom_ids)) != len(self.source_atom_ids):
            raise ValueError("Component sources must be unique")
        return self


class EvidenceComponentV4(Contract):
    finding_id: Identifier
    name: ComponentName
    index: int | None = Field(default=None, ge=0, le=7)
    text: Text
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=512)

    @property
    def identity(self) -> ComponentIdentityV4:
        return ComponentIdentityV4(
            finding_id=self.finding_id,
            component_name=self.name,
            component_index=self.index,
            component_sha256=canonical_project_digest(self.model_dump()),
            source_atom_ids=self.source_atom_ids,
        )


def component_inventory_v4(analysis: SemanticAnalysisV4) -> list[EvidenceComponentV4]:
    analysis = SemanticAnalysisV4.model_validate(analysis.model_dump())
    result = []

    def add(
        id_: str, name: ComponentName, text: str, ids: list[str], index: int | None = None
    ) -> None:
        result.append(
            EvidenceComponentV4(
                finding_id=id_, name=name, index=index, text=text, source_atom_ids=ids
            )
        )

    for finding in analysis.findings:
        if isinstance(finding, RequirementV4):
            add(finding.id, "content", finding.content.text, finding.content.source_atom_ids)
            add(
                finding.id,
                "normative-force",
                finding.normative_force,
                finding.content.source_atom_ids,
            )
            if finding.applicability:
                add(
                    finding.id,
                    "applicability",
                    finding.applicability.text,
                    finding.applicability.source_atom_ids,
                )
        elif isinstance(finding, ContentRejectionV4):
            add(finding.id, "content", finding.content.text, finding.content.source_atom_ids)
            add(finding.id, "rejection-reason", finding.reason, finding.content.source_atom_ids)
        elif finding.kind == "rule":
            for component in finding.component_bindings:
                text = (
                    finding.condition
                    if component.name == "condition"
                    else finding.outcome
                    if component.name == "outcome"
                    else finding.exceptions[component.index or 0]
                )
                assert text is not None
                add(finding.id, component.name, text, component.source_atom_ids, component.index)
        else:
            add(finding.id, "content", finding.text, finding.source_atom_ids)
            if finding.rejection_reason:
                add(
                    finding.id,
                    "rejection-reason",
                    finding.rejection_reason,
                    finding.source_atom_ids,
                )
    return result


def coverage_source_ids(finding: BoundFindingV3 | RequirementV4 | ContentRejectionV4) -> list[str]:
    # A condition/applicability source alone cannot cover the requirement's normative content.
    return (
        finding.content.source_atom_ids
        if isinstance(finding, RequirementV4)
        else finding.source_atom_ids
    )
