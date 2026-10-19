"""Component bindings and guard mappings use synthetic evidence, never model approval."""

import copy

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.semantic_analysis_v3 import (
    ComponentBinding,
    SemanticAnalysisV3,
)


def fixture_analysis(project, guards=True):
    extraction = extract_grounding(project)
    criteria = [atom for atom in extraction.atoms if atom.kind == "acceptance-criterion"]
    context = compact_context(extraction)
    proposal = {
        "criteria": [
            {
                "source_atom_id": atom.id,
                "kind": "business-rule",
                "condition": {"text": "Synthetic condition", "source_atom_ids": [atom.id]},
                "outcome": {"text": "Synthetic outcome", "source_atom_ids": [atom.id]},
                "note": "Synthetic component binding, not semantic success",
            }
            for atom in criteria
        ],
        "guards": [
            {
                "id": "authorization-guard",
                "target_scope": "criteria",
                "condition": {
                    "text": "Synthetic authorization condition",
                    "source_atom_ids": [context[0].id],
                },
                "effect": {
                    "text": "Synthetic authorization effect",
                    "source_atom_ids": [context[1].id],
                },
                "target_criterion_atom_ids": [criteria[0].id],
                "note": "Synthetic guard mapping",
            }
        ]
        if guards
        else [],
    }
    return SemanticAnalysisV3.model_validate(
        {"extraction": extraction.model_dump(), "proposal": proposal}
    )


def test_compound_components_and_guard_mapping_stay_separate(project):
    analysis = fixture_analysis(project)
    rule, guard = analysis.findings[0], analysis.findings[-1]
    original = next(
        atom for atom in analysis.extraction.atoms if atom.kind == "acceptance-criterion"
    )
    assert rule.text == original.quote
    assert [(item.name, item.index) for item in rule.component_bindings] == [
        ("condition", None),
        ("outcome", None),
    ]
    assert guard.guard_target_scope == "criteria"
    assert guard.guard_target_atom_ids == [original.id]
    assert original.id not in guard.source_atom_ids
    assert {id_ for binding in guard.component_bindings for id_ in binding.source_atom_ids} == set(
        guard.source_atom_ids
    )
    assert analysis.disposition == "ready"
    assert SemanticAnalysisV3.model_validate_json(analysis.model_dump_json()) == analysis
    Draft202012Validator(analysis.model_json_schema()).validate(analysis.model_dump())


def test_swapping_component_sources_changes_hash_even_when_union_and_text_are_unchanged(project):
    data = fixture_analysis(project, guards=False).model_dump()
    criterion = data["proposal"]["criteria"][0]
    other = compact_context(fixture_analysis(project).extraction)[0].id
    criterion["outcome"]["source_atom_ids"] = [other]
    original = SemanticAnalysisV3.model_validate(data)
    changed = copy.deepcopy(data)
    row = changed["proposal"]["criteria"][0]
    row["condition"]["source_atom_ids"], row["outcome"]["source_atom_ids"] = (
        row["outcome"]["source_atom_ids"],
        row["condition"]["source_atom_ids"],
    )
    swapped = SemanticAnalysisV3.model_validate(changed)
    left, right = original.findings[0], swapped.findings[0]
    assert left.source_atom_ids == right.source_atom_ids
    assert (left.condition, left.outcome) == (right.condition, right.outcome)
    assert left.sha256 != right.sha256
    assert original.snapshot_sha256 != swapped.snapshot_sha256


def test_exception_positions_and_sources_are_part_of_finding_digest(project):
    data = fixture_analysis(project, guards=False).model_dump()
    context = compact_context(fixture_analysis(project).extraction)
    criterion = data["proposal"]["criteria"][0]
    criterion["condition"]["source_atom_ids"] = [context[0].id, context[1].id]
    criterion["exceptions"] = [
        {"text": "Same fixture exception", "source_atom_ids": [context[i].id]} for i in range(2)
    ]
    before = SemanticAnalysisV3.model_validate(data)
    changed = copy.deepcopy(data)
    changed["proposal"]["criteria"][0]["exceptions"].reverse()
    after = SemanticAnalysisV3.model_validate(changed)
    assert before.findings[0].source_atom_ids == after.findings[0].source_atom_ids
    assert before.findings[0].exceptions == after.findings[0].exceptions
    assert before.findings[0].sha256 != after.findings[0].sha256


