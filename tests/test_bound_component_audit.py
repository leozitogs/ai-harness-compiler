"""Schema/host invariants using saved public outputs, never new model calls."""

import hashlib
import json
from copy import deepcopy
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from test_semantic_verification import FakeGenerator

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_verification_v4 import VerifierProposalV4
from ai_harness_compiler.semantic_composition import (
    BOUND_COMPONENT_AUDIT_PROGRAM_VERSION,
    audit_composition,
    component_audit_program_digest,
    component_audit_schema,
)

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/sprint-2-6-v34-development-20261020/execution"
VERSION = BOUND_COMPONENT_AUDIT_PROGRAM_VERSION


def saved(case="dev-compatible-rules"):
    folder = EVIDENCE / case
    analysis = SemanticAnalysisV3.model_validate_json((folder / "analysis.json").read_bytes())
    proposal = json.loads((folder / "audit-response.txt").read_bytes())
    return analysis, proposal


def test_all_eight_historical_request_schema_fingerprints_are_unchanged():
    for folder in sorted(EVIDENCE.iterdir()):
        if not folder.is_dir():
            continue
        analysis, _ = saved(folder.name)
        start = json.loads((folder / "audit-call-start.json").read_bytes())
        assert (
            canonical_project_digest(component_audit_schema(analysis))
            == (start["response_schema_sha256"])
        )
        assert component_audit_program_digest(analysis) != component_audit_program_digest(
            analysis, VERSION
        )


def test_saved_mutated_digest_is_rejected_by_new_schema_and_by_host():
    analysis, proposal = saved("dev-new-domain")
    # This parses under the old response schema, but has always failed host binding.
    Draft202012Validator(component_audit_schema(analysis)).validate(proposal)
    schema = component_audit_schema(analysis, program_version=VERSION)
    Draft202012Validator.check_schema(schema)
    assert list(Draft202012Validator(schema).iter_errors(proposal))
    generator = FakeGenerator(proposal)
    with pytest.raises(ValueError, match="Verifier finding digest or exact source binding differs"):
        audit_composition(analysis, generator, "saved-response", program_version=VERSION)
    assert len(generator.calls) == 1
    assert generator.calls[0][1] == schema


def test_valid_saved_advice_keeps_free_judgments_and_advisory_authority():
    analysis, proposal = saved()
    schema = component_audit_schema(analysis, program_version=VERSION)
    validator = Draft202012Validator(schema)
    validator.validate(proposal)
    generator = FakeGenerator(proposal)
    report = audit_composition(analysis, generator, "saved-response", program_version=VERSION)
    assert report.proposal == VerifierProposalV4.model_validate(proposal)
    assert report.authority == "model-advisory"
    assert report.semantic_status == "not-established"
    assert report.compilation_eligibility == "not-authorized"
    for support in ("contradicts", "insufficient-evidence"):
        negative = deepcopy(proposal)
        for row in negative["findings"]:
            row["support"] = support
        for row in negative["component_judgments"]:
            row["support"] = support
        validator.validate(negative)
        assert (
            audit_composition(
                analysis, FakeGenerator(negative), "injected-negative", program_version=VERSION
            )
            .proposal.findings[0]
            .support
            == support
        )


@pytest.mark.parametrize("target", ["analysis", "finding-id", "finding-digest", "source", "quote"])
def test_bound_schema_rejects_changed_structural_identity(target):
    analysis, proposal = saved()
    if target == "analysis":
        proposal["analysis_sha256"] = "0" * 64
    elif target == "finding-id":
        proposal["findings"][0]["finding_id"] = "unknown"
    elif target == "finding-digest":
        proposal["findings"][0]["finding_sha256"] = "0" * 64
    elif target == "source":
        proposal["findings"][0]["source_atom_ids"] = ["unknown"]
    else:
        proposal["source_coverage"][0]["quote_sha256"] = "0" * 64
    assert list(
        Draft202012Validator(component_audit_schema(analysis, program_version=VERSION)).iter_errors(
            proposal
        )
    )


