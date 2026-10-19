"""A resolved finding needs new evidence and a separate explicit human decision."""

import hashlib

import pytest
from test_qa import check, finding, inspection, request
from test_scrum_observer import NOW

from ai_harness_compiler.models.qa import (
    QAFindingResolutionProposal,
    QAFindingResolutionReview,
    QAReviewComparison,
    ReviewSource,
)
from ai_harness_compiler.qa import compare_reviews, review_report


def proposal():
    old = request()
    previous = review_report(
        old,
        inspection([finding()]),
        [check(old)],
        engine="provided-inspection",
        inspection_status="completed",
    )
    current_request = request()
    current_request.head_commit = "c" * 40
    code = "def authorize(approved):\n    return approved\n"
    current_request.sources = [
        ReviewSource(
            path="src/approval.py", content=code, sha256=hashlib.sha256(code.encode()).hexdigest()
        )
    ]
    current = review_report(
        current_request,
        inspection(),
        [check(current_request)],
        engine="provided-inspection",
        inspection_status="completed",
    )
    return QAFindingResolutionProposal(
        previous=previous,
        current=current,
        finding_id="approval-bypass",
        citations=[{"path": "src/approval.py", "line": 2, "quote": "return approved"}],
        check_ids=["tests"],
        rationale="False approval now returns False; regression check passed.",
    )


def test_proposal_alone_cannot_clear_a_finding_and_confirmation_is_scoped():
    proposed = proposal()
    pending = compare_reviews(proposed.previous, proposed.current)
    assert pending.pending_previous_findings == ["approval-bypass"]
    assert proposed.status == "awaiting-human-review"
    review = QAFindingResolutionReview(
        proposal=proposed,
        decision="confirm",
        actor="fixture-human-reviewer",
        reviewed_at=NOW,
        comment="Reviewed explicit fixture evidence.",
    )
    compared = compare_reviews(proposed.previous, proposed.current, [review])
    assert compared.resolved_previous_findings == ["approval-bypass"]
    assert compared.pending_previous_findings == []
    assert compared.semantic_resolution == "not-established"
    assert compared.current.acceptance == "not-established"
    assert review.completion_authority == "none"
    data = compared.model_dump()
    data["resolution_reviews"] = []
    with pytest.raises(ValueError):
        QAReviewComparison.model_validate(data)


@pytest.mark.parametrize("actor", ["vera", "nexo", "engineer"])
def test_agents_and_authors_cannot_be_resolution_reviewers(actor):
    with pytest.raises(ValueError, match="separate"):
        QAFindingResolutionReview(
            proposal=proposal(),
            decision="confirm",
            actor=actor,
            reviewed_at=NOW,
            comment="Not a separate reviewer",
        )


def test_rejection_preserves_pending_and_duplicate_decisions_are_rejected():
    p = proposal()
    review = QAFindingResolutionReview(
        proposal=p,
        decision="reject",
        actor="fixture-human",
        reviewed_at=NOW,
        comment="Evidence insufficient",
    )
    result = compare_reviews(p.previous, p.current, [review])
    assert result.pending_previous_findings == [p.finding_id]
    with pytest.raises(ValueError, match="Duplicate"):
        compare_reviews(p.previous, p.current, [review, review])


@pytest.mark.parametrize(
    "change", ["finding", "citation", "check", "revision", "criteria", "facet"]
)
def test_resolution_rejects_unbound_evidence(change):
    p = proposal().model_dump()
    if change == "finding":
        p["finding_id"] = "unknown"
    elif change == "citation":
        p["citations"][0]["quote"] = "return True"
    elif change == "check":
        p["check_ids"] = ["lint"]
    elif change == "revision":
        p["previous"] = p["current"]
    elif change == "criteria":
        # A modified report is rejected before it can authorize a resolution.
        p["current"]["criterion_matrix"][0]["criterion"] = "Different rule"
    else:
        p["current"]["inspection"]["inspected_facets"].remove("business")
    with pytest.raises(ValueError):
        QAFindingResolutionProposal.model_validate(p)


def test_resolution_cannot_be_replayed_against_another_report():
    p = proposal()
    review = QAFindingResolutionReview(
        proposal=p,
        decision="confirm",
        actor="fixture-human",
        reviewed_at=NOW,
        comment="Evidence checked",
    )
    other = p.current.model_copy(deep=True)
    other.model = "changed-metadata"
    with pytest.raises(ValueError):
        compare_reviews(p.previous, other, [review])


def test_resolution_review_cannot_predate_checks():
    with pytest.raises(ValueError, match="predates"):
        QAFindingResolutionReview(
            proposal=proposal(),
            decision="confirm",
            actor="fixture-human",
            reviewed_at="2000-01-01T00:00:00+00:00",
            comment="Too old",
        )


def test_python_team_entrypoint_rejects_future_resolution_decisions(tmp_path, monkeypatch):
    from ai_harness_compiler.models.team import TeamConfig
    from ai_harness_compiler.qa import project_for
    from ai_harness_compiler.team.runtime import prepare_team

    p = proposal()
    review = QAFindingResolutionReview(
        proposal=p,
        decision="confirm",
        actor="fixture-human",
        reviewed_at="2100-01-01T00:00:00+00:00",
        comment="Future fixture",
    )
    comparison = compare_reviews(p.previous, p.current, [review])
    config = TeamConfig(
        project=project_for(p.current.request),
        selected=["alpha", "beta"],
        request="Review fixture",
        mode="ask",
        repository_root=str(tmp_path),
        scrum_snapshot=p.current.request.snapshot,
        qa_report=p.current,
        qa_comparison=comparison,
    )
    monkeypatch.setattr(
        "ai_harness_compiler.qa_collection.assert_current_request", lambda *args: None
    )
    with pytest.raises(ValueError, match="future"):
        prepare_team(config, tmp_path / "team")
    assert not (tmp_path / "team").exists()
