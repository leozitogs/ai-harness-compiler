"""Metadata-only reserved evaluation preparation; never reads cases or authorizes runs."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_eval import HumanDeclaration

Scenario = Literal[
    "novel-intent",
    "contrasting-rules",
    "ambiguous-process",
    "conflicting-sources",
    "compatible-rules",
    "unread-assets",
    "untrusted-instruction",
]
SCENARIOS = {
    "novel-intent",
    "contrasting-rules",
    "ambiguous-process",
    "conflicting-sources",
    "compatible-rules",
    "unread-assets",
    "untrusted-instruction",
}


class ReservedCaseBinding(Contract):
    case_id: Identifier
    project_id: Identifier
    family_id: Identifier
    scenario: Scenario
    artifact_path: Text
    artifact_sha256: Digest
    case_sha256: Digest
    input_sha256: Digest
    semantic_sha256: Digest


class ReservedCandidateFreeze(Contract):
    source_commit: Text = Field(pattern=r"^[0-9a-f]{40}(?:[0-9a-f]{24})?$")
    composition_version: Text
    audit_version: Text
    profile_sha256: Digest
    code_sha256: Digest

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())


class ReservedBudget(Contract):
    max_calls: int = Field(ge=1, le=1280)
    repetitions: int = Field(ge=1, le=10)
    max_call_seconds: int = Field(ge=1, le=300)
    max_session_seconds: int = Field(ge=1, le=86400)
    concurrency: Literal[1] = 1
    retries: Literal[0] = 0
    repairs: Literal[0] = 0

    @model_validator(mode="after")
    def consistent_timeout(self) -> Self:
        if self.max_session_seconds < self.max_call_seconds:
            raise ValueError("Session budget cannot be shorter than a call budget")
        return self


class ReservedCorpusReview(HumanDeclaration):
    corpus_sha256: Digest


class ReservedEvaluationProtocol(Contract):
    schema_version: Literal["ReservedEvaluationProtocol/v1"] = "ReservedEvaluationProtocol/v1"
    id: Identifier
    case_schema: Literal["AssessmentCase/v2"] = "AssessmentCase/v2"
    rubric_sha256: Digest
    candidate_designer: Text
    curator: Text | None = None
    curator_exposure: Literal["not-declared", "development-visible", "blind-declared"] = (
        "not-declared"
    )
    candidate: ReservedCandidateFreeze | None = None
    corpus_candidate_sha256: Digest | None = None
    development: list[ReservedCaseBinding] = Field(default_factory=list, max_length=64)
    reserved: list[ReservedCaseBinding] = Field(default_factory=list, max_length=64)
    review: ReservedCorpusReview | None = None
    budget: ReservedBudget | None = None
    purpose: Literal["separate-evaluation-no-tuning"] = "separate-evaluation-no-tuning"
    acceptance: Literal["all-criteria-pass-no-critical-failure"] = (
        "all-criteria-pass-no-critical-failure"
    )

    @property
    def corpus_sha256(self) -> str:
        return canonical_project_digest(
            {
                "case_schema": self.case_schema,
                "rubric_sha256": self.rubric_sha256,
                "candidate_designer": self.candidate_designer,
                "curator": self.curator,
                "curator_exposure": self.curator_exposure,
                "candidate_sha256": self.corpus_candidate_sha256,
                "development": [c.model_dump() for c in self.development],
                "reserved": [c.model_dump() for c in self.reserved],
            }
        )

    @model_validator(mode="after")
    def unique_cases(self) -> Self:
        for split in (self.development, self.reserved):
            for field in (
                "case_id",
                "artifact_path",
                "artifact_sha256",
                "case_sha256",
                "semantic_sha256",
            ):
                values = [getattr(case, field) for case in split]
                if len(values) != len(set(values)):
                    raise ValueError(
                        "Case identities and fingerprints must be unique within a split"
                    )
        return self


def reserved_preparation_gates(protocol: ReservedEvaluationProtocol) -> list[str]:
    gates = []
    if not protocol.curator or protocol.curator_exposure != "blind-declared":
        gates.append("independent-curation-not-declared")
    if protocol.curator == protocol.candidate_designer:
        gates.append("curator-is-candidate-designer")
    if protocol.candidate is None:
        gates.append("candidate-not-frozen")
    elif protocol.corpus_candidate_sha256 != protocol.candidate.sha256:
        gates.append("corpus-candidate-binding-missing-or-stale")
    if not protocol.development:
        gates.append("development-metadata-missing")
    if len(protocol.reserved) < 8:
        gates.append("reserved-case-count-insufficient")
    if {c.scenario for c in protocol.reserved} != SCENARIOS or sum(
        c.scenario == "contrasting-rules" for c in protocol.reserved
    ) < 2:
        gates.append("scenario-coverage-incomplete")
    for field in (
        "case_id",
        "project_id",
        "family_id",
        "artifact_path",
        "artifact_sha256",
        "case_sha256",
        "input_sha256",
        "semantic_sha256",
    ):
        if {getattr(c, field) for c in protocol.development} & {
            getattr(c, field) for c in protocol.reserved
        }:
            gates.append("development-reserved-overlap:" + field)
    if protocol.review is None:
        gates.append("human-expectations-review-missing")
    elif protocol.review.corpus_sha256 != protocol.corpus_sha256:
        gates.append("human-expectations-review-stale")
    elif protocol.review.reviewer == protocol.candidate_designer:
        gates.append("candidate-designer-cannot-approve-corpus")
    if protocol.budget is None:
        gates.append("execution-budget-not-proposed")
    elif protocol.budget.max_calls != 2 * len(protocol.reserved) * protocol.budget.repetitions:
        gates.append("execution-budget-does-not-match-generation-and-audit")
    return gates


class ReservedPreparationReport(Contract):
    schema_version: Literal["ReservedPreparationReport/v1"] = "ReservedPreparationReport/v1"
    protocol: ReservedEvaluationProtocol
    protocol_sha256: Digest
    state: Literal["blocked", "reviewable"]
    pending_gates: list[Text]
    payload_validation: Literal["not-performed"] = "not-performed"
    identity_authentication: Literal["not-established"] = "not-established"
    execution_authorized: Literal[False] = False
    model_calls: Literal[0] = 0

    @model_validator(mode="after")
    def bind_metadata_diagnostic(self) -> Self:
        protocol = ReservedEvaluationProtocol.model_validate(self.protocol.model_dump())
        gates = reserved_preparation_gates(protocol)
        if self.protocol_sha256 != canonical_project_digest(protocol.model_dump()) or (
            self.pending_gates != gates or self.state != ("blocked" if gates else "reviewable")
        ):
            raise ValueError(
                "Preparation state must match exact protocol metadata and pending gates"
            )
        return self


def prepare_reserved_evaluation(protocol: ReservedEvaluationProtocol) -> ReservedPreparationReport:
    protocol = ReservedEvaluationProtocol.model_validate(protocol.model_dump())
    gates = reserved_preparation_gates(protocol)
    return ReservedPreparationReport(
        protocol=protocol,
        protocol_sha256=canonical_project_digest(protocol.model_dump()),
        state="blocked" if gates else "reviewable",
        pending_gates=gates,
    )
