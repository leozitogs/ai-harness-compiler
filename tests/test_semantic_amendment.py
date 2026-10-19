"""Amendment integration tests bind omissions without repairing or approving input."""

import json

import pytest
from jsonschema import Draft202012Validator
from test_semantic_assessment import fixtures
from test_semantic_verification import FakeGenerator
from test_semantic_verification_v3 import advice, missing_question

from ai_harness_compiler.cli import main
from ai_harness_compiler.semantic_verification import (
    verification_response_schema_v3,
    verify_complete,
)


def test_missing_question_is_returned_without_host_repair_or_expected_labels(project):
    _, _, analysis = fixtures(project)
    generator = FakeGenerator(missing_question(analysis))
    result = verify_complete(analysis, generator, "fixture-model")
    assert result.analysis == analysis
    assert result.proposal.omissions[0].kind == "question"
    payload = json.loads(generator.calls[0][0].split("\nINPUT DATA:\n", 1)[1])
    assert set(payload) == {"packet", "disposition", "finding_digests"}
    assert "expected_behavior" not in payload["packet"]
    assert result.compilation_eligibility == "not-authorized"
    assert result.semantic_status == "not-established"


@pytest.mark.parametrize("kind", ["rule", "question", "conflict"])
def test_omission_schema_rejects_incompatible_impact(project, kind):
    _, _, analysis = fixtures(project)
    schema = verification_response_schema_v3(analysis)
    Draft202012Validator.check_schema(schema)
    data = advice(analysis)
    data["omissions"] = [
        {
            "id": "missing-item",
            "kind": kind,
            "text": "Fixture",
            "rationale": "Fixture",
            "source_atom_ids": ["atom-1", "atom-2"],
            "impact": "rule" if kind == "question" else None,
        }
    ]
    assert not list(Draft202012Validator(schema).iter_errors(data))
    data["omissions"][0]["impact"] = None if kind == "question" else "rule"
    assert list(Draft202012Validator(schema).iter_errors(data))


def test_verifier_v3_cli_saves_advisory_only(project, tmp_path, monkeypatch):
    from ai_harness_compiler.adapters.codex_cli import CodexCompactModel

    _, _, analysis = fixtures(project)
    input_path = tmp_path / "analysis.json"
    input_path.write_text(analysis.model_dump_json(), encoding="utf-8")
    output = tmp_path / "advice.json"
    monkeypatch.setattr(
        CodexCompactModel,
        "generate_json",
        lambda self, prompt, schema: json.dumps(missing_question(analysis)),
    )
    assert main(["verify-analysis-v3", str(input_path), "--output", str(output)]) == 0
    result = json.loads(output.read_text(encoding="utf-8"))
    assert result["schema_version"] == "SemanticVerifierReport/v3"
    assert result["authority"] == "model-advisory"
    assert result["model_qualification"] == "not-established"
    assert main(["verify-analysis-v3", str(input_path), "--output", str(output)]) == 1


@pytest.mark.parametrize("behavior", ["ready", "blocked"])
def test_provider_schema_binds_materiality_to_actual_finding_kind(project, behavior):
    _, _, analysis = fixtures(project, behavior=behavior)
    schema = verification_response_schema_v3(analysis)
    data = advice(analysis)
    assert not list(Draft202012Validator(schema).iter_errors(data))
    data["findings"][0]["materiality"] = (
        "not-applicable" if behavior == "blocked" else "appropriate"
    )
    assert list(Draft202012Validator(schema).iter_errors(data))
