"""Injected calls verify graph isolation and honesty, not model quality."""

import threading

import pytest
from pydantic import ValidationError

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import (
    CompactAnalysisSpec,
    CompactProposal,
    compact_input,
)
from ai_harness_compiler.models.comparison import ComparisonReport
from ai_harness_compiler.team.comparison import ComparisonCandidateConfig, run_comparison


def proposal(extraction, note="Fixture rationale", outcome="Fixture outcome"):
    return CompactAnalysisSpec(
        extraction=extraction,
        interpretation=CompactProposal.model_validate(
            {
                "criteria": [
                    {
                        "kind": "business-rule",
                        "condition": "Fixture condition",
                        "outcome": outcome,
                        "note": note,
                    }
                    for _ in compact_input(extraction).criteria
                ]
            }
        ),
    )


def metadata():
    return {
        "local": ComparisonCandidateConfig("ollama", "fixture-local", "a" * 64),
        "cloud": ComparisonCandidateConfig("codex-cli", "fixture-requested", "b" * 64),
    }


def test_independent_calls_really_fan_out_and_return_in_config_order(project):
    extraction = extract_grounding(project)
    barrier = threading.Barrier(2, timeout=5)
    received = []

    def call(value):
        received.append(value)
        barrier.wait()
        return proposal(value)

    report = run_comparison(extraction, {"cloud": call, "local": call}, metadata())
    assert len(received) == 2
    assert received[0] is not received[1]
    assert received[0].request is not received[1].request
    assert all(value is not extraction for value in received)
    assert [c.id for c in report.candidates] == ["local", "cloud"]
    assert [c.program_sha256 for c in report.candidates] == ["a" * 64, "b" * 64]
    assert report.criterion_agreements == list(range(len(compact_input(extraction).criteria)))
    assert report.criterion_disagreements == []
    assert report.human_review_required is True
    assert report.semantic_status == report.model_qualification == "not-established"
    assert all(c.reported_model is None for c in report.candidates)
    assert all(c.compact_analysis.understanding.review is None for c in report.candidates)


@pytest.mark.parametrize("difference", ["note", "outcome"])
def test_exact_behavior_comparison_excludes_rationale_only(project, difference):
    extraction = extract_grounding(project)

    def right(value):
        return proposal(value, **{difference: "Other fixture value"})

    report = run_comparison(extraction, {"local": proposal, "cloud": right}, metadata())
    indices = list(range(len(compact_input(extraction).criteria)))
    assert report.criterion_agreements == (indices if difference == "note" else [])
    assert report.criterion_disagreements == ([] if difference == "note" else indices)


@pytest.mark.parametrize(
    ("exception", "status", "code"),
    [
        (TimeoutError("secret timeout"), "timeout", "provider-timeout"),
        (RuntimeError("private prompt"), "error", "provider-error"),
        (ValueError("private proposal"), "error", "invalid-proposal"),
    ],
)
def test_one_failed_branch_keeps_other_and_sanitizes_errors(project, exception, status, code):
    extraction = extract_grounding(project)

    def failed(value):
        raise exception

    report = run_comparison(extraction, {"local": failed, "cloud": proposal}, metadata())
    assert [r.status for r in report.candidates] == [status, "completed"]
    assert report.candidates[0].error_code == code
    assert report.unavailable_criteria == list(range(len(compact_input(extraction).criteria)))
    assert report.criterion_agreements == report.criterion_disagreements == []
    assert str(exception) not in report.model_dump_json()


def test_mutated_extraction_is_rejected_without_contaminating_other_branch(project):
    extraction = extract_grounding(project)
    original = extraction.model_dump()

    def corrupt(value):
        value.atoms[0].__dict__["quote"] = "Malicious change"
        return proposal(value)

    report = run_comparison(extraction, {"local": corrupt, "cloud": proposal}, metadata())
    assert report.candidates[0].error_code == "invalid-proposal"
    assert report.candidates[1].status == "completed"
    assert extraction.model_dump() == original


@pytest.mark.parametrize(
    "tamper",
    ["total", "wall", "inventory", "digest", "promotion", "duplicate", "provider", "nested"],
)
def test_contradictory_reports_and_mutable_children_rejected(project, tamper):
    extraction = extract_grounding(project)
    report = run_comparison(extraction, {"local": proposal, "cloud": proposal}, metadata())
    data = report.model_dump()
    if tamper == "total":
        data["total_call_seconds"] += 1
    elif tamper == "wall":
        data["wall_time_seconds"] = 0.0
    elif tamper == "inventory":
        data["criterion_disagreements"] = [0]
    elif tamper == "digest":
        data["input_sha256"] = "0" * 64
    elif tamper == "promotion":
        data["human_review_required"] = False
    elif tamper == "duplicate":
        data["candidates"][1]["id"] = data["candidates"][0]["id"]
    elif tamper == "provider":
        data["candidates"][1]["provider"] = "ollama"
    else:
        report.candidates[0].compact_analysis.interpretation.criteria[0].__dict__["kind"] = (
            "requirement"
        )
        data = report.model_dump()
    with pytest.raises(ValidationError):
        ComparisonReport.model_validate(data)


@pytest.mark.parametrize("concurrency", [0, 3, True])
def test_invalid_concurrency_does_not_call_any_provider(project, concurrency):
    calls = []

    def call(value):
        calls.append(value)
        return proposal(value)

    with pytest.raises(ValueError):
        run_comparison(
            extract_grounding(project), {"local": call, "cloud": call}, metadata(), concurrency
        )
    assert calls == []


@pytest.mark.parametrize("metric", ["wall_time_seconds", "total_call_seconds"])
@pytest.mark.parametrize("value", [float("nan"), float("inf"), -1.0])
def test_nonfinite_or_negative_metrics_cannot_establish_a_report(project, metric, value):
    extraction = extract_grounding(project)
    report = run_comparison(extraction, {"local": proposal, "cloud": proposal}, metadata())
    data = report.model_dump()
    data[metric] = value
    with pytest.raises(ValidationError):
        ComparisonReport.model_validate(data)


def test_provider_diversity_is_validated_before_execution(project):
    calls = []

    def call(value):
        calls.append(value)
        return proposal(value)

    configs = metadata()
    configs["cloud"] = ComparisonCandidateConfig("ollama", "another-local")
    with pytest.raises(ValueError):
        run_comparison(extract_grounding(project), {"local": call, "cloud": call}, configs)
    assert calls == []
