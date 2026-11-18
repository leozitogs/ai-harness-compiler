"""Source-bound functional change data; declarations never grant execution authority."""

import re
from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_eval import HumanDeclaration
from ai_harness_compiler.models.understanding import GroundedItem, UnderstandingRequest

ExampleKind = Literal["success", "failure", "boundary"]
EXAMPLE_KINDS: tuple[ExampleKind, ...] = ("success", "failure", "boundary")


class ChangeRuleV1(GroundedItem):
    statement: Text = Field(max_length=4000)
    origin: Literal["declared", "hypothesis"]

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())


class RuleConfirmationV1(HumanDeclaration):
    rule_id: Identifier
    rule_sha256: Digest
    source_sha256: Digest


class BusinessExampleV1(Contract):
    id: Identifier
    rule_id: Identifier
    kind: ExampleKind
    given: Text = Field(max_length=4000)
    when: Text = Field(max_length=2000)
    then: Text = Field(max_length=4000)
    data_declaration: Literal["synthetic-not-privacy-verified"] = "synthetic-not-privacy-verified"


class ExampleExemptionV1(Contract):
    rule_id: Identifier
    kind: ExampleKind
    reason: Text = Field(max_length=2000)


class ChangeQuestionV1(GroundedItem):
    text: Text = Field(max_length=2000)
    rule_ids: list[Identifier] = Field(min_length=1, max_length=64)
    owner: Text
    impact: Literal["rule", "authorization", "outcome", "precedence", "implementation-detail"]

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())


class QuestionDecisionV1(HumanDeclaration):
    question_id: Identifier
    question_sha256: Digest
    source_sha256: Digest
    answer: Text = Field(max_length=4000)


class FunctionalRequirementV1(Contract):
    id: Identifier
    text: Text = Field(max_length=4000)
    rule_ids: list[Identifier] = Field(min_length=1, max_length=64)


class ScenarioBindingV1(Contract):
    id: Identifier
    requirement_id: Identifier
    example_id: Identifier
    test_ref: Text = Field(max_length=512)
    execution_status: Literal["not-run"] = "not-run"

    @model_validator(mode="after")
    def test_locator(self) -> Self:
        # A locator, never a command, import target, executable or claim that the test exists.
        if not re.fullmatch(
            r"tests/(?:[A-Za-z0-9_-]+/)*test_[A-Za-z0-9_-]+\.py"
            r"::test_[A-Za-z0-9_]+",
            self.test_ref,
        ):
            raise ValueError("Test reference must be a relative test-file/function locator")
        return self


def _unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Duplicate {label}")


