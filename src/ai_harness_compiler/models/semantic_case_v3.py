"""New expectation identity; no implicit migration of approval or rejection scope."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_eval import HumanDeclaration


class AssessmentObligationV3(Contract):
    id: Identifier
    source_pointer: Text
    quote: Text
    disposition: Literal["rule", "required-question", "requirement", "statement", "domain"]


class AssessmentCaseV3(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["AssessmentCase/v3"] = "AssessmentCase/v3"
    id: Identifier
    project: ProjectInput
    expected_behavior: Literal["ready", "blocked", "safely-rejected"]
    obligations: list[AssessmentObligationV3] = Field(default_factory=list, max_length=64)
    requires_conflict: bool = False
    conflict_source_pointers: list[Text] = Field(default_factory=list, max_length=32)
    required_project_rejection_pointers: list[Text] = Field(default_factory=list, max_length=32)
    required_content_rejection_pointers: list[Text] = Field(default_factory=list, max_length=32)
    expectations_approval: HumanDeclaration | None = None

    @property
    def snapshot_sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def grounded_expectations(self) -> Self:
        # Reuse historical literal/behavior invariants, not its rejection semantics.
        data = self.model_dump(exclude={"schema_version", "required_content_rejection_pointers"})
        data["refusal_source_pointers"] = data.pop("required_project_rejection_pointers")
        for obligation in data["obligations"]:
            if obligation["disposition"] in {"statement", "domain"}:
                obligation["disposition"] = (
                    "requirement"  # Literal validation only; not a migration.
                )
        AssessmentCase.model_validate(data)
        pointers = self.required_content_rejection_pointers
        eligible = {
            a.pointer for a in extract_grounding(self.project).atoms if a.kind != "asset-metadata"
        }
        if len(pointers) != len(set(pointers)) or not set(pointers).issubset(eligible):
            raise ValueError(
                "Content rejection expectations require unique eligible original sources"
            )
        return self