def test_new_schema_does_not_replace_complete_inventory_validation():
    analysis, proposal = saved()
    proposal["findings"][0] = deepcopy(proposal["findings"][1])
    Draft202012Validator(component_audit_schema(analysis, program_version=VERSION)).validate(
        proposal
    )
    with pytest.raises(ValueError, match="assess every finding exactly once"):
        audit_composition(
            analysis, FakeGenerator(proposal), "injected-duplicate", program_version=VERSION
        )


def test_unknown_audit_recipe_fails_before_generator_call():
    analysis, proposal = saved()
    generator = FakeGenerator(proposal)
    with pytest.raises(ValueError, match="Unknown component audit program"):
        audit_composition(analysis, generator, "unused", program_version="unknown")
    assert generator.calls == []


@pytest.mark.parametrize("field,value", [("component_index", 99), ("source_atom_ids", ["unknown"])])
def test_bound_schema_rejects_invented_component_identity(field, value):
    analysis, proposal = saved()
    proposal["component_judgments"][0][field] = value
    assert list(
        Draft202012Validator(component_audit_schema(analysis, program_version=VERSION)).iter_errors(
            proposal
        )
    )


def test_new_schema_accepts_analysis_without_rule_components(project):
    from test_semantic_analysis_v3 import fixture_analysis
    from test_semantic_verification_v4 import advice

    data = fixture_analysis(project, guards=False).model_dump()
    for criterion in data["proposal"]["criteria"]:
        criterion.update(kind="requirement", condition=None, outcome=None, exceptions=[])
    analysis = SemanticAnalysisV3.model_validate(data)
    proposal = advice(analysis)
    assert not proposal["component_judgments"]
    schema = component_audit_schema(analysis, program_version=VERSION)
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(proposal)
    report = audit_composition(
        analysis,
        FakeGenerator(proposal),
        "injected-requirements",
        program_version=VERSION,
    )
    assert report.proposal == VerifierProposalV4.model_validate(proposal)


def test_exception_index_is_bound_to_the_actual_component(project):
    from test_semantic_analysis_v3 import fixture_analysis
    from test_semantic_verification_v4 import advice

    data = fixture_analysis(project, guards=False).model_dump()
    criterion = data["proposal"]["criteria"][0]
    criterion["exceptions"] = [
        {"text": "Synthetic exception", "source_atom_ids": [criterion["source_atom_id"]]}
    ]
    analysis = SemanticAnalysisV3.model_validate(data)
    proposal = advice(analysis)
    validator = Draft202012Validator(component_audit_schema(analysis, program_version=VERSION))
    validator.validate(proposal)
    exception = next(
        row for row in proposal["component_judgments"] if row["component_name"] == "exception"
    )
    assert exception["component_index"] == 0
    exception["component_index"] = 1
    assert list(validator.iter_errors(proposal))


def test_offline_proof_binds_saved_sources_without_claiming_new_model_execution():
    proof = json.loads(
        (ROOT / "docs/evidence/sprint-2-6-audit-bindings-20261020/offline-check.json").read_bytes()
    )
    assert proof["model_calls"] == 0 and proof["holdout_read"] is False
    assert proof["provider_schema_compatibility"] == "not-tested"
    assert proof["incident_operational_resolution"] == "not-established"
    for row in proof["cases"]:
        assert (
            hashlib.sha256((ROOT / row["analysis_path"]).read_bytes()).hexdigest()
            == (row["analysis_file_sha256"])
        )
        raw = (ROOT / row["saved_response_path"]).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row["saved_response_sha256"]
        analysis = SemanticAnalysisV3.model_validate_json(
            (ROOT / row["analysis_path"]).read_bytes()
        )
        schema = component_audit_schema(analysis, program_version=VERSION)
        assert canonical_project_digest(schema) == row["bound_response_schema_sha256"]
        assert component_audit_program_digest(analysis, VERSION) == row["bound_program_sha256"]
        assert (not any(Draft202012Validator(schema).iter_errors(json.loads(raw)))) == (
            row["saved_response_conforms_to_bound_schema"]
        )
