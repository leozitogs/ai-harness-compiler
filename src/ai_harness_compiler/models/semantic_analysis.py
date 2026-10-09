"""V2 interpretations retain literal atom bindings and independent release gates."""

import hashlib
from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.compact_analysis import (
    ContextInterpretation,
    Subject,
    compact_context,
)
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.grounding import GroundingExtraction

Impact = Literal["rule", "authorization", "outcome", "precedence", "implementation-detail"]


class MaterialQuestion(Contract):
    text: Text = Field(max_length=2000)
    impact: Impact
    rationale: Text = Field(max_length=1000)

    @property
    def blocking(self) -> bool:
        return self.impact != "implementation-detail"


class CriterionAnalysis(Contract):
    source_atom_id: Identifier
    kind: Literal["business-rule", "requirement", "needs-clarification"]
    condition: Text | None = Field(default=None, max_length=2000)
    outcome: Text | None = Field(default=None, max_length=2000)
    exceptions: list[Text] = Field(default_factory=list, max_length=8)
    note: Text = Field(max_length=1000)
    question: MaterialQuestion | None = None
    uncertainties: list[MaterialQuestion] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def consistent_kind(self) -> Self:
        if self.kind == "business-rule":
            if not self.condition or not self.outcome or self.question is not None:
                raise ValueError("Rule requires condition/outcome and no primary question")
        elif self.condition is not None or self.outcome is not None or self.exceptions:
            raise ValueError("Non-rule cannot assert executable rule components")
        if (self.kind == "needs-clarification") != (self.question is not None):
            raise ValueError("Only clarification has a primary question")
        if self.question is not None and not self.question.blocking:
            raise ValueError("Clarification requires material business impact")
        return self


class AnalysisIssue(Contract):
    kind: Literal["question", "conflict", "safe-rejection"]
    text: Text = Field(max_length=2000)
    context_indices: list[int] = Field(min_length=1, max_length=32)
    rationale: Text = Field(max_length=1000)
    impact: Impact | None = None
    rejection_reason: Literal["untrusted-instruction", "unread-required-source"] | None = None

    @model_validator(mode="after")
    def consistent_issue(self) -> Self:
        if (self.kind == "question") != (self.impact is not None):
            raise ValueError("Only questions declare an impact")
        if (self.kind == "safe-rejection") != (self.rejection_reason is not None):
            raise ValueError("Safe rejection requires a grounded reason")
        return self


class AnalysisProposal(Contract):
    schema_version: Literal["SemanticAnalysisProposal/v2"] = "SemanticAnalysisProposal/v2"
    criteria: list[CriterionAnalysis] = Field(min_length=1, max_length=64)
    context_findings: list[ContextInterpretation] = Field(default_factory=list, max_length=32)
    issues: list[AnalysisIssue] = Field(default_factory=list, max_length=16)


class SourceBinding(Contract):
    atom_id: Identifier
    source_ref: Identifier
    pointer: Text
    quote: str = Field(min_length=1)
    quote_sha256: Digest


class BoundFinding(Contract):
    id: Identifier
    kind: Literal["rule", "requirement", "statement", "domain", "question", "conflict", "rejection"]
    text: Text
    condition: Text | None = None
    outcome: Text | None = None
    exceptions: list[Text] = Field(default_factory=list)
    impact: Impact | None = None
    rationale: Text
    source_atom_ids: list[Identifier] = Field(min_length=1)
    subject: Subject | None = None
    rejection_reason: Literal["untrusted-instruction", "unread-required-source"] | None = None

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())


class SemanticAnalysis(Contract):
    schema_version: Literal["SemanticAnalysis/v2"] = "SemanticAnalysis/v2"
    extraction: GroundingExtraction
    proposal: AnalysisProposal

    @property
    def sources(self) -> list[SourceBinding]:
        extraction = GroundingExtraction.model_validate(self.extraction.model_dump())
        return [
            SourceBinding(
                atom_id=a.id,
                source_ref=a.source_ref,
                pointer=a.pointer,
                quote=a.quote,
                quote_sha256=hashlib.sha256(a.quote.encode()).hexdigest(),
            )
            for a in compact_context(extraction)
        ]

    @property
    def findings(self) -> list[BoundFinding]:
        extraction = GroundingExtraction.model_validate(self.extraction.model_dump())
        proposal = AnalysisProposal.model_validate(self.proposal.model_dump())
        context = compact_context(extraction)
        criteria = [a for a in extraction.atoms if a.kind == "acceptance-criterion"]
        if len(criteria) != len(proposal.criteria):
            raise ValueError("Every original criterion position must be interpreted")
        result: list[BoundFinding] = []
        for number, (atom, intent) in enumerate(zip(criteria, proposal.criteria, strict=True), 1):
            if intent.source_atom_id != atom.id:
                raise ValueError("Criterion identity/order must match the original atom inventory")
            kind = {
                "business-rule": "rule",
                "requirement": "requirement",
                "needs-clarification": "question",
            }[intent.kind]
            result.append(
                BoundFinding.model_validate(
                    dict(
                        id=f"criterion-{number}",
                        kind=kind,
                        text=intent.question.text if intent.question else atom.quote,
                        condition=intent.condition,
                        outcome=intent.outcome,
                        exceptions=intent.exceptions,
                        impact=intent.question.impact if intent.question else None,
                        rationale=intent.question.rationale if intent.question else intent.note,
                        source_atom_ids=[atom.id],
                    )
                )
            )
            for index, question in enumerate(intent.uncertainties, 1):
                result.append(
                    BoundFinding(
                        id=f"uncertainty-{number}-{index}",
                        kind="question",
                        text=question.text,
                        impact=question.impact,
                        rationale=question.rationale,
                        source_atom_ids=[atom.id],
                    )
                )

        def bind(indices: list[int]) -> list[str]:
            if len(indices) != len(set(indices)) or any(
                type(i) is not int or not 0 <= i < len(context) for i in indices
            ):
                raise ValueError("Context positions must resolve uniquely to exact atoms")
            return [context[i].id for i in indices]

        for number, finding in enumerate(proposal.context_findings, 1):
            result.append(
                BoundFinding(
                    id=f"context-{number}",
                    kind="domain" if finding.subject == "domain" else "statement",
                    text=finding.text,
                    rationale=finding.note,
                    subject=finding.subject,
                    source_atom_ids=bind(finding.context_indices),
                )
            )
        for number, issue in enumerate(proposal.issues, 1):
            ids = bind(issue.context_indices)
            if issue.kind == "conflict" and len(ids) < 2:
                raise ValueError("Conflict requires two distinct literal atoms")
            result.append(
                BoundFinding(
                    id=f"issue-{number}",
                    kind="rejection" if issue.kind == "safe-rejection" else issue.kind,
                    text=issue.text,
                    impact=issue.impact,
                    rationale=issue.rationale,
                    rejection_reason=issue.rejection_reason,
                    source_atom_ids=ids,
                )
            )
        return result

    @property
    def disposition(self) -> Literal["ready", "blocked", "safely-rejected"]:
        findings = self.findings
        if any(f.kind == "rejection" for f in findings):
            return "safely-rejected"
        if any(
            f.kind == "conflict" or (f.kind == "question" and f.impact != "implementation-detail")
            for f in findings
        ):
            return "blocked"
        return "ready"

    @property
    def snapshot_sha256(self) -> str:
        _ = self.findings
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def validate_bindings(self) -> Self:
        _ = self.findings
        return self
