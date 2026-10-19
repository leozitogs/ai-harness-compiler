"""Component-specific provenance and explicit guards; no generated rule execution."""

import hashlib
from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.compact_analysis import ContextInterpretation, compact_context
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.semantic_analysis import (
    AnalysisIssue,
    BoundFinding,
    MaterialQuestion,
    SourceBinding,
)


class EvidenceText(Contract):
    text: Text = Field(max_length=2000)
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def distinct_sources(self) -> Self:
        if len(set(self.source_atom_ids)) != len(self.source_atom_ids):
            raise ValueError("Component evidence cannot duplicate source atoms")
        return self


class CriterionV3(Contract):
    source_atom_id: Identifier
    kind: Literal["business-rule", "requirement", "needs-clarification"]
    condition: EvidenceText | None = None
    outcome: EvidenceText | None = None
    exceptions: list[EvidenceText] = Field(default_factory=list, max_length=8)
    note: Text = Field(max_length=1000)
    question: MaterialQuestion | None = None
    uncertainties: list[MaterialQuestion] = Field(default_factory=list, max_length=4)

    @model_validator(mode="after")
    def consistent_kind(self) -> Self:
        if self.kind == "business-rule":
            if self.condition is None or self.outcome is None or self.question is not None:
                raise ValueError("Rule requires independently sourced condition and outcome")
        elif self.condition is not None or self.outcome is not None or self.exceptions:
            raise ValueError("Non-rule cannot claim rule components")
        if (self.kind == "needs-clarification") != (self.question is not None):
            raise ValueError("Only clarification has a primary question")
        if self.question is not None and not self.question.blocking:
            raise ValueError("Clarification requires material business impact")
        return self


class GuardSpec(Contract):
    id: Identifier
    condition: EvidenceText
    effect: EvidenceText
    target_scope: Literal["project", "criteria"]
    target_criterion_atom_ids: list[Identifier] = Field(default_factory=list, max_length=64)
    note: Text = Field(max_length=1000)

    @model_validator(mode="after")
    def unique_targets(self) -> Self:
        if len(self.target_criterion_atom_ids) != len(set(self.target_criterion_atom_ids)):
            raise ValueError("Guard targets must be distinct criterion atoms")
        if (self.target_scope == "criteria") != bool(self.target_criterion_atom_ids):
            raise ValueError(
                "Criterion scope needs targets; project scope has no criterion targets"
            )
        return self


class AnalysisProposalV3(Contract):
    schema_version: Literal["SemanticAnalysisProposal/v3"] = "SemanticAnalysisProposal/v3"
    criteria: list[CriterionV3] = Field(min_length=1, max_length=64)
    guards: list[GuardSpec] = Field(default_factory=list, max_length=32)
    context_findings: list[ContextInterpretation] = Field(default_factory=list, max_length=32)
    issues: list[AnalysisIssue] = Field(default_factory=list, max_length=16)


class ComponentBinding(Contract):
    name: Literal["condition", "outcome", "exception"]
    index: int | None = Field(default=None, ge=0, le=7)
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def valid_placement(self) -> Self:
        if (self.name == "exception") != (self.index is not None):
            raise ValueError("Only exception bindings have an index")
        if len(self.source_atom_ids) != len(set(self.source_atom_ids)):
            raise ValueError("Component binding sources must be unique")
        return self


class BoundFindingV3(BoundFinding):
    component_bindings: list[ComponentBinding] = Field(default_factory=list, max_length=10)
    guard_target_atom_ids: list[Identifier] = Field(default_factory=list, max_length=64)
    guard_target_scope: Literal["project", "criteria"] | None = None

    @model_validator(mode="after")
    def consistent_components(self) -> Self:
        keys = [(item.name, item.index) for item in self.component_bindings]
        if len(keys) != len(set(keys)):
            raise ValueError("Finding cannot duplicate a component placement")
        if self.kind == "rule":
            expected: list[tuple[str, int | None]] = [("condition", None), ("outcome", None)]
            expected += [("exception", index) for index in range(len(self.exceptions))]
            if keys != expected:
                raise ValueError("Rule finding must preserve every ordered component binding")
        elif self.component_bindings or self.guard_target_atom_ids or self.guard_target_scope:
            raise ValueError("Only rule findings carry components or guard targets")
        if any(
            not set(item.source_atom_ids).issubset(self.source_atom_ids)
            for item in self.component_bindings
        ):
            raise ValueError("Component bindings must remain in the overall source inventory")
        if len(self.guard_target_atom_ids) != len(set(self.guard_target_atom_ids)):
            raise ValueError("Guard finding target mappings must be unique")
        if (self.guard_target_scope == "criteria") != bool(self.guard_target_atom_ids):
            raise ValueError("Only criterion-scoped guards carry criterion targets")
        return self


