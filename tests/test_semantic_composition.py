"""Injected boundaries exercise component protocol integration, never semantic approval."""

import hashlib
import json
from typing import cast

import pytest
from jsonschema import Draft202012Validator
from test_semantic_analysis_v3 import fixture_analysis
from test_semantic_verification import FakeGenerator
from test_semantic_verification_v4 import advice

from ai_harness_compiler.cli import main
from ai_harness_compiler.semantic_composition import (
    CANDIDATE_COMPOSITION_PROGRAM_VERSION,
    COMPOSITION_PROMPT,
    CompositionProgramVersion,
    analyze_composition,
    audit_composition,
    component_audit_schema,
    composition_program_digest,
    composition_response_schema,
)


def test_generation_sources_and_explicit_guard_preserved(project):
    analysis = fixture_analysis(project)
    generator = FakeGenerator(analysis.proposal.model_dump())
    result = analyze_composition(analysis.extraction, generator)
    assert result == analysis
    assert result.findings[-1].guard_target_atom_ids
    packet = json.loads(generator.calls[0][0].split("\nINPUT DATA:\n", 1)[1])
    assert packet["context_atom_ids"]
    assert "expected_behavior" not in packet
    schema = composition_response_schema(analysis.extraction)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(analysis.proposal.model_dump())


def test_legacy_recipe_and_default_are_preserved(project):
    analysis = fixture_analysis(project)
    generator = FakeGenerator(analysis.proposal.model_dump())
    analyze_composition(analysis.extraction, generator)
    assert generator.calls[0][0].split("\nINPUT DATA:\n", 1)[0] == COMPOSITION_PROMPT
    assert hashlib.sha256(COMPOSITION_PROMPT.encode()).hexdigest() == (
        "c7db46d4ed1c910537aa092c0187608f91e24b186515ddcd97a8bfd7570cad87"
    )


def test_candidate_is_explicit_and_has_a_distinct_reproducible_fingerprint(project):
    analysis = fixture_analysis(project)
    generator = FakeGenerator(analysis.proposal.model_dump())
    result = analyze_composition(
        analysis.extraction, generator, program_version=CANDIDATE_COMPOSITION_PROGRAM_VERSION
    )
    assert result == analysis  # Injected output tests transport, not semantic improvement.
    assert "subject=constraint" in generator.calls[0][0]
    assert generator.calls[0][1] == composition_response_schema(analysis.extraction)
    baseline = composition_program_digest(analysis.extraction)
    candidate = composition_program_digest(
        analysis.extraction, CANDIDATE_COMPOSITION_PROGRAM_VERSION
    )
    assert baseline != candidate
    assert candidate == composition_program_digest(
        analysis.extraction, CANDIDATE_COMPOSITION_PROGRAM_VERSION
    )
    packet = json.loads(generator.calls[0][0].split("\nINPUT DATA:\n", 1)[1])
    assert "expected_behavior" not in packet
    assert "human_review" not in packet


def test_unknown_recipe_rejected_before_generator_call(project):
    analysis = fixture_analysis(project)
    generator = FakeGenerator(analysis.proposal.model_dump())
    with pytest.raises(ValueError, match="Unknown composition program"):
        analyze_composition(
            analysis.extraction,
            generator,
            program_version=cast(CompositionProgramVersion, "unknown"),
        )
    assert not generator.calls


@pytest.mark.parametrize("kind", ["business-rule", "requirement", "needs-clarification"])
def test_generation_schema_enforces_rule_component_shape(project, kind):
    analysis = fixture_analysis(project)
    data = analysis.proposal.model_dump()
    criterion = data["criteria"][0]
    criterion["kind"] = kind
    if kind != "business-rule":
        criterion["condition"] = criterion["outcome"] = None
    if kind == "needs-clarification":
        criterion["question"] = {
            "text": "Which business actor?",
            "impact": "authorization",
            "rationale": "Changes permission to act",
        }
    validator = Draft202012Validator(composition_response_schema(analysis.extraction))
    validator.validate(data)
    if kind == "business-rule":
        criterion["condition"] = None
    else:
        criterion["outcome"] = {"text": "Unexpected rule outcome", "source_atom_ids": ["atom-1"]}
    assert list(validator.iter_errors(data))


def test_atomic_audit_receives_exact_components_without_case_gold(project):
    analysis = fixture_analysis(project)
    generator = FakeGenerator(advice(analysis))
    report = audit_composition(analysis, generator, "fixture-model")
    assert report.analysis == analysis
    assert report.authority == "model-advisory"
    assert report.model_qualification == "not-established"
    payload = json.loads(generator.calls[0][0].split("\nINPUT DATA:\n", 1)[1])
    assert set(payload) == {
        "analysis_sha256",
        "findings",
        "sources",
        "disposition",
        "content_trust",
    }
    assert payload["findings"][0]["component_bindings"]


@pytest.mark.parametrize("name", ["condition", "outcome", "exception"])
def test_component_index_schema_constrained_by_kind(project, name):
    analysis = fixture_analysis(project)
    schema = component_audit_schema(analysis)
    data = advice(analysis)
    row = data["component_judgments"][0]
    row["component_name"] = name
    row["component_index"] = 0 if name == "exception" else None
    assert not list(Draft202012Validator(schema).iter_errors(data))
    row["component_index"] = None if name == "exception" else 0
    assert list(Draft202012Validator(schema).iter_errors(data))


def test_cli_v4_preserves_advisory_and_existing_output(project, tmp_path, monkeypatch):
    from ai_harness_compiler.adapters.codex_cli import CodexCompactModel

    analysis = fixture_analysis(project)
    input_path = tmp_path / "analysis.json"
    input_path.write_text(analysis.model_dump_json(), encoding="utf-8")
    output = tmp_path / "advice.json"
    monkeypatch.setattr(
        CodexCompactModel,
        "generate_json",
        lambda self, prompt, schema: json.dumps(advice(analysis)),
    )
    assert main(["verify-analysis-v4", str(input_path), "--output", str(output)]) == 0
    assert (
        json.loads(output.read_text(encoding="utf-8"))["schema_version"]
        == "SemanticVerifierReport/v4"
    )
    before = output.read_bytes()
    assert main(["verify-analysis-v4", str(input_path), "--output", str(output)]) == 1
    assert output.read_bytes() == before
