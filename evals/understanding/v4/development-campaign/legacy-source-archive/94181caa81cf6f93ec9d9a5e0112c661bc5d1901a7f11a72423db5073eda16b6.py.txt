"""Opt-in injected flow identities; no provider selection or implicit execution approval."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.semantic_assessment_v4 import SemanticAssessmentV4, assess_v4
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_eval import HumanDeclaration, UnderstandingRubric
from ai_harness_compiler.models.semantic_preflight import SemanticPreflightReport, preflight_case
from ai_harness_compiler.models.semantic_verification_v5 import (
    SemanticVerifierReportV5,
    audit_v5_program_digest,
)


class SemanticFlowRequestV4(Contract):
    schema_version: Literal["SemanticFlowRequest/v4"] = "SemanticFlowRequest/v4"
    run_id: Identifier
    case: AssessmentCaseV3
    rubric: UnderstandingRubric
    requested_model: Text = Field(max_length=256)
    generation_program_sha256: Digest
    audit_program_sha256: Digest
    max_generator_calls: Literal[2] = 2

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def exact_programs(self) -> Self:
        # Local import avoids coupling domain models to an instantiated provider.
        from ai_harness_compiler.semantic_generation_v4 import generation_program_v4

        if (
            self.generation_program_sha256
            != generation_program_v4(extract_grounding(self.case.project))
            or self.audit_program_sha256 != audit_v5_program_digest()
            or self.rubric.version != "v2"
        ):
            raise ValueError("Flow must bind current generation, audit and v2 rubric")
        return self


class SemanticFlowAuthorizationV4(HumanDeclaration):
    schema_version: Literal["SemanticFlowAuthorization/v4"] = "SemanticFlowAuthorization/v4"
    request_sha256: Digest
    authorized: Literal[True]


class SemanticFlowCallV4(Contract):
    stage: Literal["analysis", "audit"]
    prompt_sha256: Digest
    schema_sha256: Digest


class SemanticFlowResultV4(Contract):
    schema_version: Literal["SemanticFlowResult/v4"] = "SemanticFlowResult/v4"
    request: SemanticFlowRequestV4
    authorization: SemanticFlowAuthorizationV4
    preflight: SemanticPreflightReport
    calls: list[SemanticFlowCallV4] = Field(max_length=2)
    status: Literal["completed", "failed"]
    failure_code: Literal["factory-failed", "analysis-failed", "audit-failed"] | None = None
    analysis: SemanticAnalysisV4 | None = None
    audit: SemanticVerifierReportV5 | None = None
    assessment: SemanticAssessmentV4 | None = None
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def exact_result(self) -> Self:
        request = SemanticFlowRequestV4.model_validate(self.request.model_dump())
        if (
            self.authorization.request_sha256 != request.sha256
            or not request.case.expectations_approval
            or not request.rubric.approval
            or self.preflight != preflight_case(request.case, "SemanticAnalysis/v4")
            or self.preflight.status != "compatible"
        ):
            raise ValueError("Flow requires exact approval and preflight snapshots")
        stages = [c.stage for c in self.calls]
        if stages != ["analysis", "audit"][: len(stages)]:
            raise ValueError("Flow calls must be ordered, debited once and never retried")
        if self.analysis:
            analysis = SemanticAnalysisV4.model_validate(self.analysis.model_dump())
            if analysis.extraction != extract_grounding(request.case.project):
                raise ValueError("Flow analysis differs from original project")
        if self.audit:
            audit = SemanticVerifierReportV5.model_validate(self.audit.model_dump())
            if audit.analysis != self.analysis or audit.requested_model != request.requested_model:
                raise ValueError("Audit must bind flow analysis and requested model")
        if self.assessment != (
            assess_v4(request.case, request.rubric, self.analysis) if self.analysis else None
        ):
            raise ValueError(
                "Initial assessment must be reproducible without human output approval"
            )
        shape = (len(stages), self.analysis is not None, self.audit is not None)
        expected = {
            "factory-failed": (0, False, False),
            "analysis-failed": (1, False, False),
            "audit-failed": (2, True, False),
            None: (2, True, True),
        }
        if shape != expected[self.failure_code] or (self.status == "completed") != (
            self.failure_code is None
        ):
            raise ValueError(
                "Technical completion must match charged calls and validated artifacts"
            )
        return self
