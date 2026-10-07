"""Literal evidence and quotation checks; neither establishes semantic correctness."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.understanding import (
    ProjectUnderstandingSpec,
    UnderstandingRequest,
    reference_value,
)

EvidenceKind = Literal[
    "conception",
    "branding",
    "constraint",
    "backlog-description",
    "acceptance-criterion",
    "domain-declaration",
    "asset-metadata",
]


class EvidenceAtom(Contract):
    id: Identifier
    source_ref: Identifier
    pointer: Text = Field(max_length=512)
    quote: str = Field(min_length=1, max_length=16_384)
    kind: EvidenceKind
    content_trust: Literal["untrusted-data"] = "untrusted-data"


class ExcludedReference(Contract):
    source_ref: Identifier
    reason: Literal["external-claim-not-verified", "supplied-profile-not-reanalyzed"]


def literal_evidence(
    request: UnderstandingRequest,
) -> tuple[list[EvidenceAtom], list[ExcludedReference]]:
    """Enumerate known manifest sections, without opening assets or interpreting text."""
    from ai_harness_compiler.understanding import prepare_understanding

    canonical = prepare_understanding(request.original_input)
    if request != canonical:
        raise ValueError("Grounding requires the complete canonical input reference inventory")
    atoms: list[EvidenceAtom] = []
    excluded: list[ExcludedReference] = []
    data = request.original_input.model_dump()

    def add_leaves(value: object, pointer: str, ref: str, kind: EvidenceKind) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                token = key.replace("~", "~0").replace("/", "~1")
                add_leaves(child, f"{pointer}/{token}", ref, kind)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                add_leaves(child, f"{pointer}/{index}", ref, kind)
        elif value is not None:
            if len(atoms) >= 512:
                raise ValueError("Grounding atom limit exceeded")
            atoms.append(
                EvidenceAtom(
                    id=f"atom-{len(atoms) + 1}",
                    source_ref=ref,
                    pointer=pointer,
                    quote=reference_value(request.original_input, pointer),
                    kind=kind,
                )
            )

    for ref in request.references:
        pointer = ref.pointer
        if pointer.startswith("/evidence_pack/"):
            excluded.append(
                ExcludedReference(
                    source_ref=ref.id,
                    reason="external-claim-not-verified",
                )
            )
            continue
        if pointer == "/domain_profile":
            excluded.append(
                ExcludedReference(
                    source_ref=ref.id,
                    reason="supplied-profile-not-reanalyzed",
                )
            )
            continue
        kind: EvidenceKind
        if pointer == "/conception":
            kind = "conception"
        elif pointer == "/branding":
            kind = "branding"
        elif pointer == "/constraints":
            kind = "constraint"
        elif pointer == "/domain":
            kind = "domain-declaration"
        elif pointer == "/assets":
            kind = "asset-metadata"
        elif "/acceptance_criteria/" in pointer:
            kind = "acceptance-criterion"
        else:
            kind = "backlog-description"
        if pointer in {"/branding", "/constraints", "/assets"}:
            add_leaves(data[pointer[1:]], pointer, ref.id, kind)
        else:
            add_leaves(ref.value, pointer, ref.id, kind)
    return atoms, excluded


class GroundingExtraction(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["GroundingExtraction/v1"] = "GroundingExtraction/v1"
    request: UnderstandingRequest
    atoms: list[EvidenceAtom] = Field(min_length=1, max_length=512)
    excluded_references: list[ExcludedReference] = Field(default_factory=list, max_length=128)
    asset_contents: Literal["not-read"] = "not-read"
    semantic_status: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def preserve_inventory(self) -> Self:
        atoms, excluded = literal_evidence(self.request)
        if self.atoms != atoms or self.excluded_references != excluded:
            raise ValueError("Grounding must preserve the complete literal evidence inventory")
        return self


class CriterionQuotation(Contract):
    atom_id: Identifier
    quoted_by_rules: list[Identifier] = Field(default_factory=list, max_length=128)


def criterion_quotations(
    extraction: GroundingExtraction,
    spec: ProjectUnderstandingSpec,
) -> list[CriterionQuotation]:
    return [
        CriterionQuotation(
            atom_id=atom.id,
            quoted_by_rules=[
                rule.id
                for rule in spec.proposal.business_rules
                if rule.origin == "extracted"
                and rule.description == atom.quote
                and atom.source_ref in rule.source_refs
            ],
        )
        for atom in extraction.atoms
        if atom.kind == "acceptance-criterion"
    ]


class GroundingQuotationReport(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["GroundingQuotationReport/v1"] = "GroundingQuotationReport/v1"
    extraction: GroundingExtraction
    understanding: ProjectUnderstandingSpec
    criteria: list[CriterionQuotation] = Field(min_length=1, max_length=512)
    semantic_status: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def verify_quotations(self) -> Self:
        if self.extraction.request != self.understanding.request:
            raise ValueError("Grounding and proposal must share the original input snapshot")
        if self.criteria != criterion_quotations(self.extraction, self.understanding):
            raise ValueError("Criterion quotation report contradicts the actual proposal")
        return self