class SemanticAnalysisV3(Contract):
    schema_version: Literal["SemanticAnalysis/v3"] = "SemanticAnalysis/v3"
    extraction: GroundingExtraction
    proposal: AnalysisProposalV3

    @property
    def sources(self) -> list[SourceBinding]:
        extraction = GroundingExtraction.model_validate(self.extraction.model_dump())
        return [
            SourceBinding(
                atom_id=atom.id,
                source_ref=atom.source_ref,
                pointer=atom.pointer,
                quote=atom.quote,
                quote_sha256=hashlib.sha256(atom.quote.encode()).hexdigest(),
            )
            for atom in compact_context(extraction)
        ]

    @property
    def findings(self) -> list[BoundFindingV3]:
        extraction = GroundingExtraction.model_validate(self.extraction.model_dump())
        proposal = AnalysisProposalV3.model_validate(self.proposal.model_dump())
        context = compact_context(extraction)
        allowed = {atom.id for atom in context}
        criteria = [atom for atom in extraction.atoms if atom.kind == "acceptance-criterion"]
        if [item.source_atom_id for item in proposal.criteria] != [atom.id for atom in criteria]:
            raise ValueError(
                "Every criterion identity and position must match the original inventory"
            )
        criterion_ids = {atom.id for atom in criteria}

        def components(
            condition: EvidenceText, outcome: EvidenceText, exceptions: list[EvidenceText]
        ) -> list[ComponentBinding]:
            values: list[tuple[str, int | None, EvidenceText]] = [
                ("condition", None, condition),
                ("outcome", None, outcome),
            ]
            values += [("exception", index, item) for index, item in enumerate(exceptions)]
            bindings = []
            for name, index, value in values:
                if not set(value.source_atom_ids).issubset(allowed):
                    raise ValueError("Rule component references an ineligible original source")
                bindings.append(
                    ComponentBinding.model_validate(
                        {
                            "name": name,
                            "index": index,
                            "source_atom_ids": value.source_atom_ids,
                        }
                    )
                )
            return bindings

        def union(bindings: list[ComponentBinding], anchor: str | None = None) -> list[str]:
            ids = [anchor] if anchor is not None else []
            ids += [id_ for item in bindings for id_ in item.source_atom_ids]
            return list(dict.fromkeys(ids))

        result = []
        for number, (atom, intent) in enumerate(zip(criteria, proposal.criteria, strict=True), 1):
            bindings = []
            if intent.kind == "business-rule":
                assert intent.condition is not None and intent.outcome is not None
                bindings = components(intent.condition, intent.outcome, intent.exceptions)
            kind: Literal["rule", "requirement", "question"] = (
                "rule"
                if intent.kind == "business-rule"
                else "requirement"
                if intent.kind == "requirement"
                else "question"
            )
            result.append(
                BoundFindingV3(
                    id=f"criterion-{number}",
                    kind=kind,
                    text=intent.question.text if intent.question else atom.quote,
                    condition=intent.condition.text if intent.condition else None,
                    outcome=intent.outcome.text if intent.outcome else None,
                    exceptions=[item.text for item in intent.exceptions],
                    impact=intent.question.impact if intent.question else None,
                    rationale=intent.question.rationale if intent.question else intent.note,
                    source_atom_ids=union(bindings, atom.id),
                    component_bindings=bindings,
                )
            )
            for index, question in enumerate(intent.uncertainties, 1):
                result.append(
                    BoundFindingV3(
                        id=f"uncertainty-{number}-{index}",
                        kind="question",
                        text=question.text,
                        impact=question.impact,
                        rationale=question.rationale,
                        source_atom_ids=[atom.id],
                    )
                )
        for guard in proposal.guards:
            if not set(guard.target_criterion_atom_ids).issubset(criterion_ids):
                raise ValueError("Guard targets must be actual criterion atoms")
            bindings = components(guard.condition, guard.effect, [])
            result.append(
                BoundFindingV3(
                    id=guard.id,
                    kind="rule",
                    text=guard.effect.text,
                    condition=guard.condition.text,
                    outcome=guard.effect.text,
                    rationale=guard.note,
                    source_atom_ids=union(bindings),
                    component_bindings=bindings,
                    guard_target_atom_ids=guard.target_criterion_atom_ids,
                    guard_target_scope=guard.target_scope,
                )
            )

        def bind(indices: list[int]) -> list[str]:
            if len(indices) != len(set(indices)) or any(
                type(i) is not int or not 0 <= i < len(context) for i in indices
            ):
                raise ValueError("Context positions must resolve uniquely to original atoms")
            return [context[i].id for i in indices]

        for number, finding in enumerate(proposal.context_findings, 1):
            result.append(
                BoundFindingV3(
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
                BoundFindingV3(
                    id=f"issue-{number}",
                    kind="rejection" if issue.kind == "safe-rejection" else issue.kind,
                    text=issue.text,
                    impact=issue.impact,
                    rationale=issue.rationale,
                    rejection_reason=issue.rejection_reason,
                    source_atom_ids=ids,
                )
            )
        if len({finding.id for finding in result}) != len(result):
            raise ValueError("All generated finding IDs and guard IDs must be distinct")
        return result

    @property
    def disposition(self) -> Literal["ready", "blocked", "safely-rejected"]:
        findings = self.findings
        if any(finding.kind == "rejection" for finding in findings):
            return "safely-rejected"
        if any(
            finding.kind == "conflict"
            or (finding.kind == "question" and finding.impact != "implementation-detail")
            for finding in findings
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
