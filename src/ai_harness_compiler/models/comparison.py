"""Two independent proposals expose textual disagreement, never semantic truth."""

import math
from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.compact_analysis import CompactAnalysisSpec, compact_input
from ai_harness_compiler.models.evidence import Digest
from ai_harness_compiler.models.grounding import GroundingExtraction

Provider = Literal["ollama", "codex-cli"]
ComparisonError = Literal["provider-error", "provider-timeout", "invalid-proposal"]


class ComparisonCandidateResult(Contract):
    id: Identifier
    provider: Provider
    requested_model: Text
    program_sha256: Digest | None = None
    reported_model: Text | None = None
    status: Literal["completed", "error", "timeout"]
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    compact_analysis: CompactAnalysisSpec | None = None
    error_code: ComparisonError | None = None

    @model_validator(mode="after")
    def consistent_result(self) -> Self:
        if self.status == "completed":
            if self.compact_analysis is None or self.error_code is not None:
                raise ValueError("Completed candidate requires a proposal and no error")
            CompactAnalysisSpec.model_validate(self.compact_analysis.model_dump())
        else:
            if self.compact_analysis is not None or self.error_code is None:
                raise ValueError("Failed candidate cannot claim a proposal")
            if (self.status == "timeout") != (self.error_code == "provider-timeout"):
                raise ValueError("Timeout status and code must agree")
        return self


def criterion_inventory(
    extraction: GroundingExtraction, candidates: list[ComparisonCandidateResult]
) -> tuple[list[int], list[int], list[int]]:
    count = len(compact_input(extraction).criteria)
    if any(c.status != "completed" for c in candidates):
        return [], [], list(range(count))
    left, right = [c.compact_analysis for c in candidates]
    assert left is not None and right is not None
    agreements: list[int] = []
    disagreements: list[int] = []
    for index, (a, b) in enumerate(
        zip(left.interpretation.criteria, right.interpretation.criteria, strict=True)
    ):
        # Notes explain a proposal but do not form its classification/behavior contract.
        equal = a.model_dump(exclude={"note"}) == b.model_dump(exclude={"note"})
        (agreements if equal else disagreements).append(index)
    return agreements, disagreements, []


class ComparisonReport(Contract):
    schema_version: Literal["UnderstandingComparison/v1"] = "UnderstandingComparison/v1"
    extraction: GroundingExtraction
    input_sha256: Digest
    candidates: list[ComparisonCandidateResult] = Field(min_length=2, max_length=2)
    criterion_agreements: list[int]
    criterion_disagreements: list[int]
    unavailable_criteria: list[int]
    comparison_basis: Literal["exact-criterion-fields-excluding-note"] = (
        "exact-criterion-fields-excluding-note"
    )
    wall_time_seconds: float = Field(ge=0, allow_inf_nan=False)
    total_call_seconds: float = Field(ge=0, allow_inf_nan=False)
    semantic_status: Literal["not-established"] = "not-established"
    model_qualification: Literal["not-established"] = "not-established"
    human_review_required: Literal[True] = True

    @model_validator(mode="after")
    def consistent_comparison(self) -> Self:
        extraction = GroundingExtraction.model_validate(self.extraction.model_dump())
        candidates = [
            ComparisonCandidateResult.model_validate(c.model_dump()) for c in self.candidates
        ]
        if self.input_sha256 != extraction.request.original_sha256:
            raise ValueError("Comparison digest must bind the authoritative input")
        if len({c.id for c in candidates}) != 2:
            raise ValueError("Comparison requires two distinct candidate identifiers")
        if {c.provider for c in candidates} != {"ollama", "codex-cli"}:
            raise ValueError("Comparison requires one candidate from each provider")
        for candidate in candidates:
            if candidate.compact_analysis is not None:
                if candidate.compact_analysis.extraction != extraction:
                    raise ValueError("Candidate must bind the complete original extraction")
                if candidate.compact_analysis.understanding.review is not None:
                    raise ValueError("Comparison cannot establish a human review")
        expected = criterion_inventory(extraction, candidates)
        actual = (
            self.criterion_agreements,
            self.criterion_disagreements,
            self.unavailable_criteria,
        )
        if actual != expected:
            raise ValueError("Criterion comparison inventory must match the proposals exactly")
        total = sum(c.elapsed_seconds for c in candidates)
        if not math.isclose(self.total_call_seconds, total, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError("Total call time must equal both measured candidate durations")
        if self.wall_time_seconds + 1e-9 < max(c.elapsed_seconds for c in candidates):
            raise ValueError("Wall time cannot be shorter than either provider call")
        return self
