"""Grounded proposals and review metadata, separate from provider or execution authority."""

import json
import re
from typing import Any, Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.project import ProjectInput


def reference_value(project: ProjectInput, pointer: str) -> str:
    if not pointer.startswith("/") or re.search(r"~(?![01])", pointer):
        raise ValueError("Input reference must use an RFC6901 pointer")
    value: Any = project.model_dump()
    for raw in pointer[1:].split("/"):
        key = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(value, dict) and key in value:
            value = value[key]
        elif isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", key):
            index = int(key)
            if index >= len(value):
                raise ValueError("Unresolved input reference")
            value = value[index]
        else:
            raise ValueError("Unresolved input reference")
    return (
        value
        if isinstance(value, str)
        else json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )


class InputReference(Contract):
    id: Identifier
    project_id: Identifier
    pointer: Text = Field(max_length=512)
    value: Text = Field(max_length=16_384)
    content_trust: Literal["untrusted-data"] = "untrusted-data"


class UnderstandingRequest(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["UnderstandingRequest/v1"] = "UnderstandingRequest/v1"
    original_input: ProjectInput
    original_sha256: Digest
    references: list[InputReference] = Field(min_length=1, max_length=128)

    @model_validator(mode="after")
    def validate_snapshot(self) -> Self:
        if self.original_sha256 != canonical_project_digest(self.original_input.model_dump()):
            raise ValueError("Understanding snapshot digest differs from original input")
        if len({item.id for item in self.references}) != len(self.references):
            raise ValueError("Input reference IDs must be unique")
        if len({item.pointer for item in self.references}) != len(self.references):
            raise ValueError("Input reference pointers must be unique")
        for item in self.references:
            if item.project_id != self.original_input.id:
                raise ValueError("Input reference belongs to another project")
            if item.value != reference_value(self.original_input, item.pointer):
                raise ValueError("Input reference differs from its original value")
        return self


class GroundedItem(Contract):
    id: Identifier
    source_refs: list[Identifier] = Field(min_length=1, max_length=32)

    @model_validator(mode="after")
    def unique_refs(self) -> Self:
        if len(self.source_refs) != len(set(self.source_refs)):
            raise ValueError("Source references must be unique")
        return self


class UnderstandingStatement(GroundedItem):
    subject: Literal[
        "purpose", "audience", "positioning", "tone", "domain", "entity", "capability", "constraint"
    ]
    text: Text
    status: Literal["declared", "hypothesis"]


class BusinessRule(GroundedItem):
    description: Text
    condition: Text
    outcome: Text
    exceptions: list[Text] = Field(default_factory=list)
    origin: Literal["extracted", "hypothesis"]


class DomainCandidate(GroundedItem):
    domain: Text
    rationale: Text
    confidence: None = None


class UnderstandingConflict(GroundedItem):
    description: Text
    source_refs: list[Identifier] = Field(min_length=2, max_length=32)


class UnderstandingQuestion(GroundedItem):
    question: Text
    blocking: bool = True


class UnderstandingProposal(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["UnderstandingProposal/v1"] = "UnderstandingProposal/v1"
    statements: list[UnderstandingStatement] = Field(default_factory=list, max_length=128)
    business_rules: list[BusinessRule] = Field(default_factory=list, max_length=128)
    domain_candidates: list[DomainCandidate] = Field(default_factory=list, max_length=16)
    conflicts: list[UnderstandingConflict] = Field(default_factory=list, max_length=64)
    questions: list[UnderstandingQuestion] = Field(default_factory=list, max_length=128)

    @model_validator(mode="after")
    def unique_items(self) -> Self:
        items = (
            self.statements
            + self.business_rules
            + self.domain_candidates
            + self.conflicts
            + self.questions
        )
        if not items:
            raise ValueError("Understanding proposal must contain grounded findings or questions")
        if len({item.id for item in items}) != len(items):
            raise ValueError("Understanding item IDs must be globally unique")
        domains = [item.domain for item in self.domain_candidates]
        if len(domains) != len(set(domains)):
            raise ValueError("Domain candidates must be unique")
        return self


class ReviewAnswer(Contract):
    item_id: Identifier
    text: Text


class UnderstandingReview(Contract):
    decision: Literal["approved", "rejected"]
    reviewer: Text
    note: Text
    input_sha256: Digest
    proposal_sha256: Digest
    answers: list[ReviewAnswer] = Field(default_factory=list)
    resolutions: list[ReviewAnswer] = Field(default_factory=list)


class ProjectUnderstandingSpec(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["ProjectUnderstanding/v1"] = "ProjectUnderstanding/v1"
    request: UnderstandingRequest
    proposal: UnderstandingProposal
    review: UnderstandingReview | None = None

    @model_validator(mode="after")
    def validate_proposal(self) -> Self:
        references = {item.id: item for item in self.request.references}
        items = (
            self.proposal.statements
            + self.proposal.business_rules
            + self.proposal.domain_candidates
            + self.proposal.conflicts
            + self.proposal.questions
        )
        for item in items:
            if set(item.source_refs) - references.keys():
                raise ValueError("Unresolved understanding source reference")
        for statement in self.proposal.statements:
            if statement.status == "declared" and not any(
                statement.text == references[ref].value for ref in statement.source_refs
            ):
                raise ValueError("Declared statement must preserve a quoted input value")
        for rule in self.proposal.business_rules:
            if rule.origin == "extracted" and not any(
                rule.description == references[ref].value for ref in rule.source_refs
            ):
                raise ValueError("Extracted rule description must preserve a quoted input value")
        if self.review:
            if (
                self.review.input_sha256 != self.request.original_sha256
                or self.review.proposal_sha256
                != canonical_project_digest(self.proposal.model_dump())
            ):
                raise ValueError("Understanding review is stale or belongs to another snapshot")
            questions = {item.id for item in self.proposal.questions}
            conflicts = {item.id for item in self.proposal.conflicts}
            answers = {item.item_id for item in self.review.answers}
            resolutions = {item.item_id for item in self.review.resolutions}
            if len(answers) != len(self.review.answers) or len(resolutions) != len(
                self.review.resolutions
            ):
                raise ValueError("Duplicate review answers or resolutions")
            if answers - questions or resolutions - conflicts:
                raise ValueError("Review answer/resolution must reference a proposal item")
            if self.review.decision == "approved":
                blocking = {item.id for item in self.proposal.questions if item.blocking}
                if blocking - answers or conflicts - resolutions:
                    raise ValueError("Approval requires blocking questions and conflicts resolved")
        return self
