"""Explicit migration of v1 baseline IR; never fabricate provenance for research."""

from typing import Any

from ai_harness_compiler.models import HarnessSpec, ProjectInput
from ai_harness_compiler.models.domain import DomainProfile
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.pipeline import plan


def migrate_domain(payload: Any) -> DomainProfile:
    if not isinstance(payload, dict) or set(payload) - {
        "primary",
        "status",
        "confidence",
        "evidence_ids",
    }:
        raise ValueError("Legacy domain profile has unsupported fields")
    if payload.get("confidence") is not None:
        raise ValueError("Legacy numeric confidence has no evaluation provenance; migrate manually")
    origins = {"declared": "user-declaration", "DOMAIN_UNCERTAIN": "unknown"}
    if not isinstance(payload.get("status"), str) or payload["status"] not in origins:
        raise ValueError("Unsupported legacy classification status")
    return DomainProfile.model_validate({**payload, "origin": origins[payload["status"]]})


def migrate_harness_v1(payload: dict[str, Any]) -> HarnessSpec:
    if payload.get("schema_version") != "HarnessSpec/v1":
        raise ValueError("Migration requires HarnessSpec/v1")
    dna = payload.get("project_dna")
    if not isinstance(dna, dict) or dna.get("schema_version") != "ProjectDNA/v1":
        raise ValueError("Migration requires ProjectDNA/v1")
    project = ProjectInput.model_validate(dna.get("project"))
    if project.evidence_pack:
        raise ValueError("Legacy baseline cannot contain an EvidencePack")
    expected = plan(project).project_dna
    evidence = dna.get("evidence")
    if not isinstance(evidence, list):
        raise ValueError("Legacy evidence must be a list")
    known = {item.id: item for item in expected.evidence}
    migrated = []
    for item in evidence:
        if (
            not isinstance(item, dict)
            or not isinstance(item.get("id"), str)
            or item["id"] not in known
        ):
            raise ValueError("Custom legacy evidence needs manual provenance migration")
        entry = known[item["id"]]
        legacy = entry.model_dump(include={"id", "source", "claim", "kind"})
        if item != legacy:
            raise ValueError("Legacy evidence differs from its declared project source")
        migrated.append(entry.model_dump())
    result = dict(payload)
    result["schema_version"] = "HarnessSpec/v3"
    result["project_dna"] = {
        **dna,
        "schema_version": "ProjectDNA/v3",
        "domain": migrate_domain(dna.get("domain")).model_dump(),
        "project": project.model_dump(),
        "sources": [item.model_dump() for item in expected.sources],
        "evidence": migrated,
    }
    decisions = payload.get("decisions")
    if not isinstance(decisions, list) or not all(isinstance(item, dict) for item in decisions):
        raise ValueError("Legacy decisions must be mappings")
    for item in decisions:
        references = item.get("evidence_ids")
        if not isinstance(references, list) or not all(isinstance(ref, str) for ref in references):
            raise ValueError("Legacy decision references must be a list of IDs")
    result["decisions"] = [
        {
            **item,
            "capability_ids": sorted(
                {
                    known[reference].capability_id
                    for reference in item.get("evidence_ids", [])
                    if reference in known and known[reference].capability_id is not None
                }
            ),
        }
        for item in decisions
    ]
    return HarnessSpec.model_validate(result)


def migrate_harness_v2(payload: dict[str, Any]) -> HarnessSpec:
    dna = payload.get("project_dna")
    if (
        payload.get("schema_version") != "HarnessSpec/v2"
        or not isinstance(dna, dict)
        or dna.get("schema_version") != "ProjectDNA/v2"
    ):
        raise ValueError("Migration requires HarnessSpec/v2 and ProjectDNA/v2")
    project = ProjectInput.model_validate(dna.get("project"))
    if project.domain_profile is not None:
        raise ValueError("Legacy IR cannot contain a multidimensional profile")
    sources = dna.get("sources")
    if not isinstance(sources, list) or not all(isinstance(item, dict) for item in sources):
        raise ValueError("Legacy sources must be mappings")
    old_digest = canonical_project_digest(project.model_dump(exclude={"domain_profile"}))
    new_digest = canonical_project_digest(project.model_dump())
    updated_sources = []
    for source in sources:
        updated = dict(source)
        if source.get("id") == "project-manifest":
            if source.get("sha256") != old_digest:
                raise ValueError("Legacy canonical digest does not match project input")
            if source.get("verification_status", "unverified") != "unverified":
                raise ValueError(
                    "Reviewed canonical source requires manual migration and re-review"
                )
            updated["sha256"] = new_digest
        updated_sources.append(updated)
    result = {
        **payload,
        "schema_version": "HarnessSpec/v3",
        "project_dna": {
            **dna,
            "schema_version": "ProjectDNA/v3",
            "project": project.model_dump(),
            "domain": migrate_domain(dna.get("domain")).model_dump(),
            "sources": updated_sources,
        },
    }
    return HarnessSpec.model_validate(result)


def migrate_harness(payload: dict[str, Any]) -> HarnessSpec:
    if payload.get("schema_version") == "HarnessSpec/v1":
        return migrate_harness_v1(payload)
    if payload.get("schema_version") == "HarnessSpec/v2":
        return migrate_harness_v2(payload)
    raise ValueError("Migration requires HarnessSpec/v1 or HarnessSpec/v2")
