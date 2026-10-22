"""Additive intent representation; neither evidence binding nor disposition grants approval."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.semantic_analysis import SourceBinding
from ai_harness_compiler.models.semantic_analysis_v3 import (
    AnalysisProposalV3,
    BoundFindingV3,
    EvidenceText,
    SemanticAnalysisV3,
)


class RequirementV4(Contract):
    """Explicit normative interpretation at any eligible source, without invented triggers."""

    id: Identifier
    kind: Literal["requirement"] = "requirement"
    content: EvidenceText
    normative_force: Literal["required", "prohibited"]
    applicability: EvidenceText | None = None
    note: Text = Field(max_length=1000)

    @property
    def source_atom_ids(self) -> list[str]:
        return list(
            dict.fromkeys(
                self.content.source_atom_ids
                + (self.applicability.source_atom_ids if self.applicability else [])
            )
        )

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())


class ContentRejectionV4(Contract):
    """A rejected instruction fragment is an observation, not project-wide rejection."""

    id: Identifier
    kind: Literal["content-rejection"] = "content-rejection"
    content: EvidenceText
    reason: Literal["untrusted-instruction"] = "untrusted-instruction"
    note: Text = Field(max_length=1000)

    @property
    def source_atom_ids(self) -> list[str]:
        return list(self.content.source_atom_ids)

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())


class AnalysisProposalV4(Contract):
    schema_version: Literal["SemanticAnalysisProposal/v4"] = "SemanticAnalysisProposal/v4"
    # Reuse unchanged criterion/guard/factual-context contracts; never relabel old context.
    project_analysis: AnalysisProposalV3
    requirements: list[RequirementV4] = Field(default_factory=list, max_length=128)
    content_rejections: list[ContentRejectionV4] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def rejection_channels(self) -> Self:
        if any(
            issue.kind == "safe-rejection" and issue.rejection_reason == "untrusted-instruction"
            for issue in self.project_analysis.issues
        ):
            raise ValueError(
                "Untrusted instruction must use content_rejections, not project rejection"
            )
        return self


class SemanticAnalysisV4(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["SemanticAnalysis/v4"] = "SemanticAnalysis/v4"
    extraction: GroundingExtraction
    proposal: AnalysisProposalV4

    @property
    def project_analysis(self) -> SemanticAnalysisV3:
        proposal = AnalysisProposalV4.model_validate(self.proposal.model_dump())
        return SemanticAnalysisV3.model_validate(
            {
                "extraction": self.extraction.model_dump(),
                "proposal": proposal.project_analysis.model_dump(),
            }
        )

    @property
    def sources(self) -> list[SourceBinding]:
        return self.project_analysis.sources

    @property
    def findings(self) -> list[BoundFindingV3 | RequirementV4 | ContentRejectionV4]:
        proposal = AnalysisProposalV4.model_validate(self.proposal.model_dump())
        base = self.project_analysis
        allowed = {a.id for a in compact_context(base.extraction)}
        result: list[BoundFindingV3 | RequirementV4 | ContentRejectionV4] = list(base.findings)
        additional: list[RequirementV4 | ContentRejectionV4] = [
            *proposal.requirements,
            *proposal.content_rejections,
        ]
        for item in additional:
            if not set(item.source_atom_ids).issubset(allowed):
                raise ValueError("New findings require eligible literal atoms, never asset content")
            result.append(item)
        if len({f.id for f in result}) != len(result):
            raise ValueError("All v4 finding identities must be distinct across channels")
        return result

    @property
    def disposition(self) -> Literal["ready", "blocked", "safely-rejected"]:
        # Requirements without stated applicability do not fabricate a blocker.
        # Only project-analysis issues decide project disposition.
        _ = self.findings
        return self.project_analysis.disposition

    @property
    def snapshot_sha256(self) -> str:
        _ = self.findings
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def bound_channels(self) -> Self:
        _ = self.findings
        return self
