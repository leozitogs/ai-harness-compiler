"""Independent synthetic reproductions; no reserved case or model response is read."""

import subprocess
import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from ai_harness_compiler.case_diagnostics import diagnose_case
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_assessment_v3 import assess_v3
from ai_harness_compiler.models.semantic_eval import CRITERIA, UnderstandingRubric


def synthetic():
    project = ProjectInput(
        id="synthetic-diagnostic",
        name="Synthetic diagnostic",
        conception="Maintain a synthetic archive for independent contract tests.",
        backlog=[
            {
                "id": "store-record",
                "title": "Store a test record",
                "description": "Store a record with a synthetic label.",
                "acceptance_criteria": ["Show the synthetic label."],
            }
        ],
        constraints={"technical": ["Use a synthetic storage adapter."], "max_build_cost_usd": 0.0},
    )
    extraction = extract_grounding(project)
    criterion = next(a for a in extraction.atoms if a.kind == "acceptance-criterion")
    context = compact_context(extraction)
    interpretations = [
        {"subject": subject, "pointer": pointer}
        for subject, pointer in [
            ("purpose", "/conception"),
            ("capability", "/backlog/0/description"),
            ("constraint", "/constraints/technical/0"),
        ]
    ]
    analysis = SemanticAnalysisV3.model_validate(
        {
            "extraction": extraction.model_dump(),
            "proposal": {
                "criteria": [
                    {"source_atom_id": criterion.id, "kind": "requirement", "note": "Synthetic"}
                ],
                "context_findings": [
                    {
                        "subject": row["subject"],
                        "text": next(a.quote for a in context if a.pointer == row["pointer"]),
                        "context_indices": [
                            i for i, a in enumerate(context) if a.pointer == row["pointer"]
                        ],
                        "note": "Synthetic literal preservation, not human support",
                    }
                    for row in interpretations
                ],
            },
        }
    )
    case = AssessmentCase(
        id="synthetic-case",
        project=project,
        expected_behavior="ready",
        obligations=[
            {
                "id": "criterion",
                "source_pointer": criterion.pointer,
                "quote": criterion.quote,
                "disposition": "requirement",
            }
        ],
    )
    return case, analysis


@pytest.mark.parametrize(
    "pointer", ["/conception", "/backlog/0/description", "/constraints/technical/0"]
)
def test_context_requirement_cannot_be_covered_even_when_literal_text_is_preserved(pointer):
    case, analysis = synthetic()
    atom = next(a for a in analysis.extraction.atoms if a.pointer == pointer)
    data = case.model_dump()
    data["obligations"] = [
        dict(id="context", source_pointer=pointer, quote=atom.quote, disposition="requirement")
    ]
    case = AssessmentCase.model_validate(data)
    before = (case.snapshot_sha256, analysis.snapshot_sha256)
    result = diagnose_case(case, analysis)
    coverage = result.coverage[0]
    assert coverage.requirement_source_unrepresentable_in_v3
    assert not coverage.matched_finding_ids
    assert coverage.same_pointer_candidates[0].kind == "statement"
    finding = next(
        f for f in analysis.findings if f.id == coverage.same_pointer_candidates[0].finding_id
    )
    assert finding.text == atom.quote  # Text preservation is NOT a structural requirement finding.
    assert (case.snapshot_sha256, analysis.snapshot_sha256) == before
    assert result.semantic_status == "not-established"


def test_criterion_requirement_is_representable_and_matches_without_semantic_approval():
    case, analysis = synthetic()
    result = diagnose_case(case, analysis)
    assert result.coverage[0].matched_finding_ids == ("criterion-1",)
    assert not result.coverage[0].requirement_source_unrepresentable_in_v3
    assert result.authority == "structural-diagnostic-only"
    with pytest.raises(FrozenInstanceError):
        result.case_id = "changed"


def test_source_present_under_another_kind_is_not_coverage_or_unrepresentability():
    case, analysis = synthetic()
    data = case.model_dump()
    data["obligations"][0]["disposition"] = "rule"
    case = AssessmentCase.model_validate(data)
    result = diagnose_case(case, analysis).coverage[0]
    assert not result.matched_finding_ids
    assert not result.requirement_source_unrepresentable_in_v3
    assert result.same_pointer_candidates[0].kind == "requirement"


def test_disposition_and_refusal_mismatches_coexist_even_when_old_check_masks_one():
    case, analysis = synthetic()
    data = case.model_dump()
    data.update(expected_behavior="safely-rejected", refusal_source_pointers=["/conception"])
    case = AssessmentCase.model_validate(data)
    result = diagnose_case(case, analysis)
    assert not result.disposition_matches
    assert result.actual_disposition == "ready"
    assert result.unmatched_refusal_pointers == ("/conception",)
    rubric = UnderstandingRubric(
        id="synthetic-rubric",
        version="v2",
        criteria=[{"id": c, "description": "Synthetic criterion"} for c in CRITERIA],
    )
    old = assess_v3(case, rubric, analysis)
    check = next(c for c in old.checks if c.criterion == "project-understanding")
    assert check.note == "Required sourced refusal absent from analysis"
    assert old.status == "fail"  # Historical semantics remain unchanged.


