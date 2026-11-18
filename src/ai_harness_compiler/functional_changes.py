"""Pure draft/readiness checks, independent of inference, test execution and installation."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Text
from ai_harness_compiler.models.functional_change import (
    EXAMPLE_KINDS,
    ChangeWorkLogV1,
    FunctionalChangeReviewV1,
    FunctionalChangeV1,
)


class FunctionalBlockerV1(Contract):
    code: Literal[
        "unconfirmed-rule",
        "missing-example",
        "missing-requirement",
        "unmapped-requirement",
        "unmapped-example",
        "unresolved-question",
        "stale-review",
    ]
    reference: Text


def _blockers(
    change: FunctionalChangeV1, review: FunctionalChangeReviewV1 | None
) -> list[FunctionalBlockerV1]:
    result = []

    def add(code: str, reference: str) -> None:
        result.append(FunctionalBlockerV1.model_validate(dict(code=code, reference=reference)))

    confirmed = {c.rule_id for c in change.confirmations}
    covered = {(e.rule_id, e.kind) for e in change.examples} | {
        (e.rule_id, e.kind) for e in change.exemptions
    }
    required = {id_ for r in change.requirements for id_ in r.rule_ids}
    mapped = {s.example_id for s in change.scenarios}
    mapped_requirements = {s.requirement_id for s in change.scenarios}
    decided = {d.question_id for d in change.decisions}
    for rule in change.rules:
        if rule.id not in confirmed:
            add("unconfirmed-rule", rule.id)
        if not any(e.rule_id == rule.id for e in change.examples):
            add("missing-example", f"{rule.id}:concrete")
        for kind in EXAMPLE_KINDS:
            if (rule.id, kind) not in covered:
                add("missing-example", f"{rule.id}:{kind}")
        if rule.id not in required:
            add("missing-requirement", rule.id)
    for example in change.examples:
        if example.id not in mapped:
            add("unmapped-example", example.id)
    for requirement in change.requirements:
        if requirement.id not in mapped_requirements:
            add("unmapped-requirement", requirement.id)
    for question in change.questions:
        if question.id not in decided and question.impact != "implementation-detail":
            add("unresolved-question", question.id)
    if review and (
        review.project_id != change.source.original_input.id
        or review.change_id != change.id
        or review.revision != change.revision
        or review.content_sha256 != change.sha256
    ):
        add("stale-review", change.id)
    return result


ReadinessStatus = Literal["blocked", "ready-for-human-review", "approved", "rejected"]


def _status(
    blockers: list[FunctionalBlockerV1], review: FunctionalChangeReviewV1 | None
) -> ReadinessStatus:
    if blockers:
        return "blocked"
    return review.decision if review else "ready-for-human-review"


class FunctionalReadinessV1(Contract):
    schema_version: Literal["FunctionalReadiness/v1"] = "FunctionalReadiness/v1"
    change: FunctionalChangeV1
    review: FunctionalChangeReviewV1 | None = None
    blockers: list[FunctionalBlockerV1] = Field(max_length=2048)
    status: ReadinessStatus
    test_execution_status: Literal["not-run"] = "not-run"
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def recompute(self) -> Self:
        change = FunctionalChangeV1.model_validate(self.change.model_dump())
        review = (
            FunctionalChangeReviewV1.model_validate(self.review.model_dump())
            if self.review
            else None
        )
        blockers = _blockers(change, review)
        if self.blockers != blockers or self.status != _status(blockers, review):
            raise ValueError("Readiness must preserve exact current blockers and review binding")
        return self


def assess_functional_change(
    change: FunctionalChangeV1, review: FunctionalChangeReviewV1 | None = None
) -> FunctionalReadinessV1:
    change = FunctionalChangeV1.model_validate(change.model_dump())
    review = FunctionalChangeReviewV1.model_validate(review.model_dump()) if review else None
    blockers = _blockers(change, review)
    return FunctionalReadinessV1(
        change=change, review=review, blockers=blockers, status=_status(blockers, review)
    )


def validate_change_worklog(
    change: FunctionalChangeV1, worklog: ChangeWorkLogV1
) -> ChangeWorkLogV1:
    change = FunctionalChangeV1.model_validate(change.model_dump())
    worklog = ChangeWorkLogV1.model_validate(worklog.model_dump())
    if worklog.change_sha256 != change.sha256 or not set(worklog.prepared_scenario_ids).issubset(
        {s.id for s in change.scenarios}
    ):
        raise ValueError("Worklog must bind current change and existing scenarios")
    return worklog
