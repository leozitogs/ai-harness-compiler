"""Offline extraction -> proposal -> quotation verification boundaries."""

from typing import Protocol

from ai_harness_compiler.models.grounded_analysis import (
    GroundedAnalysisProposal,
    GroundedAnalysisSpec,
)
from ai_harness_compiler.models.grounding import (
    GroundingExtraction,
    GroundingQuotationReport,
    criterion_quotations,
    literal_evidence,
)
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec
from ai_harness_compiler.understanding import prepare_understanding


class GroundedAnalysisModel(Protocol):
    def analyze(self, extraction: GroundingExtraction) -> GroundedAnalysisProposal:
        """Propose findings and complete dispositions; no review or input replacement."""
        ...


def analyze_project(project: ProjectInput, model: GroundedAnalysisModel) -> GroundedAnalysisSpec:
    extraction = extract_grounding(project)
    analysis = model.analyze(GroundingExtraction.model_validate(extraction.model_dump()))
    return GroundedAnalysisSpec.model_validate(
        {
            "extraction": extraction.model_dump(),
            "analysis": analysis.model_dump(),
        }
    )


def extract_grounding(project: ProjectInput) -> GroundingExtraction:
    request = prepare_understanding(project)
    atoms, excluded = literal_evidence(request)
    return GroundingExtraction(request=request, atoms=atoms, excluded_references=excluded)


def verify_quotations(spec: ProjectUnderstandingSpec) -> GroundingQuotationReport:
    snapshot = ProjectUnderstandingSpec.model_validate(spec.model_dump())
    extraction = extract_grounding(snapshot.request.original_input)
    return GroundingQuotationReport(
        extraction=extraction,
        understanding=snapshot,
        criteria=criterion_quotations(extraction, snapshot),
    )
