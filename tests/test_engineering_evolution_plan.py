"""The evolution queue preserves criteria and cannot bypass unfinished prerequisites."""

import hashlib
import json
from pathlib import Path

import pytest

from ai_harness_compiler.intake import load_project
from ai_harness_compiler.models.task import STAGES, TaskGraph
from ai_harness_compiler.pipeline import plan
from ai_harness_compiler.planning import decompose

ROOT = Path(__file__).resolve().parents[1]


def queue():
    return json.loads((ROOT / "planning/engineering-evolution.json").read_bytes())


def test_queue_binds_exact_canonical_criteria_dependencies_and_review_stages():
    data = queue()
    project = load_project(ROOT / "project-definition")
    canonical = {item.id: item for item in project.backlog}
    expected = {f"ahc-{i:03}" for i in range(31, 43)}
    ids = [entry["capability_id"] for entry in data["items"]]
    assert len(ids) == len(set(ids)) == 12 and set(ids) == expected
    for entry in data["items"]:
        item = canonical[entry["capability_id"]]
        assert entry["depends_on"] == item.depends_on
        index = project.backlog.index(item)
        assert entry["acceptance_source"] == (
            f"project-definition/project.yaml#/backlog/{index}/acceptance_criteria"
        )
        encoded = json.dumps(
            item.acceptance_criteria, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode()
        assert entry["acceptance_criteria_sha256"] == hashlib.sha256(encoded).hexdigest()
        assert len(item.acceptance_criteria) >= 4
        assert entry["status"] == "proposed" and entry["first_slice"] and entry["verification"]
        for stage_index, stage in enumerate(entry["stages"]):
            assert stage["id"] == f"{item.id}-{STAGES[stage_index]}"
            expected_dependencies = (
                [f"{item.id}-{STAGES[stage_index - 1]}"]
                if stage_index
                else [f"{dependency}-review" for dependency in item.depends_on]
            )
            assert stage["requires"] == expected_dependencies
            assert stage["status"] == "planned" and stage["deliverable"]
        assert len(entry["stages"]) == 4


def test_wave_order_is_acyclic_but_never_claims_external_prerequisites_completed():
    data = queue()
    project = load_project(ROOT / "project-definition")
    graph = plan(project).capability_graph
    selected = [entry["capability_id"] for entry in data["items"]]
    waves = [id_ for wave in data["waves"] for id_ in wave["capabilities"]]
    assert set(waves) == set(selected) and len(waves) == len(selected)
    order = {id_: position for position, id_ in enumerate(waves)}
    for entry in data["items"]:
        for dependency in entry["depends_on"]:
            if dependency in order:
                assert order[dependency] < order[entry["capability_id"]]
    # The roadmap is deliberately not an executable sprint with fake completed gates.
    with pytest.raises(ValueError, match="Unplanned prerequisites"):
        decompose(graph, selected)
    full = decompose(graph)
    assert TaskGraph.model_validate_json(full.model_dump_json()) == full
    assert len(full.tasks) == len(project.backlog) * 4
    assert full.execution_status == "not-run" and full.declared_completed_capabilities == []


def test_backlog_refinement_is_neither_sprint_assignment_nor_execution_authority():
    data = queue()
    assert data["status"] == "backlog-refinement" and data["execution_started"] is False
    assert data["sprint_assignment"] is None and data["capacity_confirmed"] is False
    assert data["estimates"] is None and data["model_invocations_authorized"] == 0
    assert data["existing_story_criteria_preserved"] is True
    assert data["existing_sprint_scope_preserved"] is True
    new_ids = {entry["capability_id"] for entry in data["items"]}
    for path in (ROOT / "planning").glob("sprint-*.json"):
        sprint = json.loads(path.read_bytes())
        if "selected_capabilities" in sprint:
            assert not new_ids.intersection(sprint["selected_capabilities"])
            assert not new_ids.intersection(sprint.get("declared_completed_capabilities", []))
