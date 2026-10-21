"""Synthetic replay checks contract behavior, not model efficacy or human approval."""

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from test_semantic_verification import FakeGenerator

from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.semantic_composition import (
    COMPOSITION_PROGRAM_VERSION,
    MATERIALITY_COMPOSITION_PROGRAM_VERSION,
    analyze_composition,
    composition_program_digest,
    composition_response_schema,
)

ROOT = Path(__file__).resolve().parents[1]
ROUND = ROOT / "docs/evidence/sprint-2-6-v33-development-20261020"
VERSION = MATERIALITY_COMPOSITION_PROGRAM_VERSION


def saved(case):
    return SemanticAnalysisV3.model_validate_json(
        (ROUND / "execution" / case / "analysis.json").read_bytes()
    )


def test_v33_recorded_fingerprints_and_default_remain_unchanged():
    protocol = json.loads((ROUND / "protocol-v2.json").read_bytes())
    assert COMPOSITION_PROGRAM_VERSION == "semantic-composition/v3.1"
    for row in protocol["cases"]:
        extraction = saved(row["case"]).extraction
        assert (
            composition_program_digest(extraction, "semantic-composition/v3.3")
            == row["program_sha256"]
        )
        assert composition_program_digest(extraction, VERSION) != row["program_sha256"]
        assert composition_response_schema(
            extraction, program_version=VERSION
        ) == composition_response_schema(extraction, program_version="semantic-composition/v3.3")


@pytest.mark.parametrize("case", ["dev-ambiguous", "dev-branding-conflict"])
def test_nonblocking_followup_does_not_remove_independent_business_blockers(case):
    original = saved(case)
    data = original.proposal.model_dump()
    data["issues"][-1]["impact"] = "implementation-detail"
    data["issues"][-1]["rationale"] = (
        "Synthetic contract example: preserve the obligation; execution detail is unresolved."
    )
    Draft202012Validator(
        composition_response_schema(original.extraction, program_version=VERSION)
    ).validate(data)
    result = analyze_composition(original.extraction, FakeGenerator(data), program_version=VERSION)
    assert result.disposition == "blocked"
    assert result.proposal.issues[:-1] == original.proposal.issues[:-1]
    assert result.proposal.context_findings == original.proposal.context_findings
    assert result.proposal.guards == original.proposal.guards
    assert result.snapshot_sha256 != original.snapshot_sha256
    # The stored real output is untouched and remains a failed human snapshot.
    assert saved(case).snapshot_sha256 == original.snapshot_sha256
    assert saved(case).proposal.issues[-1].impact == "rule"


@pytest.mark.parametrize("impact", ["rule", "authorization", "outcome", "precedence"])
def test_host_does_not_silently_downgrade_model_blockers(impact):
    original = saved("dev-ambiguous")
    data = original.proposal.model_dump()
    data["issues"][-1]["impact"] = impact
    result = analyze_composition(original.extraction, FakeGenerator(data), program_version=VERSION)
    assert result.proposal.model_dump() == data
    assert result.disposition == "blocked"


def test_v34_keeps_secondary_question_source_route_enforced():
    original = saved("dev-ambiguous")
    data = original.proposal.model_dump()
    data["criteria"][0]["uncertainties"] = [
        {"text": "A secondary question", "impact": "rule", "rationale": "Synthetic test"}
    ]
    with pytest.raises(ValueError, match="COMPOSITION_QUESTION_ROUTE"):
        analyze_composition(original.extraction, FakeGenerator(data), program_version=VERSION)


def test_unrecognized_recipe_fails_before_provider_call():
    original = saved("dev-ambiguous")
    generator = FakeGenerator(original.proposal.model_dump())
    with pytest.raises(ValueError, match="Unknown composition program"):
        analyze_composition(original.extraction, generator, program_version="invalid")
    assert generator.calls == []


def test_v34_frozen_protocol_and_preexecution_rejection_are_not_a_model_result():
    folder = ROOT / "docs/evidence/sprint-2-6-v34-development-20261020"
    raw = (folder / "protocol.json").read_bytes()
    protocol = json.loads(raw)
    event = json.loads((folder / "execution-status.json").read_bytes())
    assert event["protocol_sha256"] == hashlib.sha256(raw).hexdigest()
    assert event["status"] == "authorization-blocked"
    assert event["executor_started"] is False and event["calls_used"] == 0
    assert event["model_qualification"] == "not-established"
    assert event["compilation_eligibility"] == "not-authorized"
    assert protocol["program_version"] == VERSION
    assert protocol["budget"]["max_calls"] == 16
    assert protocol["budget"]["max_concurrency"] == 1
    assert protocol["budget"]["retries"] == protocol["budget"]["holdout_calls"] == 0
    assert (
        hashlib.sha256((folder / "runner-source.txt").read_bytes()).hexdigest()
        == (protocol["runner_sha256"])
    )
    for row in protocol["cases"]:
        assert (
            composition_program_digest(saved(row["case"]).extraction, VERSION)
            == (row["program_sha256"])
        )
