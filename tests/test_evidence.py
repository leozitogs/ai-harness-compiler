"""Provenance, reference scopes and explicit IR migration without network access."""

import copy
import json
import socket
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.compiler import compile_harness, render
from ai_harness_compiler.migration import migrate_harness_v1
from ai_harness_compiler.models import HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.evidence import EvidencePack, SourceRecord
from ai_harness_compiler.pipeline import plan

LEGACY = Path(__file__).parent / "fixtures/harness-v1.json"


def research_pack(capability_id="material-library"):
    return {
        "schema_version": "EvidencePack/v1",
        "sources": [
            {
                "id": "paper",
                "location": "https://example.invalid/paper",
                "origin": "external-research",
                "collected_at": "2026-10-06T10:00:00Z",
            }
        ],
        "evidence": [
            {
                "id": "paper-claim",
                "source_id": "paper",
                "source": "https://example.invalid/paper#section-1",
                "claim": "A submitted research claim, not independently verified.",
                "kind": "research",
                "scope": "capability",
                "capability_id": capability_id,
            }
        ],
    }


def test_baseline_provenance_is_canonical_and_not_verification(project):
    spec = plan(project)
    source = spec.project_dna.sources[0]
    assert source.origin == "user-declaration" and source.verification_status == "unverified"
    assert len(source.sha256) == 64 and source.collected_at is None
    assert all(item.source_id == source.id for item in spec.project_dna.evidence)
    assert plan(project) == spec
    changed = project.model_copy(deep=True)
    changed.conception = "Different declared intent"
    assert plan(changed).project_dna.sources[0].sha256 != source.sha256


def test_supplied_research_survives_roundtrip_and_build_without_network(
    project, tmp_path, monkeypatch
):
    def no_network(*args, **kwargs):
        raise AssertionError("Evidence metadata must not fetch source content")

    monkeypatch.setattr(socket, "socket", no_network)
    payload = project.model_dump()
    payload["evidence_pack"] = research_pack()
    spec = plan(ProjectInput.model_validate(payload))
    assert spec.project_dna.sources[-1].verification_status == "unverified"
    assert "paper-claim" in spec.capability_graph.capabilities[0].evidence_ids
    assert spec.project_dna.evidence[0].kind == "declared"
    assert spec.project_dna.evidence[-1].kind == "research"
    assert HarnessSpec.model_validate_json(spec.model_dump_json()) == spec
    output = compile_harness(spec, tmp_path / "build")
    pack = EvidencePack.model_validate_json(
        (output / ".ai/evidence/pack.json").read_text(encoding="utf-8")
    )
    assert pack.sources == spec.project_dna.sources
    assert pack.evidence == spec.project_dna.evidence
    assert render(spec) == render(spec)
    Draft202012Validator(HarnessSpec.model_json_schema()).validate(spec.model_dump())


@pytest.mark.parametrize(
    "case",
    ["source-missing", "source-duplicate", "entry-duplicate", "origin", "locator", "capability"],
)
def test_invalid_input_pack_is_rejected(project, case):
    pack = research_pack()
    if case == "source-missing":
        pack["evidence"][0]["source_id"] = "missing"
    elif case == "source-duplicate":
        pack["sources"].append(copy.deepcopy(pack["sources"][0]))
    elif case == "entry-duplicate":
        pack["evidence"].append(copy.deepcopy(pack["evidence"][0]))
    elif case == "origin":
        pack["evidence"][0]["kind"] = "declared"
    elif case == "locator":
        pack["evidence"][0]["source"] = "https://another.invalid/paper"
    else:
        pack["evidence"][0]["capability_id"] = "missing"
    payload = project.model_dump()
    payload["evidence_pack"] = pack
    with pytest.raises(ValidationError):
        ProjectInput.model_validate(payload)


@pytest.mark.parametrize(
    "case",
    [
        "missing",
        "duplicate",
        "wrong-capability",
        "wrong-decision",
        "duplicate-decision",
        "wrong-domain",
        "duplicate-domain",
        "rejected",
        "unknown-decision-capability",
    ],
)
def test_ir_rejects_invalid_reference_scopes_before_writing(project, tmp_path, case):
    payload = plan(project).model_dump()
    node = payload["capability_graph"]["capabilities"][0]
    if case == "missing":
        node["evidence_ids"] = ["missing"]
    elif case == "duplicate":
        node["evidence_ids"] *= 2
    elif case == "wrong-capability":
        node["evidence_ids"] = ["backlog-2"]
    elif case == "wrong-decision":
        payload["decisions"][0]["evidence_ids"] = ["backlog-1"]
    elif case == "duplicate-decision":
        payload["decisions"][0]["evidence_ids"] *= 2
    elif case == "wrong-domain":
        payload["project_dna"]["domain"]["evidence_ids"] = ["project-intent"]
    elif case == "duplicate-domain":
        payload["project_dna"]["domain"]["evidence_ids"] *= 2
    elif case == "rejected":
        payload["project_dna"]["sources"][0]["verification_status"] = "rejected"
    else:
        payload["decisions"][0]["capability_ids"] = ["missing"]
    output = tmp_path / "invalid"
    with pytest.raises(ValidationError):
        compile_harness(HarnessSpec.model_validate(payload), output)
    assert not output.exists()


