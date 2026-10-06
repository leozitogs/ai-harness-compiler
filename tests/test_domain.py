"""Domain dimensions, uncertainty and migration are independent of model providers."""

import copy
import json
import socket
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.compiler import render
from ai_harness_compiler.migration import migrate_harness
from ai_harness_compiler.models import HarnessSpec, ProjectInput
from ai_harness_compiler.models.domain import DomainProfile
from ai_harness_compiler.pipeline import plan


def profile(status="declared"):
    return {
        "primary": "education",
        "secondary": ["content"],
        "archetype": "content-platform",
        "data": {
            "data_types": ["course-material"],
            "sensitivity": "internal",
            "contains_pii": False,
        },
        "risk": {"level": "medium", "categories": ["hallucination", "privacy"]},
        "status": status,
        "origin": "user-declaration" if status == "declared" else "supplied-hypothesis",
        "evidence_ids": ["domain-profile"],
        "rationale": "Profile supplied for review.",
    }


@pytest.mark.parametrize("status", ["declared", "hypothesis"])
def test_supplied_dimensions_survive_offline_pipeline(project, status, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Domain profiling must not use network")

    monkeypatch.setattr(socket, "socket", no_network)
    payload = project.model_dump()
    payload.update(domain=None, domain_profile=profile(status))
    spec = plan(ProjectInput.model_validate(payload))
    assert spec.project_dna.domain == DomainProfile.model_validate(profile(status))
    assert spec.project_dna.domain.confidence is None
    assert spec.project_dna.domain.data.contains_pii is False
    assert spec.project_dna.domain.risk.level == "medium"
    assert spec.project_dna.domain.archetype == "content-platform"
    assert HarnessSpec.model_validate_json(spec.model_dump_json()) == spec
    assert render(spec) == render(spec)
    Draft202012Validator(HarnessSpec.model_json_schema()).validate(spec.model_dump())


def test_missing_dimensions_remain_unknown(project):
    spec = plan(project)
    domain = spec.project_dna.domain
    assert domain.status == "declared" and domain.origin == "user-declaration"
    assert domain.archetype is None and domain.data.sensitivity == "unknown"
    assert domain.data.contains_pii is None and domain.risk.level == "unknown"
    project.domain = None
    uncertain = plan(project).project_dna.domain
    assert uncertain.primary is None and uncertain.origin == "unknown"
    assert uncertain.status == "DOMAIN_UNCERTAIN"


@pytest.mark.parametrize(
    "change",
    [
        {"primary": None},
        {"origin": "unknown"},
        {"confidence": 0.9},
        {"evidence_ids": []},
        {"secondary": ["education"]},
        {"secondary": ["content", "content"]},
        {"data": {"sensitivity": "made-up"}},
        {"data": {"data_types": ["x", "x"]}},
        {"risk": {"level": "critical"}},
        {"risk": {"categories": ["privacy", "privacy"]}},
        {"risk": {"categories": ["not-a-risk"]}},
        {"evidence_ids": ["domain-profile", "domain-profile"]},
        {"status": "DOMAIN_UNCERTAIN", "origin": "unknown"},
        {"status": "hypothesis", "origin": "supplied-hypothesis", "rationale": None},
    ],
)
def test_invalid_profiles_are_rejected(change):
    payload = profile()
    payload.update(change)
    with pytest.raises(ValidationError):
        DomainProfile.model_validate(payload)


def test_multiple_hypotheses_are_preserved_without_selecting_one(project):
    payload = project.model_dump()
    payload.update(
        domain=None,
        domain_profile={
            "status": "DOMAIN_UNCERTAIN",
            "origin": "unknown",
            "hypotheses": [
                {
                    "domain": "education",
                    "rationale": "Audience suggests learning.",
                    "evidence_ids": ["domain-profile"],
                },
                {
                    "domain": "content",
                    "rationale": "Backlog suggests publishing.",
                    "evidence_ids": ["domain-profile"],
                },
            ],
        },
    )
    spec = plan(ProjectInput.model_validate(payload))
    assert spec.project_dna.domain.primary is None
    assert len(spec.project_dna.domain.hypotheses) == 2
    assert spec.project_dna.domain.confidence is None
    assert any("not been independently evaluated" in item for item in spec.project_dna.unknowns)


def test_hypothesis_references_must_resolve_with_domain_scope(project):
    payload = project.model_dump()
    p = profile("hypothesis")
    p["hypotheses"] = [
        {"domain": "content", "rationale": "Candidate", "evidence_ids": ["backlog-1"]}
    ]
    payload.update(domain=None, domain_profile=p)
    with pytest.raises(ValidationError, match="incompatible"):
        plan(ProjectInput.model_validate(payload))


def test_legacy_domain_cannot_contradict_new_profile(project):
    payload = project.model_dump()
    payload["domain_profile"] = profile("hypothesis")
    with pytest.raises(ValidationError, match="agree"):
        ProjectInput.model_validate(payload)


@pytest.mark.parametrize("version", [1, 2])
def test_v1_v2_migrate_explicitly_without_invented_dimensions(version, tmp_path):
    source = Path(__file__).parent / f"fixtures/harness-v{version}.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    original = copy.deepcopy(payload)
    result = migrate_harness(payload)
    assert payload == original
    assert result.schema_version == "HarnessSpec/v3"
    assert result.project_dna.domain.primary == payload["project_dna"]["domain"]["primary"]
    assert result.project_dna.domain.confidence is None
    assert result.project_dna.domain.archetype is None
    assert result.project_dna.domain.risk.level == "unknown"
    output = tmp_path / "migrated.json"
    assert main(["migrate", str(source), "--output", str(output)]) == 0
    assert main(["compile", str(output), "--output", str(tmp_path / "build")]) == 0


@pytest.mark.parametrize("mutation", ["confidence", "digest", "status", "review"])
def test_legacy_invalid_or_reviewed_metadata_requires_manual_migration(mutation):
    source = Path(__file__).parent / "fixtures/harness-v2.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    if mutation == "confidence":
        payload["project_dna"]["domain"]["confidence"] = 0.9
    elif mutation == "digest":
        payload["project_dna"]["sources"][0]["sha256"] = "0" * 64
    elif mutation == "review":
        payload["project_dna"]["sources"][0]["verification_status"] = "verified"
    else:
        payload["project_dna"]["domain"]["status"] = "hypothesis"
    with pytest.raises(ValueError):
        migrate_harness(payload)


def test_ir_cannot_invent_dimensions_absent_from_input(project):
    payload = plan(project).model_dump()
    payload["project_dna"]["domain"]["risk"]["level"] = "high"
    with pytest.raises(ValidationError, match="additional classifications"):
        HarnessSpec.model_validate(payload)


def test_malformed_legacy_status_is_a_controlled_cli_error(tmp_path, capsys):
    source = Path(__file__).parent / "fixtures/harness-v2.json"
    payload = json.loads(source.read_text(encoding="utf-8"))
    payload["project_dna"]["domain"]["status"] = {"invalid": "mapping"}
    invalid = tmp_path / "legacy.json"
    invalid.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "migrated.json"
    assert main(["migrate", str(invalid), "--output", str(output)]) == 1
    assert "Unsupported legacy classification" in capsys.readouterr().err
    assert not output.exists()
