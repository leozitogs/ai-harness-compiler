"""Opt-in contract schemas without changing the frozen historical CLI or runtime."""

from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.semantic_analysis_v4 import AnalysisProposalV4, SemanticAnalysisV4
from ai_harness_compiler.models.semantic_assessment_v4 import (
    SemanticAssessmentV4,
    SemanticHumanReviewV4,
)
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowRequestV4,
    SemanticFlowResultV4,
)
from ai_harness_compiler.models.semantic_preflight import SemanticPreflightReport
from ai_harness_compiler.models.semantic_verification_v5 import (
    SemanticVerifierReportV5,
    VerifierProposalV5,
)

OFFLINE_MODELS: dict[str, type[Contract]] = {
    "semantic-analysis-proposal-v4": AnalysisProposalV4,
    "semantic-analysis-v4": SemanticAnalysisV4,
    "semantic-assessment-case-v3": AssessmentCaseV3,
    "semantic-preflight-report": SemanticPreflightReport,
    "semantic-verifier-proposal-v5": VerifierProposalV5,
    "semantic-verifier-report-v5": SemanticVerifierReportV5,
    "semantic-human-review-v4": SemanticHumanReviewV4,
    "semantic-assessment-v4": SemanticAssessmentV4,
    "semantic-flow-request-v4": SemanticFlowRequestV4,
    "semantic-flow-authorization-v4": SemanticFlowAuthorizationV4,
    "semantic-flow-result-v4": SemanticFlowResultV4,
}
