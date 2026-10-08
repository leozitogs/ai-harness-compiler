"""Complete criterion dispositions, still proposals awaiting semantic judgment."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
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
]


class GroundingInvariantError(ValueError):
    def __init__(self, code: GroundingErrorCode, message: str) -> None:
        self.code = code
        super().__init__(message)


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
        spec = self.understanding
        atoms = [item for item in self.extraction.atoms if item.kind == "acceptance-criterion"]
        if [item.atom_id for item in self.analysis.criterion_dispositions] != [a.id for a in atoms]:
            raise GroundingInvariantError(
                "criterion-inventory-invalid",
                "Analysis must account for every criterion in extraction order",
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