def test_unmatched_context_can_remain_a_real_omission():
    case, analysis = synthetic()
    atom = next(a for a in analysis.extraction.atoms if a.pointer == "/conception")
    data = case.model_dump()
    data["obligations"] = [
        dict(id="context", source_pointer=atom.pointer, quote=atom.quote, disposition="requirement")
    ]
    case = AssessmentCase.model_validate(data)
    data = analysis.model_dump()
    data["proposal"]["context_findings"] = []
    result = diagnose_case(case, SemanticAnalysisV3.model_validate(data)).coverage[0]
    assert result.requirement_source_unrepresentable_in_v3
    assert not result.same_pointer_candidates  # Incompatibility does not prove preservation.


def test_other_project_snapshot_is_rejected():
    case, analysis = synthetic()
    case.project.name = "Different synthetic project"
    with pytest.raises(ValueError, match="DIAGNOSTIC_INPUT_MISMATCH"):
        diagnose_case(case, analysis)


@pytest.mark.parametrize("impact,matched", [("implementation-detail", False), ("rule", True)])
def test_question_must_keep_material_impact(impact, matched):
    case, analysis = synthetic()
    context = compact_context(analysis.extraction)
    index = next(i for i, a in enumerate(context) if a.pointer == "/conception")
    data = case.model_dump()
    data.update(
        expected_behavior="blocked",
        obligations=[
            dict(
                id="question",
                source_pointer="/conception",
                quote=case.project.conception,
                disposition="required-question",
            )
        ],
    )
    case = AssessmentCase.model_validate(data)
    data = analysis.model_dump()
    data["proposal"]["issues"] = [
        dict(
            kind="question",
            text="Synthetic question?",
            context_indices=[index],
            rationale="Synthetic materiality",
            impact=impact,
        )
    ]
    result = diagnose_case(case, SemanticAnalysisV3.model_validate(data))
    assert bool(result.coverage[0].matched_finding_ids) == matched


def test_required_conflict_and_explicit_refusal_are_reported_independently():
    case, analysis = synthetic()
    context = compact_context(analysis.extraction)
    pointers = ["/conception", "/backlog/0/description"]
    indices = [i for i, a in enumerate(context) if a.pointer in pointers]
    data = case.model_dump()
    data.update(
        expected_behavior="blocked", requires_conflict=True, conflict_source_pointers=pointers
    )
    case = AssessmentCase.model_validate(data)
    assert diagnose_case(case, analysis).required_conflict_missing
    data = analysis.model_dump()
    data["proposal"]["issues"] = [
        dict(
            kind="conflict",
            text="Synthetic conflict",
            context_indices=indices,
            rationale="Synthetic sources",
        )
    ]
    analysis = SemanticAnalysisV3.model_validate(data)
    assert not diagnose_case(case, analysis).required_conflict_missing
    data = case.model_dump()
    data.update(expected_behavior="safely-rejected", refusal_source_pointers=["/conception"])
    case = AssessmentCase.model_validate(data)
    data = analysis.model_dump()
    data["proposal"]["issues"].append(
        dict(
            kind="safe-rejection",
            text="Synthetic refusal",
            context_indices=[next(i for i, a in enumerate(context) if a.pointer == "/conception")],
            rationale="Synthetic reason",
            rejection_reason="untrusted-instruction",
        )
    )
    result = diagnose_case(case, SemanticAnalysisV3.model_validate(data))
    assert not result.unmatched_refusal_pointers
    assert result.disposition_matches


def test_v3_cannot_move_a_criterion_requirement_to_a_context_source():
    _, analysis = synthetic()
    data = analysis.model_dump()
    data["proposal"]["criteria"][0]["source_atom_id"] = next(
        a.id for a in analysis.extraction.atoms if a.pointer == "/conception"
    )
    with pytest.raises(ValueError, match="criterion identity"):
        SemanticAnalysisV3.model_validate(data)


def test_offline_script_preserves_input_and_existing_output(tmp_path):
    case, analysis = synthetic()
    case_path = tmp_path / "case.json"
    analysis_path = tmp_path / "analysis.json"
    output = tmp_path / "diagnostic.json"
    case_path.write_text(case.model_dump_json(), encoding="utf-8")
    analysis_path.write_text(analysis.model_dump_json(), encoding="utf-8")
    command = [
        sys.executable,
        str(Path(__file__).resolve().parents[1] / "scripts/diagnose_semantic_case.py"),
        "--case",
        str(case_path),
        "--analysis",
        str(analysis_path),
        "--output",
        str(output),
    ]
    subprocess.run(command, check=True, capture_output=True)
    before = output.read_bytes()
    assert b'"structural-diagnostic-only"' in before
    assert subprocess.run(command, capture_output=True).returncode != 0
    assert output.read_bytes() == before
