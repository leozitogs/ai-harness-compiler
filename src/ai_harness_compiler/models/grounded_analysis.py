"""Complete criterion dispositions, still proposals awaiting semantic judgment."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.understanding import (
    ProjectUnderstandingSpec,
    UnderstandingProposal,
)

GroundingErrorCode = Literal[
    "criterion-inventory-invalid",
    "criterion-rule-link-invalid",
    "criterion-requirement-link-invalid",
    "criterion-question-link-invalid",
    "excluded-source-used",
    "declared-quote-invalid",
    "extracted-quote-invalid",
    "proposal-reference-invalid",
]


class GroundingInvariantError(ValueError):
    def __init__(
        self,
        code: GroundingErrorCode,
        message: str,
        atom_ids: list[str] | None = None,
        reason: str = "inventory-mismatch",
        source_ref_ids: list[str] | None = None,
    ) -> None:
        self.code = code
        self.atom_ids = atom_ids or []
        self.reason = reason
        self.source_ref_ids = source_ref_ids or []
        super().__init__(message)


class GroundingDiagnostic(Contract):
    schema_version: Literal["GroundingDiagnostic/v1"] = "GroundingDiagnostic/v1"
    input_sha256: Digest
    proposal_sha256: Digest
    error_code: GroundingErrorCode
    atom_ids: list[Identifier] = Field(default_factory=list, max_length=512)
    source_ref_ids: list[Identifier] = Field(default_factory=list, max_length=128)
    reason: Literal[
        "inventory-mismatch",
        "finding-missing",
        "wrong-origin",
        "quote-mismatch",
        "source-mismatch",
        "wrong-kind",
        "question-not-blocking",
    ]

    @model_validator(mode="after")
    def validate_reason(self) -> Self:
        if len(set(self.atom_ids)) != len(self.atom_ids):
            raise ValueError("Diagnostic atom IDs must be unique")
        if len(set(self.source_ref_ids)) != len(self.source_ref_ids) or not (
            self.atom_ids or self.source_ref_ids
        ):
            raise ValueError("Diagnostic requires unique scoped evidence IDs")
        allowed = {
            "criterion-inventory-invalid": {"inventory-mismatch"},
            "criterion-rule-link-invalid": {
                "finding-missing",
                "wrong-origin",
                "quote-mismatch",
                "source-mismatch",
            },
            "criterion-requirement-link-invalid": {
                "finding-missing",
                "wrong-origin",
                "quote-mismatch",
                "source-mismatch",
                "wrong-kind",
            },
            "criterion-question-link-invalid": {
                "finding-missing",
                "question-not-blocking",
                "source-mismatch",
            },
            "excluded-source-used": set(),
            "declared-quote-invalid": {"quote-mismatch"},
            "extracted-quote-invalid": {"quote-mismatch"},
            "proposal-reference-invalid": {"source-mismatch"},
        }
        if self.reason not in allowed[self.error_code]:
            raise ValueError("Diagnostic reason contradicts error code")
        if self.error_code.startswith("criterion-") and not self.atom_ids:
            raise ValueError("Criterion diagnostic requires criterion atoms")
        if (
            self.error_code
            in {"declared-quote-invalid", "extracted-quote-invalid", "proposal-reference-invalid"}
            and not self.source_ref_ids
        ):
            raise ValueError("Quote diagnostic requires original source references")
        return self


class GroundedRepairInput(Contract):
    extraction: GroundingExtraction
    feedback: GroundingDiagnostic

    @model_validator(mode="after")
    def bind_feedback(self) -> Self:
        allowed = {a.id for a in self.extraction.atoms if a.kind == "acceptance-criterion"}
        allowed_refs = {r.id for r in self.extraction.request.references} - {
            r.source_ref for r in self.extraction.excluded_references
        }
        if (
            self.feedback.input_sha256 != self.extraction.request.original_sha256
            or set(self.feedback.atom_ids) - allowed
            or set(self.feedback.source_ref_ids) - allowed_refs
        ):
            raise ValueError("Repair feedback must bind to original criterion evidence")
        return self


class CriterionDisposition(Contract):
    atom_id: Identifier
    disposition: Literal["business-rule", "requirement", "needs-clarification"]
    finding_ids: list[Identifier] = Field(min_length=1, max_length=32)
    note: Text = Field(max_length=2000)

    @model_validator(mode="after")
    def unique_findings(self) -> Self:
        if len(self.finding_ids) != len(set(self.finding_ids)):
            raise ValueError("Disposition finding IDs must be unique")
        return self


class GroundedAnalysisProposal(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["GroundedAnalysisProposal/v1"] = "GroundedAnalysisProposal/v1"
    proposal: UnderstandingProposal
    criterion_dispositions: list[CriterionDisposition] = Field(min_length=1, max_length=512)


class GroundedAnalysisSpec(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["GroundedAnalysis/v1"] = "GroundedAnalysis/v1"
    extraction: GroundingExtraction
    analysis: GroundedAnalysisProposal
    semantic_status: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"

    @property
    def understanding(self) -> ProjectUnderstandingSpec:
        return ProjectUnderstandingSpec.model_validate(
            {
                "request": self.extraction.request.model_dump(),
                "proposal": self.analysis.proposal.model_dump(),
            }
        )

    @model_validator(mode="after")
    def validate_dispositions(self) -> Self:
        references = {r.id: r.value for r in self.extraction.request.references}
        proposed = self.analysis.proposal
        items = (
            proposed.statements
            + proposed.business_rules
            + proposed.domain_candidates
            + proposed.conflicts
            + proposed.questions
        )
        if any(set(item.source_refs) - references.keys() for item in items):
            eligible = references.keys() - {
                r.source_ref for r in self.extraction.excluded_references
            }
            raise GroundingInvariantError(
                "proposal-reference-invalid",
                "Proposal references do not resolve to original input",
                reason="source-mismatch",
                source_ref_ids=sorted(eligible),
            )
        for quoted_statement in self.analysis.proposal.statements:
            if (
                quoted_statement.status == "declared"
                and not set(quoted_statement.source_refs) - references.keys()
                and not any(
                    quoted_statement.text == references[r] for r in quoted_statement.source_refs
                )
            ):
                raise GroundingInvariantError(
                    "declared-quote-invalid",
                    "Declared quote does not match its original references",
                    reason="quote-mismatch",
                    source_ref_ids=quoted_statement.source_refs,
                )
        for quoted_rule in self.analysis.proposal.business_rules:
            if (
                quoted_rule.origin == "extracted"
                and not set(quoted_rule.source_refs) - references.keys()
                and not any(
                    quoted_rule.description == references[r] for r in quoted_rule.source_refs
                )
            ):
                raise GroundingInvariantError(
                    "extracted-quote-invalid",
                    "Extracted quote does not match its original references",
                    reason="quote-mismatch",
                    source_ref_ids=quoted_rule.source_refs,
                )
        spec = self.understanding
        atoms = [item for item in self.extraction.atoms if item.kind == "acceptance-criterion"]
        if [item.atom_id for item in self.analysis.criterion_dispositions] != [a.id for a in atoms]:
            raise GroundingInvariantError(
                "criterion-inventory-invalid",
                "Analysis must account for every criterion in extraction order",
                [a.id for a in atoms],
            )
        rules = {item.id: item for item in spec.proposal.business_rules}
        statements = {item.id: item for item in spec.proposal.statements}
        questions = {item.id: item for item in spec.proposal.questions}
        for atom, disposition in zip(atoms, self.analysis.criterion_dispositions, strict=True):
            for identifier in disposition.finding_ids:
                if disposition.disposition == "business-rule":
                    rule = rules.get(identifier)
                    if not rule or (
                        rule.origin != "extracted"
                        or rule.description != atom.quote
                        or atom.source_ref not in rule.source_refs
                    ):
                        raise GroundingInvariantError(
                            "criterion-rule-link-invalid",
                            "Rule disposition requires an extracted quoted rule",
                            [atom.id],
                            "finding-missing"
                            if not rule
                            else "wrong-origin"
                            if rule.origin != "extracted"
                            else "quote-mismatch"
                            if rule.description != atom.quote
                            else "source-mismatch",
                        )
                elif disposition.disposition == "requirement":
                    statement = statements.get(identifier)
                    if not statement or (
                        statement.status != "declared"
                        or statement.text != atom.quote
                        or statement.subject not in {"capability", "constraint"}
                        or atom.source_ref not in statement.source_refs
                    ):
                        raise GroundingInvariantError(
                            "criterion-requirement-link-invalid",
                            "Requirement disposition requires a declared quoted finding",
                            [atom.id],
                            "finding-missing"
                            if not statement
                            else "wrong-origin"
                            if statement.status != "declared"
                            else "quote-mismatch"
                            if statement.text != atom.quote
                            else "wrong-kind"
                            if statement.subject not in {"capability", "constraint"}
                            else "source-mismatch",
                        )
                else:
                    question = questions.get(identifier)
                    if (
                        not question
                        or not question.blocking
                        or atom.source_ref not in question.source_refs
                    ):
                        raise GroundingInvariantError(
                            "criterion-question-link-invalid",
                            "Clarification requires a blocking question citing the criterion",
                            [atom.id],
                            "finding-missing"
                            if not question
                            else "question-not-blocking"
                            if not question.blocking
                            else "source-mismatch",
                        )
        excluded = {item.source_ref for item in self.extraction.excluded_references}
        findings = (
            spec.proposal.statements
            + spec.proposal.business_rules
            + spec.proposal.domain_candidates
            + spec.proposal.conflicts
        )
        if any(excluded.intersection(item.source_refs) for item in findings):
            raise GroundingInvariantError(
                "excluded-source-used", "Excluded references cannot support analysis findings"
            )
        return self