def test_capability_decision_accepts_matching_evidence(project):
    payload = plan(project).model_dump()
    payload["decisions"][0].update(evidence_ids=["backlog-1"], capability_ids=["material-library"])
    assert HarnessSpec.model_validate(payload).decisions[0].capability_ids == ["material-library"]


@pytest.mark.parametrize(
    "changes",
    [
        {"collected_at": None},
        {"collected_at": "2026-10-06T10:00:00"},
        {"collected_at": "2026-99-01T10:00:00Z"},
        {"sha256": "bad"},
        {"verification_status": "verified"},
        {"verified_by": "reviewer"},
    ],
)
def test_source_requires_honest_well_formed_metadata(changes):
    payload = research_pack()["sources"][0]
    payload.update(changes)
    with pytest.raises(ValidationError):
        SourceRecord.model_validate(payload)


def test_verified_metadata_requires_trace_and_timestamp_order():
    payload = research_pack()["sources"][0]
    payload.update(
        verification_status="verified",
        sha256="a" * 64,
        verified_by="human-reviewer",
        verified_at="2026-10-06T11:00:00Z",
    )
    assert SourceRecord.model_validate(payload).verified_by == "human-reviewer"
    payload["verified_at"] = "2026-10-06T09:00:00Z"
    with pytest.raises(ValidationError, match="precede"):
        SourceRecord.model_validate(payload)


def test_reserved_ids_cannot_replace_canonical_sources(project):
    payload = project.model_dump()
    pack = research_pack()
    pack["sources"][0]["id"] = "project-manifest"
    pack["evidence"][0]["source_id"] = "project-manifest"
    payload["evidence_pack"] = pack
    with pytest.raises(ValidationError, match="Source IDs"):
        plan(ProjectInput.model_validate(payload))


def test_explicit_migration_preserves_legacy_claims_and_protects_files(tmp_path, capsys):
    payload = json.loads(LEGACY.read_text(encoding="utf-8"))
    original = copy.deepcopy(payload)
    migrated = migrate_harness_v1(payload)
    assert payload == original
    assert migrated.schema_version == "HarnessSpec/v2"
    assert migrated.project_dna.schema_version == "ProjectDNA/v2"
    for entry, old in zip(
        migrated.project_dna.evidence, payload["project_dna"]["evidence"], strict=True
    ):
        assert entry.model_dump(include={"id", "source", "claim", "kind"}) == old
    assert main(["compile", str(LEGACY), "--output", str(tmp_path / "bad")]) == 1
    assert "explicit migration" in capsys.readouterr().err
    output = tmp_path / "migrated.json"
    assert main(["migrate", str(LEGACY), "--output", str(output)]) == 0
    before = output.read_bytes()
    assert main(["migrate", str(LEGACY), "--output", str(output)]) == 1
    assert output.read_bytes() == before
    assert main(["compile", str(output), "--output", str(tmp_path / "good")]) == 0


def test_migration_refuses_unknown_legacy_provenance():
    payload = json.loads(LEGACY.read_text(encoding="utf-8"))
    payload["project_dna"]["evidence"][0]["kind"] = "research"
    with pytest.raises(ValueError, match="differs"):
        migrate_harness_v1(payload)


def test_dna_validates_sources_without_requiring_harness(project):
    payload = plan(project).project_dna.model_dump()
    payload["evidence"][0]["source_id"] = "missing"
    with pytest.raises(ValidationError, match="source"):
        ProjectDNA.model_validate(payload)


def test_canonical_manifest_digest_is_checked_before_export(project, tmp_path):
    spec = plan(project)
    spec.project_dna.sources[0].sha256 = "0" * 64
    output = tmp_path / "tampered"
    with pytest.raises(ValidationError, match="provenance"):
        compile_harness(spec, output)
    assert not output.exists()


def test_rejected_research_is_preserved_but_not_linked(project):
    payload = project.model_dump()
    payload["evidence_pack"] = research_pack()
    payload["evidence_pack"]["sources"][0]["verification_status"] = "rejected"
    spec = plan(ProjectInput.model_validate(payload))
    assert spec.project_dna.sources[-1].verification_status == "rejected"
    assert "paper-claim" not in spec.capability_graph.capabilities[0].evidence_ids


def test_migration_rejects_malformed_reference_types():
    payload = json.loads(LEGACY.read_text(encoding="utf-8"))
    payload["decisions"][0]["evidence_ids"] = [{"unexpected": "mapping"}]
    with pytest.raises(ValueError, match="list of IDs"):
        migrate_harness_v1(payload)


def test_canonical_claim_cannot_disagree_with_the_project_input(project):
    payload = plan(project).model_dump()
    payload["project_dna"]["evidence"][0]["claim"] = "A claim absent from the input"
    with pytest.raises(ValidationError, match="Canonical evidence"):
        HarnessSpec.model_validate(payload)


def test_declared_domain_cannot_cite_research_as_declaration(project):
    payload = project.model_dump()
    pack = research_pack()
    pack["evidence"][0].update(scope="domain", capability_id=None)
    payload["evidence_pack"] = pack
    dna = plan(ProjectInput.model_validate(payload)).project_dna.model_dump()
    dna["domain"]["evidence_ids"] = ["paper-claim"]
    with pytest.raises(ValidationError, match="declared evidence"):
        ProjectDNA.model_validate(dna)
