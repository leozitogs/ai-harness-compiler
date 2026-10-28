"""Structural conflict/question coverage, independent of human semantic assessment."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier
from ai_harness_compiler.models.evidence import Digest
from ai_harness_compiler.models.semantic_analysis_v3 import BoundFindingV3
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4


class ConflictQuestionBindingV1(Contract):
    conflict_id: Identifier
    conflict_sha256: Digest
    source_atom_ids: list[Identifier] = Field(min_length=1, max_length=32)
    candidate_question_ids: list[Identifier] = Field(max_length=128)


def conflict_bindings(analysis: SemanticAnalysisV4) -> list[ConflictQuestionBindingV1]:
    questions = [
        f
        for f in analysis.findings
        if isinstance(f, BoundFindingV3) and f.kind == "question" and f.impact == "precedence"
    ]
    return [
        ConflictQuestionBindingV1(
            conflict_id=f.id,
            conflict_sha256=f.sha256,
            source_atom_ids=f.source_atom_ids,
            candidate_question_ids=[
                q.id for q in questions if set(f.source_atom_ids).issubset(q.source_atom_ids)
            ],
        )
        for f in analysis.findings
        if f.kind == "conflict"
    ]


def conflict_status(bindings: list[ConflictQuestionBindingV1]) -> str:
    if not bindings:
        return "no-conflicts"
    return (
        "questions-present"
        if all(b.candidate_question_ids for b in bindings)
        else "missing-question"
    )


class ConflictQuestionDiagnosticV1(Contract):
    schema_version: Literal["ConflictQuestionDiagnostic/v1"] = "ConflictQuestionDiagnostic/v1"
    analysis: SemanticAnalysisV4
    analysis_sha256: Digest
    bindings: list[ConflictQuestionBindingV1] = Field(max_length=128)
    status: Literal["no-conflicts", "missing-question", "questions-present"]
    semantic_judgment: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def exact_structure(self) -> Self:
        expected = conflict_bindings(self.analysis)
        if (
            self.analysis_sha256 != self.analysis.snapshot_sha256
            or self.bindings != expected
            or self.status != conflict_status(expected)
        ):
            raise ValueError(
                "Conflict diagnostics must bind exact analysis and structural coverage"
            )
        return self


def diagnose_conflict_questions(analysis: SemanticAnalysisV4) -> ConflictQuestionDiagnosticV1:
    analysis = SemanticAnalysisV4.model_validate(analysis.model_dump())
    bindings = conflict_bindings(analysis)
    return ConflictQuestionDiagnosticV1.model_validate(
        dict(
            analysis=analysis,
            analysis_sha256=analysis.snapshot_sha256,
            bindings=bindings,
            status=conflict_status(bindings),
        )
    )
