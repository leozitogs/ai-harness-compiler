"""Pure QA evidence validation and Nexo closure advice; no execution authority."""

from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.qa import (
    FACETS,
    CheckID,
    Facet,
    QACheckResult,
    QACriterionResult,
    QAFindingResolutionProposal,
    QAFindingResolutionReview,
    QAIncidentCandidate,
    QAInspection,
    QAReviewComparison,
    QAReviewReport,
    QAReviewRequest,
    SprintClosureAssessment,
)
from ai_harness_compiler.scrum_observer import PlanProjection, decode_document


def project_for(request: QAReviewRequest) -> ProjectInput:
    source = next(s for s in request.snapshot.observation.sources if s.kind == "project")
    return ProjectInput.model_validate(decode_document(source.content or ""))


def validate_inspection(request: QAReviewRequest, inspection: QAInspection) -> None:
    inspection = QAInspection.model_validate(inspection.model_dump())
    if len({f.id for f in inspection.findings}) != len(inspection.findings):
        raise ValueError("QA finding IDs must be unique")
    if len(set(inspection.inspected_facets)) != len(inspection.inspected_facets):
        raise ValueError("Inspection facets must be unique")
    sources = {s.path: s for s in request.sources}
    selected = {s.id for s in request.snapshot.stories}
    stories = {s.id: s for s in project_for(request).backlog}
    for finding in inspection.findings:
        if (
            finding.story_id not in selected
            or finding.story_id not in stories
            or finding.criterion_index >= len(stories[finding.story_id].acceptance_criteria)
        ):
            raise ValueError("Finding refers to an unknown story or criterion")
        if finding.facet not in inspection.inspected_facets:
            raise ValueError("Finding facet was not inspected")
        for citation in finding.citations:
            source = sources.get(citation.path)
            lines = source.content.splitlines() if source else []
            if citation.line > len(lines) or citation.quote not in lines[citation.line - 1]:
                raise ValueError("Finding citation is absent from the exact captured line")


def report_facts(
    request: QAReviewRequest,
    inspection: QAInspection,
    checks: list[QACheckResult],
) -> tuple[str, list[Facet], int, list[QACriterionResult]]:
    missing = [f for f in FACETS if f not in inspection.inspected_facets]
    selected = {s.id for s in request.snapshot.stories}
    count = sum(
        len(s.acceptance_criteria) for s in project_for(request).backlog if s.id in selected
    )
    failures = any(c.status in {"failed", "timed-out", "output-limit"} for c in checks)
    matrix = [
        QACriterionResult(
            story_id=item.id,
            criterion_index=i,
            criterion=text,
            finding_ids=[
                f.id
                for f in inspection.findings
                if f.story_id == item.id and f.criterion_index == i
            ],
        )
        for item in project_for(request).backlog
        if item.id in selected
        for i, text in enumerate(item.acceptance_criteria)
    ]
    # Findings remain open until a new, explicitly reviewed inspection. A citation
    # validates location, never the semantic claim or a proposed reproduction.
    if failures or any(f.severity in {"P0", "P1"} for f in inspection.findings):
        recommendation = "changes-required"
    elif (
        inspection.findings
        or missing
        or request.excluded_paths
        or not checks
        or any(c.status != "passed" for c in checks)
    ):
        recommendation = "inconclusive"
    else:
        recommendation = "ready-for-po"
    return recommendation, missing, count, matrix


def review_report(
    request: QAReviewRequest,
    inspection: QAInspection,
    checks: list[QACheckResult],
    *,
    engine: str = "local",
    model: str | None = None,
    inspection_status: str = "not-requested",
    model_calls: int | None = 0,
    model_attempts: int = 0,
) -> QAReviewReport:
    request = QAReviewRequest.model_validate(request.model_dump())
    validate_inspection(request, inspection)
    recommendation, missing, count, matrix = report_facts(request, inspection, checks)
    return QAReviewReport.model_validate(
        {
            "request": request.model_dump(),
            "request_sha256": request.request_sha256,
            "engine": engine,
            "model": model,
            "inspection": inspection.model_dump(),
            "inspection_status": inspection_status,
            "model_calls": model_calls,
            "model_attempts": model_attempts,
            "checks": [c.model_dump() for c in checks],
            "recommendation": recommendation,
            "missing_facets": missing,
            "criterion_count": count,
            "criterion_matrix": [c.model_dump() for c in matrix],
        }
    )


def closure_facts(qa: QAReviewReport) -> tuple[str, list[str], list[str], list[CheckID], str]:
    source = next(s for s in qa.request.snapshot.observation.sources if s.kind == "plan")
    goal = PlanProjection.model_validate(decode_document(source.content or "")).goal
    blockers = [f.id for f in qa.inspection.findings if f.severity in {"P0", "P1"}]
    failures = [c.id for c in qa.checks if c.status in {"failed", "timed-out", "output-limit"}]
    return goal, blockers, [s.id for s in qa.request.snapshot.stories], failures, qa.recommendation


