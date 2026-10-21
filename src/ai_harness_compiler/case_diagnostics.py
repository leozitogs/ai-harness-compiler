"""Pure structural diagnostics, separate from historical assessments and human judgment.

These frozen dataclasses are internal projections, not approval/wire contracts.
No finding is relabeled, no expectation is relaxed and no status is promoted.
"""

from dataclasses import dataclass
from typing import Literal

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase

MATERIAL_IMPACTS = {"rule", "authorization", "outcome", "precedence"}


@dataclass(frozen=True)
class FindingCandidate:
    finding_id: str
    kind: str
    subject: str | None


@dataclass(frozen=True)
class CoverageDiagnostic:
    obligation_id: str
    source_pointer: str
    expected_kind: str
    matched_finding_ids: tuple[str, ...]
    same_pointer_candidates: tuple[FindingCandidate, ...]
    requirement_source_unrepresentable_in_v3: bool


@dataclass(frozen=True)
class CaseDiagnostics:
    case_id: str
    case_sha256: str
    analysis_sha256: str
    expected_disposition: str
    actual_disposition: str
    disposition_matches: bool
    coverage: tuple[CoverageDiagnostic, ...]
    unmatched_refusal_pointers: tuple[str, ...]
    required_conflict_missing: bool
    authority: Literal["structural-diagnostic-only"] = "structural-diagnostic-only"
    semantic_status: Literal["not-established"] = "not-established"


def diagnose_case(case: AssessmentCase, analysis: SemanticAnalysisV3) -> CaseDiagnostics:
    """Enumerate every structural observation without a one-message-per-criterion limit.

    V3 produces requirement findings only from acceptance criteria. Context
    findings project to statement/domain; guards to rule; issues to question,
    conflict/rejection. Requiring kind=requirement at any other source is thus
    unrepresentable in this version, regardless of prompt or model quality.
    A same-pointer candidate alone establishes neither coverage nor support.
    """
    case = AssessmentCase.model_validate(case.model_dump())
    analysis = SemanticAnalysisV3.model_validate(analysis.model_dump())
    if canonical_project_digest(case.project.model_dump()) != (
        analysis.extraction.request.original_sha256
    ):
        raise ValueError("DIAGNOSTIC_INPUT_MISMATCH")
    atoms = {a.id: a for a in analysis.extraction.atoms}
    criteria = {a.pointer for a in atoms.values() if a.kind == "acceptance-criterion"}
    findings = analysis.findings
    pointers = {f.id: {atoms[id_].pointer for id_ in f.source_atom_ids} for f in findings}
    coverage = []
    for obligation in case.obligations:
        kind = (
            "question" if obligation.disposition == "required-question" else obligation.disposition
        )
        candidates = [f for f in findings if obligation.source_pointer in pointers[f.id]]
        coverage.append(
            CoverageDiagnostic(
                obligation_id=obligation.id,
                source_pointer=obligation.source_pointer,
                expected_kind=kind,
                matched_finding_ids=tuple(
                    f.id
                    for f in candidates
                    if f.kind == kind and (kind != "question" or f.impact in MATERIAL_IMPACTS)
                ),
                same_pointer_candidates=tuple(
                    FindingCandidate(f.id, f.kind, f.subject) for f in candidates
                ),
                requirement_source_unrepresentable_in_v3=(
                    kind == "requirement" and obligation.source_pointer not in criteria
                ),
            )
        )
    return CaseDiagnostics(
        case_id=case.id,
        case_sha256=case.snapshot_sha256,
        analysis_sha256=analysis.snapshot_sha256,
        expected_disposition=case.expected_behavior,
        actual_disposition=analysis.disposition,
        disposition_matches=case.expected_behavior == analysis.disposition,
        coverage=tuple(coverage),
        unmatched_refusal_pointers=tuple(
            pointer
            for pointer in case.refusal_source_pointers
            if not any(f.kind == "rejection" and pointer in pointers[f.id] for f in findings)
        ),
        required_conflict_missing=case.requires_conflict
        and not any(
            f.kind == "conflict" and set(case.conflict_source_pointers).issubset(pointers[f.id])
            for f in findings
        ),
    )
