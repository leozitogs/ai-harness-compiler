"""Explicit migration of v1 baseline IR; never fabricate provenance for research."""

from typing import Any

from ai_harness_compiler.models import HarnessSpec, ProjectInput
from ai_harness_compiler.pipeline import plan


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
    result["schema_version"] = "HarnessSpec/v2"
    result["project_dna"] = {
        **dna,
        "schema_version": "ProjectDNA/v2",
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