def assess_closure(qa: QAReviewReport) -> SprintClosureAssessment:
    qa = QAReviewReport.model_validate(qa.model_dump())
    goal, blockers, carryover, failures, conclusion = closure_facts(qa)
    return SprintClosureAssessment.model_validate(
        {
            "qa": qa.model_dump(),
            "qa_sha256": qa.report_sha256,
            "sprint_goal": goal,
            "blocking_findings": blockers,
            "carryover": carryover,
            "check_failures": failures,
            "conclusion": conclusion,
        }
    )


def comparison_facts(
    previous: QAReviewReport, current: QAReviewReport
) -> tuple[list[CheckID], list[str]]:
    old, new = previous.request.snapshot.observation, current.request.snapshot.observation
    if (old.project_id, old.repository, old.sprint_id) != (
        new.project_id,
        new.repository,
        new.sprint_id,
    ):
        raise ValueError("QA reports belong to different project, repository or sprint")
    old_criteria = [(c.story_id, c.criterion_index, c.criterion) for c in previous.criterion_matrix]
    new_criteria = [(c.story_id, c.criterion_index, c.criterion) for c in current.criterion_matrix]
    same_scope = old_criteria == new_criteria
    new_checks = {c.id: c for c in current.checks}
    cleared = [
        c.id
        for c in previous.checks
        if c.status in {"failed", "timed-out", "output-limit"}
        and c.id in new_checks
        and new_checks[c.id].status == "passed"
        and previous.request.head_commit != current.request.head_commit
        and same_scope
    ]
    return cleared, [f.id for f in previous.inspection.findings]


def validate_resolution_proposal(proposal: QAFindingResolutionProposal) -> None:
    previous = QAReviewReport.model_validate(proposal.previous.model_dump())
    current = QAReviewReport.model_validate(proposal.current.model_dump())
    comparison_facts(previous, current)
    if previous.request.head_commit == current.request.head_commit:
        raise ValueError("Resolution needs a new revision")
    old_matrix = [(c.story_id, c.criterion_index, c.criterion) for c in previous.criterion_matrix]
    new_matrix = [(c.story_id, c.criterion_index, c.criterion) for c in current.criterion_matrix]
    if old_matrix != new_matrix:
        raise ValueError("Resolution cannot change criterion scope")
    findings = {f.id: f for f in previous.inspection.findings}
    if proposal.finding_id not in findings:
        raise ValueError("Resolution refers to an unknown previous finding")
    finding = findings[proposal.finding_id]
    if (
        current.inspection_status != "completed"
        or finding.facet not in current.inspection.inspected_facets
    ):
        raise ValueError("Resolution requires current inspection of the finding facet")
    if any(f.id == finding.id for f in current.inspection.findings):
        raise ValueError("Finding remains open in the current inspection")
    if len(set(proposal.check_ids)) != len(proposal.check_ids):
        raise ValueError("Resolution checks must be unique")
    checks = {c.id: c for c in current.checks}
    if any(
        identifier not in checks or checks[identifier].status != "passed"
        for identifier in proposal.check_ids
    ):
        raise ValueError("Resolution requires observed passing checks")
    sources = {s.path: s for s in current.request.sources}
    for citation in proposal.citations:
        source = sources.get(citation.path)
        lines = source.content.splitlines() if source else []
        if citation.line > len(lines) or citation.quote not in lines[citation.line - 1]:
            raise ValueError("Resolution citation is absent from the current source")


def resolution_facts(
    previous: QAReviewReport, current: QAReviewReport, reviews: list[QAFindingResolutionReview]
) -> list[str]:
    resolved = []
    seen = set()
    for value in reviews:
        review = QAFindingResolutionReview.model_validate(value.model_dump())
        proposal = review.proposal
        if (
            proposal.previous.report_sha256 != previous.report_sha256
            or proposal.current.report_sha256 != current.report_sha256
        ):
            raise ValueError("Resolution belongs to different QA reports")
        if proposal.finding_id in seen:
            raise ValueError("Duplicate resolution decision for a finding")
        seen.add(proposal.finding_id)
        if review.decision == "confirm":
            resolved.append(proposal.finding_id)
    return resolved


def compare_reviews(
    previous: QAReviewReport,
    current: QAReviewReport,
    resolutions: list[QAFindingResolutionReview] | None = None,
) -> QAReviewComparison:
    previous = QAReviewReport.model_validate(previous.model_dump())
    current = QAReviewReport.model_validate(current.model_dump())
    cleared, pending = comparison_facts(previous, current)
    reviews = resolutions or []
    resolved = resolution_facts(previous, current, reviews)
    return QAReviewComparison(
        previous=previous,
        current=current,
        cleared_check_failures=cleared,
        pending_previous_findings=[p for p in pending if p not in resolved],
        resolution_reviews=reviews,
        resolved_previous_findings=resolved,
    )


def incident_candidates(report: QAReviewReport) -> list[QAIncidentCandidate]:
    report = QAReviewReport.model_validate(report.model_dump())
    return [
        QAIncidentCandidate.model_validate(
            {
                "qa_sha256": report.report_sha256,
                "head_commit": report.request.head_commit,
                "check_id": c.id,
                "observed_status": c.status,
                "output_sha256": c.output_sha256,
            }
        )
        for c in report.checks
        if c.status in {"failed", "timed-out", "output-limit"}
    ]
