"""Model-owned interpretations and compiler-owned literal citations, without promotion."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Text
from ai_harness_compiler.models.evidence import Digest
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec

Subject = Literal[
    "purpose", "audience", "positioning", "tone", "domain", "entity", "capability", "constraint"
]


class CompactContext(Contract):
    kind: Literal[
        "conception", "branding", "constraint", "backlog-description", "domain-declaration"
    ]
    text: str = Field(min_length=1, max_length=16_384)


class CompactInput(Contract):
    schema_version: Literal["CompactUnderstandingInput/v1"] = "CompactUnderstandingInput/v1"
    input_sha256: Digest
    context: list[CompactContext] = Field(min_length=1, max_length=512)
    criteria: list[str] = Field(min_length=1, max_length=64)
    unread_asset_count: int = Field(ge=0)
    content_trust: Literal["untrusted-data"] = "untrusted-data"


def compact_input(extraction: GroundingExtraction) -> CompactInput:
    extraction = GroundingExtraction.model_validate(extraction.model_dump())
    return CompactInput.model_validate(
        {
            "input_sha256": extraction.request.original_sha256,
            "context": [
                {"kind": a.kind, "text": a.quote}
                for a in extraction.atoms
                if a.kind not in {"acceptance-criterion", "asset-metadata"}
            ],
            "criteria": [a.quote for a in extraction.atoms if a.kind == "acceptance-criterion"],
            "unread_asset_count": len(extraction.request.original_input.assets),
        }
    )


class CriterionInterpretation(Contract):
    kind: Literal["business-rule", "requirement", "needs-clarification"]
    condition: Text | None = Field(default=None, max_length=2000)
    outcome: Text | None = Field(default=None, max_length=2000)
    question: Text | None = Field(default=None, max_length=2000)
    note: Text = Field(max_length=1000)
    uncertainties: list[Text] = Field(default_factory=list, max_length=1)

    @model_validator(mode="after")
    def consistent_kind(self) -> Self:
        if self.kind == "business-rule":
            if not self.condition or not self.outcome or self.question is not None:
                raise ValueError("Business interpretation needs condition/outcome only")
        elif self.condition is not None or self.outcome is not None:
            raise ValueError("Non-rule cannot claim condition/outcome")
        if (self.kind == "needs-clarification") != (self.question is not None):
            raise ValueError("Clarification requires a question; other kinds cannot claim one")
        return self


class ContextInterpretation(Contract):
    subject: Subject
    text: Text = Field(max_length=2000)
    note: Text = Field(max_length=1000)
    context_indices: list[int] = Field(min_length=1, max_length=32)


class ContextIssue(Contract):
    kind: Literal["question", "conflict"]
    text: Text = Field(max_length=2000)
    context_indices: list[int] = Field(min_length=1, max_length=32)


class CompactProposal(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["CompactUnderstandingProposal/v1"] = "CompactUnderstandingProposal/v1"
    criteria: list[CriterionInterpretation] = Field(min_length=1, max_length=64)
    context_findings: list[ContextInterpretation] = Field(default_factory=list, max_length=32)
    issues: list[ContextIssue] = Field(default_factory=list, max_length=16)


class CompactAnalysisSpec(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["CompactUnderstanding/v1"] = "CompactUnderstanding/v1"
    extraction: GroundingExtraction
    interpretation: CompactProposal
    semantic_status: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"

    @property
    def understanding(self) -> ProjectUnderstandingSpec:
        extraction = GroundingExtraction.model_validate(self.extraction.model_dump())
        interpretation = CompactProposal.model_validate(self.interpretation.model_dump())
        context = [
            a for a in extraction.atoms if a.kind not in {"acceptance-criterion", "asset-metadata"}
        ]
        criteria = [a for a in extraction.atoms if a.kind == "acceptance-criterion"]
        if len(criteria) != len(interpretation.criteria):
            raise ValueError("Compact interpretation must account for every criterion position")
        proposal: dict[str, list[dict[str, object]]] = {
            key: []
            for key in [
                "statements",
                "business_rules",
                "domain_candidates",
                "questions",
                "conflicts",
            ]
        }
        for number, (atom, intent) in enumerate(
            zip(criteria, interpretation.criteria, strict=True), 1
        ):
            common: dict[str, object] = {
                "id": f"criterion-{number}",
                "source_refs": [atom.source_ref],
            }
            if intent.kind == "business-rule":
                proposal["business_rules"].append(
                    common
                    | {
                        "description": atom.quote,
                        "condition": intent.condition,
                        "outcome": intent.outcome,
                        "origin": "hypothesis",
                    }
                )
            elif intent.kind == "requirement":
                proposal["statements"].append(
                    common | {"subject": "constraint", "text": atom.quote, "status": "declared"}
                )
            else:
                proposal["questions"].append(
                    common | {"question": intent.question, "blocking": True}
                )
            for uncertainty in intent.uncertainties:
                proposal["questions"].append(
                    {
                        "id": f"uncertainty-{number}",
                        "source_refs": [atom.source_ref],
                        "question": f"Confirmar: {uncertainty}",
                        "blocking": True,
                    }
                )

        def refs(indices: list[int]) -> list[str]:
            if len(indices) != len(set(indices)) or any(
                type(i) is not int or not 0 <= i < len(context) for i in indices
            ):
                raise ValueError("Compact context positions must resolve uniquely")
            return list(dict.fromkeys(context[i].source_ref for i in indices))

        for number, finding in enumerate(interpretation.context_findings, 1):
            common = {"id": f"context-{number}", "source_refs": refs(finding.context_indices)}
            if finding.subject == "domain":
                proposal["domain_candidates"].append(
                    common | {"domain": finding.text, "rationale": finding.note}
                )
            else:
                proposal["statements"].append(
                    common
                    | {"subject": finding.subject, "text": finding.text, "status": "hypothesis"}
                )
        for number, issue in enumerate(interpretation.issues, 1):
            common = {"id": f"issue-{number}", "source_refs": refs(issue.context_indices)}
            if issue.kind == "conflict":
                proposal["conflicts"].append(common | {"description": issue.text})
            else:
                proposal["questions"].append(common | {"question": issue.text, "blocking": True})
        return ProjectUnderstandingSpec.model_validate(
            {"request": extraction.request.model_dump(), "proposal": proposal}
        )

    @model_validator(mode="after")
    def validate_projection(self) -> Self:
        compact_input(self.extraction)
        _ = self.understanding
        return self
