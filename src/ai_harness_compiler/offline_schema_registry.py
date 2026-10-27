"""Opt-in contract schemas without changing the frozen historical CLI or runtime."""

from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.semantic_analysis_v4 import AnalysisProposalV4, SemanticAnalysisV4
from ai_harness_compiler.models.semantic_assessment_v4 import (
    SemanticAssessmentV4,
    SemanticHumanReviewV4,
)
from ai_harness_compiler.models.semantic_campaign import (
    SemanticCampaignAuthorizationV1,
    SemanticCampaignCallV1,
    SemanticCampaignReportV1,
    SemanticCampaignRequestV1,
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
from ai_harness_compiler.models.supervised_transport import (
    SupervisedFlowAuthorizationV1,
    SupervisedFlowReportV1,
    SupervisedFlowRequestV1,
    TransportLimitsV1,
    TransportReceiptV1,
)

OFFLINE_MODELS: dict[str, type[Contract]] = {
    "semantic-campaign-request-v1": SemanticCampaignRequestV1,
    "semantic-campaign-authorization-v1": SemanticCampaignAuthorizationV1,
    "semantic-campaign-call-v1": SemanticCampaignCallV1,
    "semantic-campaign-report-v1": SemanticCampaignReportV1,
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
    "supervised-flow-request-v1": SupervisedFlowRequestV1,
    "supervised-flow-authorization-v1": SupervisedFlowAuthorizationV1,
    "supervised-flow-report-v1": SupervisedFlowReportV1,
    "transport-limits-v1": TransportLimitsV1,
    "transport-receipt-v1": TransportReceiptV1,
}
