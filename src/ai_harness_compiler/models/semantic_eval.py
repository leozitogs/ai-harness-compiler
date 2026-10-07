"""Artifact evaluation contracts; semantic approval is separate from schema validity."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec, reference_value

CriterionID = Literal[
    "rule-coverage",
    "citation-support",
    "conflict-validity",
    "asset-bounds",
    "uncertainty",
    "project-understanding",
]
CRITERIA: tuple[CriterionID, ...] = (
    "rule-coverage",
    "citation-support",
    "conflict-validity",
    "asset-bounds",
    "uncertainty",
    "project-understanding",
)
Verdict = Literal["not-run", "pass", "fail", "error"]


def semantic_snapshot_digest(project: ProjectInput) -> str:
    """Detect renamed clones across eval splits without changing canonical input provenance."""
    content = project.model_dump()
    content.pop("id")
    content.pop("name")
    return canonical_project_digest(content)


class RubricCriterion(Contract):
    id: CriterionID
    description: Text


class HumanDeclaration(Contract):
    reviewer: Text
    note: Text
    authority: Literal["human-declared-not-authenticated"] = "human-declared-not-authenticated"


class UnderstandingRubric(Contract):
    schema_version: Literal["UnderstandingRubric/v1"] = "UnderstandingRubric/v1"
    id: Identifier
    version: Identifier
    criteria: list[RubricCriterion] = Field(min_length=6, max_length=6)
    acceptance: Literal["all-criteria-pass-no-critical-failure"] = (
        "all-criteria-pass-no-critical-failure"
    )
    approval: HumanDeclaration | None = None

    @model_validator(mode="after")
    def complete_criteria(self) -> Self:
        if {item.id for item in self.criteria} != set(CRITERIA):
            raise ValueError("Rubric must contain every criterion exactly once")
        return self


class ExpectedRule(Contract):
    id: Identifier
    source_pointer: Text
    quote: Text


class UnderstandingEvalCase(Contract):
    id: Identifier
    category: Identifier
    project: ProjectInput
    required_rules: list[ExpectedRule] = Field(min_length=1, max_length=64)
    expected_conflicts: Literal["none", "present", "unspecified"] = "none"
    requires_blocking_question: bool = False
    review_guidance: Text

    @model_validator(mode="after")
    def grounded_expectations(self) -> Self:
        if len({item.id for item in self.required_rules}) != len(self.required_rules):
            raise ValueError("Required rule IDs must be unique")
        if len({item.source_pointer for item in self.required_rules}) != len(self.required_rules):
            raise ValueError("Required rule pointers must be unique")
        for rule in self.required_rules:
            if reference_value(self.project, rule.source_pointer) != rule.quote:
                raise ValueError("Required rule quote differs from the original input")
        return self


class UnderstandingEvalSuite(Contract):
    schema_version: Literal["UnderstandingEvalSuite/v1"] = "UnderstandingEvalSuite/v1"
    id: Identifier
    version: Identifier
    split: Literal["development", "holdout"]
    cases: list[UnderstandingEvalCase] = Field(min_length=8, max_length=64)

    @model_validator(mode="after")
    def unique_cases(self) -> Self:
        for values in (
            [case.id for case in self.cases],
            [case.project.id for case in self.cases],
            [semantic_snapshot_digest(case.project) for case in self.cases],
        ):
            if len(values) != len(set(values)):
                raise ValueError("Suite cases and project snapshots must be distinct")
        return self


class FrozenUnderstandingCorpus(Contract):
    schema_version: Literal["FrozenUnderstandingCorpus/v1"] = "FrozenUnderstandingCorpus/v1"
    version: Identifier
    artifacts: dict[Literal["rubric.json", "development.json", "holdout.json"], Digest]
    expectation_status: Literal["proposed-human-review-required"] = "proposed-human-review-required"

    @model_validator(mode="after")
    def all_artifacts(self) -> Self:
        if set(self.artifacts) != {"rubric.json", "development.json", "holdout.json"}:
            raise ValueError("Frozen corpus must bind both splits and rubric")
        return self


class SemanticCheck(Contract):
    criterion: CriterionID
    outcome: Literal["not-run", "pass", "fail"]
    note: Text


class RuleCoverage(Contract):
    requirement_id: Identifier
    business_rule_id: Identifier


class ItemSupport(Contract):
    item_id: Identifier
    source_refs: list[Identifier] = Field(min_length=1, max_length=32)
    outcome: Literal["pass", "fail"]
    note: Text


class SemanticReview(HumanDeclaration):
    case_sha256: Digest
    rubric_sha256: Digest
    proposal_sha256: Digest
    checks: list[SemanticCheck] = Field(min_length=6, max_length=6)
    coverage: list[RuleCoverage] = Field(default_factory=list, max_length=64)
    support: list[ItemSupport] = Field(default_factory=list, max_length=512)

    @model_validator(mode="after")
    def complete_checks(self) -> Self:
        if {item.criterion for item in self.checks} != set(CRITERIA):
            raise ValueError("Human review must address every criterion exactly once")
        if len({item.requirement_id for item in self.coverage}) != len(self.coverage):
            raise ValueError("Each requirement can have only one review mapping")
        if len({item.item_id for item in self.support}) != len(self.support):
            raise ValueError("Each item can have only one support judgment")
        return self


def case_checks(
    case: UnderstandingEvalCase, spec: ProjectUnderstandingSpec, review: SemanticReview | None
) -> list[SemanticCheck]:
    automatic: dict[CriterionID, str] = {}
    if not spec.proposal.business_rules:
        automatic["rule-coverage"] = "Required business rules absent from proposal"
    if case.expected_conflicts == "none" and spec.proposal.conflicts:
        automatic["conflict-validity"] = "Proposal conflicts contradict the case expectation"
    if case.expected_conflicts == "present" and not spec.proposal.conflicts:
        automatic["conflict-validity"] = "Required explicit conflict absent from proposal"
    if case.requires_blocking_question and not any(q.blocking for q in spec.proposal.questions):
        automatic["uncertainty"] = "Required blocking question absent from proposal"
    judgments = {item.criterion: item for item in review.checks} if review else {}
    return [
        SemanticCheck(criterion=criterion, outcome="fail", note=automatic[criterion])
        if criterion in automatic
        else judgments.get(
            criterion,
            SemanticCheck(
                criterion=criterion, outcome="not-run", note="Independent human judgment required"
            ),
        )
        for criterion in CRITERIA
    ]


class UnderstandingEvalReport(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["UnderstandingArtifactEval/v1"] = "UnderstandingArtifactEval/v1"
    case: UnderstandingEvalCase
    rubric: UnderstandingRubric
    corpus_sha256: Digest
    split: Literal["development", "holdout"]
    declared_candidate_sha256: Digest | None = None
    understanding: ProjectUnderstandingSpec | None = None
    error_code: Text | None = None
    review: SemanticReview | None = None
    checks: list[SemanticCheck] = Field(default_factory=list)
    status: Verdict
    input_sha256: Digest
    proposal_sha256: Digest | None = None
    execution_evidence: Literal["offline-artifact-model-execution-not-established"] = (
        "offline-artifact-model-execution-not-established"
    )
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def consistent_judgment(self) -> Self:
        if self.split == "holdout" and self.declared_candidate_sha256 is None:
            raise ValueError("Holdout evaluation requires declared frozen candidate digest")
        if self.input_sha256 != canonical_project_digest(self.case.project.model_dump()):
            raise ValueError("Eval input digest differs from case input")
        if self.error_code is not None:
            if self.status != "error" or any((self.understanding, self.review, self.checks)):
                raise ValueError("Error report cannot contain proposal or judgment")
            if self.proposal_sha256 is not None:
                raise ValueError("Error report cannot claim a proposal digest")
            return self
        if self.understanding is None:
            raise ValueError("Artifact evaluation requires an understanding proposal")
        spec = self.understanding
        if spec.request.original_input != self.case.project:
            raise ValueError("Evaluated artifact belongs to a different case snapshot")
        digest = canonical_project_digest(spec.proposal.model_dump())
        if self.proposal_sha256 != digest:
            raise ValueError("Eval proposal digest differs from evaluated artifact")
        if self.review:
            review = self.review
            if (
                review.case_sha256 != canonical_project_digest(self.case.model_dump())
                or review.rubric_sha256 != canonical_project_digest(self.rubric.model_dump())
                or review.proposal_sha256 != digest
            ):
                raise ValueError("Semantic review is stale or belongs to another artifact/rubric")
            requirements = {rule.id: rule for rule in self.case.required_rules}
            rules = {rule.id: rule for rule in spec.proposal.business_rules}
            refs = {ref.id: ref for ref in spec.request.references}
            proposal_items = (
                spec.proposal.statements
                + spec.proposal.business_rules
                + spec.proposal.domain_candidates
                + spec.proposal.conflicts
                + spec.proposal.questions
            )
            items = {item.id: item for item in proposal_items}
            for support in review.support:
                if (
                    support.item_id not in items
                    or support.source_refs != items[support.item_id].source_refs
                ):
                    raise ValueError("Support judgment differs from the item's cited sources")
            if any(
                check.criterion == "citation-support" and check.outcome == "pass"
                for check in review.checks
            ):
                if set(items) != {support.item_id for support in review.support} or any(
                    support.outcome != "pass" for support in review.support
                ):
                    raise ValueError("Citation pass requires support judgments for every item")
            for mapping in review.coverage:
                if (
                    mapping.requirement_id not in requirements
                    or mapping.business_rule_id not in rules
                ):
                    raise ValueError("Coverage mapping has unresolved IDs")
                pointer = requirements[mapping.requirement_id].source_pointer
                if not any(
                    pointer == refs[key].pointer or pointer.startswith(refs[key].pointer + "/")
                    for key in rules[mapping.business_rule_id].source_refs
                ):
                    raise ValueError("Covered rule does not cite its required source")
            coverage_pass = any(
                check.criterion == "rule-coverage" and check.outcome == "pass"
                for check in review.checks
            )
            if coverage_pass and set(requirements) != {
                mapping.requirement_id for mapping in review.coverage
            }:
                raise ValueError("Coverage pass requires a mapping for every required rule")
        expected_checks = case_checks(self.case, spec, self.review)
        if self.checks != expected_checks:
            raise ValueError("Eval checks contradict automatic findings or supplied review")
        outcomes = {check.outcome for check in expected_checks}
        expected_status: Verdict = (
            "fail"
            if "fail" in outcomes
            else "pass"
            if outcomes == {"pass"} and self.rubric.approval
            else "not-run"
        )
        if self.status != expected_status:
            raise ValueError("Eval status contradicts findings, pending review or rubric approval")
        return self
