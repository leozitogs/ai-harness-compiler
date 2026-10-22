"""Opt-in contract schemas without changing the frozen historical CLI or runtime."""

from ai_harness_compiler.models.base import Contract
from ai_harness_compiler.models.semantic_analysis_v4 import AnalysisProposalV4, SemanticAnalysisV4
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import SemanticPreflightReport

OFFLINE_MODELS: dict[str, type[Contract]] = {
    "semantic-analysis-proposal-v4": AnalysisProposalV4,
    "semantic-analysis-v4": SemanticAnalysisV4,
    "semantic-assessment-case-v3": AssessmentCaseV3,
    "semantic-preflight-report": SemanticPreflightReport,
}