class FunctionalChangeV1(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["FunctionalChange/v1"] = "FunctionalChange/v1"
    id: Identifier
    revision: int = Field(ge=1)
    source: UnderstandingRequest
    capability_ids: list[Identifier] = Field(min_length=1, max_length=64)
    intent: Text = Field(max_length=4000)
    rules: list[ChangeRuleV1] = Field(min_length=1, max_length=64)
    confirmations: list[RuleConfirmationV1] = Field(default_factory=list, max_length=64)
    examples: list[BusinessExampleV1] = Field(default_factory=list, max_length=512)
    exemptions: list[ExampleExemptionV1] = Field(default_factory=list, max_length=192)
    questions: list[ChangeQuestionV1] = Field(default_factory=list, max_length=64)
    decisions: list[QuestionDecisionV1] = Field(default_factory=list, max_length=64)
    requirements: list[FunctionalRequirementV1] = Field(default_factory=list, max_length=128)
    scenarios: list[ScenarioBindingV1] = Field(default_factory=list, max_length=512)

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def exact_references(self) -> Self:
        # Nested models can be mutated after construction; validate them again at the boundary.
        source = UnderstandingRequest.model_validate(self.source.model_dump())
        references = {r.id: r for r in source.references}
        source_sha256 = canonical_project_digest(source.model_dump())
        capabilities = {c.id for c in source.original_input.backlog}
        _unique(self.capability_ids, "capabilities")
        if not set(self.capability_ids).issubset(capabilities):
            raise ValueError("Change capabilities must belong to its source project")
        _unique(
            [r.id for r in self.rules]
            + [e.id for e in self.examples]
            + [q.id for q in self.questions]
            + [r.id for r in self.requirements]
            + [s.id for s in self.scenarios],
            "change identities",
        )
        rules = {r.id: r for r in self.rules}
        questions = {q.id: q for q in self.questions}
        examples = {e.id: e for e in self.examples}
        requirements = {r.id: r for r in self.requirements}
        for grounded in [*self.rules, *self.questions]:
            _unique(grounded.source_refs, "source references")
            if not set(grounded.source_refs).issubset(references):
                raise ValueError("Unresolved functional source reference")
            if any(
                references[id_].pointer == "/assets"
                or references[id_].pointer.startswith("/assets/")
                for id_ in grounded.source_refs
            ):
                raise ValueError("Asset metadata cannot confirm functional business behavior")
            for id_ in grounded.source_refs:
                parts = references[id_].pointer.split("/")
                if parts[1] == "backlog" and (len(parts) < 3 or not parts[2].isdigit()):
                    raise ValueError("Functional backlog sources require a specific capability")
                if (
                    len(parts) >= 3
                    and parts[1] == "backlog"
                    and parts[2].isdigit()
                    and source.original_input.backlog[int(parts[2])].id not in self.capability_ids
                ):
                    raise ValueError("Functional source belongs to an unselected capability")
        linked: list[ChangeQuestionV1 | FunctionalRequirementV1] = [
            *self.questions,
            *self.requirements,
        ]
        for item in linked:
            _unique(item.rule_ids, "rule references")
            if not set(item.rule_ids).issubset(rules):
                raise ValueError("Unresolved functional rule reference")
        for question in self.questions:
            required = {ref for id_ in question.rule_ids for ref in rules[id_].source_refs}
            if not required.issubset(question.source_refs):
                raise ValueError("Question must preserve sources of all linked rules")
        _unique([c.rule_id for c in self.confirmations], "rule confirmations")
        for confirmation in self.confirmations:
            rule = rules.get(confirmation.rule_id)
            if (
                rule is None
                or confirmation.rule_sha256 != rule.sha256
                or confirmation.source_sha256 != source_sha256
            ):
                raise ValueError("Rule confirmation belongs to different rule/project content")
        _unique([d.question_id for d in self.decisions], "question decisions")
        for decision in self.decisions:
            decided_question = questions.get(decision.question_id)
            if (
                decided_question is None
                or decision.question_sha256 != decided_question.sha256
                or decision.source_sha256 != source_sha256
            ):
                raise ValueError("Question decision belongs to different question/project content")
        for example in self.examples:
            if example.rule_id not in rules:
                raise ValueError("Example must reference an existing rule")
        keys = [f"{e.rule_id}:{e.kind}" for e in self.exemptions]
        _unique(keys, "example exemptions")
        for exemption in self.exemptions:
            if exemption.rule_id not in rules or any(
                e.rule_id == exemption.rule_id and e.kind == exemption.kind for e in self.examples
            ):
                raise ValueError("Exemption must name an existing rule and an absent example kind")
        for scenario in self.scenarios:
            requirement = requirements.get(scenario.requirement_id)
            linked_example = examples.get(scenario.example_id)
            if (
                requirement is None
                or linked_example is None
                or linked_example.rule_id not in requirement.rule_ids
            ):
                raise ValueError("Scenario must link an example to a requirement of its rule")
        return self


class FunctionalChangeReviewV1(HumanDeclaration):
    schema_version: Literal["FunctionalChangeReview/v1"] = "FunctionalChangeReview/v1"
    project_id: Identifier
    change_id: Identifier
    revision: int = Field(ge=1)
    content_sha256: Digest
    decision: Literal["approved", "rejected"]


class ChangeWorkLogV1(Contract):
    """Checklist progress has no test result or functional approval fields."""

    schema_version: Literal["ChangeWorkLog/v1"] = "ChangeWorkLog/v1"
    change_sha256: Digest
    prepared_scenario_ids: list[Identifier] = Field(default_factory=list, max_length=512)

    @model_validator(mode="after")
    def distinct_prepared(self) -> Self:
        _unique(self.prepared_scenario_ids, "prepared scenarios")
        return self