@pytest.mark.parametrize(
    "change",
    [
        "unknown-component",
        "duplicate-component",
        "asset-component",
        "wrong-order",
        "unknown-target",
        "duplicate-target",
        "guard-collision",
        "duplicate-guard",
        "project-with-target",
        "criteria-without-target",
        "no-guard-scope",
    ],
)
def test_invalid_component_and_guard_bindings_are_rejected(project, change):
    analysis = fixture_analysis(project)
    data = analysis.model_dump()
    criterion, guard = data["proposal"]["criteria"][0], data["proposal"]["guards"][0]
    if change == "unknown-component":
        criterion["condition"]["source_atom_ids"] = ["unknown-atom"]
    elif change == "duplicate-component":
        criterion["condition"]["source_atom_ids"] *= 2
    elif change == "asset-component":
        asset = next(atom for atom in analysis.extraction.atoms if atom.kind == "asset-metadata")
        guard["effect"]["source_atom_ids"] = [asset.id]
    elif change == "wrong-order":
        data["proposal"]["criteria"].reverse()
    elif change == "unknown-target":
        guard["target_criterion_atom_ids"] = [compact_context(analysis.extraction)[0].id]
    elif change == "duplicate-target":
        guard["target_criterion_atom_ids"] *= 2
    elif change == "guard-collision":
        guard["id"] = "criterion-1"
    elif change == "duplicate-guard":
        data["proposal"]["guards"].append(copy.deepcopy(guard))
    elif change == "project-with-target":
        guard["target_scope"] = "project"
    elif change == "criteria-without-target":
        guard["target_criterion_atom_ids"] = []
    else:
        del guard["target_scope"]
    with pytest.raises(ValidationError):
        SemanticAnalysisV3.model_validate(data)


def test_project_guard_survives_without_artificial_criterion_target(project):
    data = fixture_analysis(project).model_dump()
    guard = data["proposal"]["guards"][0]
    guard.update(target_scope="project", target_criterion_atom_ids=[])
    analysis = SemanticAnalysisV3.model_validate(data)
    finding = analysis.findings[-1]
    assert finding.guard_target_scope == "project"
    assert finding.guard_target_atom_ids == []
    assert finding.source_atom_ids
    assert analysis.proposal.guards[0].effect.text == finding.outcome


def test_guard_target_changes_are_hashed_without_becoming_support_sources(project):
    data = fixture_analysis(project).model_dump()
    before = SemanticAnalysisV3.model_validate(data)
    data["proposal"]["guards"][0]["target_criterion_atom_ids"] = [
        data["proposal"]["criteria"][1]["source_atom_id"]
    ]
    after = SemanticAnalysisV3.model_validate(data)
    left, right = before.findings[-1], after.findings[-1]
    assert left.source_atom_ids == right.source_atom_ids
    assert left.component_bindings == right.component_bindings
    assert left.guard_target_atom_ids != right.guard_target_atom_ids
    assert left.sha256 != right.sha256
    assert before.snapshot_sha256 != after.snapshot_sha256


@pytest.mark.parametrize(
    "impact,expected", [("implementation-detail", "ready"), ("authorization", "blocked")]
)
def test_materiality_disposition_is_preserved_without_promoting_guard_authority(
    project, impact, expected
):
    data = fixture_analysis(project).model_dump()
    data["proposal"]["criteria"][0]["uncertainties"] = [
        {
            "text": "Synthetic pending question",
            "impact": impact,
            "rationale": "Fixture materiality",
        }
    ]
    analysis = SemanticAnalysisV3.model_validate(data)
    assert analysis.disposition == expected
    assert (
        not {"approval", "model_qualification", "compilation_eligibility"}
        & analysis.model_dump().keys()
    )


def test_mutated_children_cannot_change_component_or_guard_mapping_silently(project):
    analysis = fixture_analysis(project)
    analysis.proposal.guards[0].condition.source_atom_ids.append("unknown-atom")
    with pytest.raises(ValidationError):
        SemanticAnalysisV3.model_validate(analysis.model_dump())
    with pytest.raises(ValueError):
        _ = analysis.findings


@pytest.mark.parametrize("name,index", [("condition", 0), ("exception", None), ("outcome", 1)])
def test_component_binding_placement_contract_is_closed(name, index):
    with pytest.raises(ValidationError):
        ComponentBinding(name=name, index=index, source_atom_ids=["atom-1"])
