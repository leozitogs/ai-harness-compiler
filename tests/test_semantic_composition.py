"""Injected boundaries exercise component protocol integration, never semantic approval."""

import json

import pytest
from jsonschema import Draft202012Validator
from test_semantic_analysis_v3 import fixture_analysis
from test_semantic_verification import FakeGenerator
from test_semantic_verification_v4 import advice

from ai_harness_compiler.cli import main
from ai_harness_compiler.semantic_composition import (
    analyze_composition,
    audit_composition,
    component_audit_schema,
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
