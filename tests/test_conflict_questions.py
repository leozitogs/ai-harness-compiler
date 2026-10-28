"""Structural omission signals are neither semantic approval nor historical regrading."""

import json

import pytest
from jsonschema import Draft202012Validator
from test_semantic_flow_v4 import FakeGenerator, fixtures

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.conflict_questions import (
    ConflictQuestionDiagnosticV1,
    diagnose_conflict_questions,
)
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.semantic_generation_programs import (
    analyze_program,
    program_digest,
    program_prompt,
)


def analysis_with_conflict(question=None):
    case, _, _ = fixtures()
    project = case.project.model_copy(deep=True)
    project.conception = "Every release requires signed authorization."
    project.branding.principles = ["Releases do not require signed authorization."]
    extraction = extract_grounding(project)
    context = compact_context(extraction)
    indices = [
        i for i, a in enumerate(context) if a.pointer in {"/conception", "/branding/principles/0"}
    ]
    assert len(indices) == 2
    issues = [
        dict(
            kind="conflict",
            text="Authorization is required and waived for the same release.",
            context_indices=indices,
            rationale="Incompatible declarations.",
        )
    ]
    if question:
        impact, sides = question
        issues.append(
            dict(
                kind="question",
                text="Which authorization rule takes precedence?",
                context_indices=indices[:sides],
                impact=impact,
                rationale="Human decision required.",
            )
        )
    criteria = [
        dict(source_atom_id=a.id, kind="requirement", note="Synthetic independent criterion.")
        for a in extraction.atoms
        if a.kind == "acceptance-criterion"
    ]
    return SemanticAnalysisV4.model_validate(
        dict(
            extraction=extraction,
            proposal=dict(project_analysis=dict(criteria=criteria, issues=issues)),
        )
    )


@pytest.mark.parametrize(
    "question,status",
    [
        (None, "missing-question"),
        (("precedence", 1), "missing-question"),
        (("implementation-detail", 2), "missing-question"),
        (("rule", 2), "missing-question"),
        (("precedence", 2), "questions-present"),
    ],
)
def test_conflict_requires_a_distinct_precedence_question_citing_every_side(question, status):
    analysis = analysis_with_conflict(question)
    original = analysis.model_dump_json()
    report = diagnose_conflict_questions(analysis)
    assert analysis.disposition == "blocked" and report.status == status
    assert len(report.bindings) == 1 and report.analysis_sha256 == analysis.snapshot_sha256
    assert report.semantic_judgment == "not-established" and analysis.model_dump_json() == original
    Draft202012Validator(ConflictQuestionDiagnosticV1.model_json_schema()).validate(
        report.model_dump(mode="json")
    )
    assert ConflictQuestionDiagnosticV1.model_validate_json(report.model_dump_json()) == report


@pytest.mark.parametrize(
    "field,value",
    [("status", "questions-present"), ("analysis_sha256", "0" * 64), ("bindings", [])],
)
def test_diagnostic_cannot_erase_a_missing_question_or_change_snapshot(field, value):
    data = diagnose_conflict_questions(analysis_with_conflict()).model_dump()
    with pytest.raises(ValueError):
        ConflictQuestionDiagnosticV1.model_validate(data | {field: value})


def test_clear_project_does_not_gain_a_conflict_question_or_blocker():
    _, _, analysis = fixtures()
    report = diagnose_conflict_questions(analysis)
    assert report.status == "no-conflicts" and report.bindings == []
    assert analysis.disposition == "ready"


def test_v42_is_explicit_and_preserves_legacy_prompts_sources_and_raw_model_omissions():
    analysis = analysis_with_conflict()
    extraction = analysis.extraction
    legacy = program_digest(extraction, "semantic-composition/v4.1")
    candidate = program_digest(extraction, "semantic-composition/v4.2")
    prompt = program_prompt(extraction, candidate)
    assert candidate != legacy and "ACTIONABLE CONFLICT UNCERTAINTY" in prompt
    assert (
        prompt.split("\nINPUT DATA:\n")[1]
        == program_prompt(extraction, legacy).split("\nINPUT DATA:\n")[1]
    )
    generator = FakeGenerator([analysis.proposal.model_dump()])
    result = analyze_program(extraction, generator, candidate)
    assert result == analysis and diagnose_conflict_questions(result).status == "missing-question"
    assert len(generator.calls) == 1


def test_private_offline_inspection_does_not_overwrite_input_or_previous_result(tmp_path, capsys):
    from scripts.inspect_semantic_diagnostics import main

    analysis = analysis_with_conflict()
    (tmp_path / ".factory").mkdir()
    original = analysis.model_dump_json()
    source = tmp_path / ".factory/analysis.json"
    source.write_text(original, encoding="utf-8")
    args = [
        "--repository",
        str(tmp_path),
        "--analysis",
        ".factory/analysis.json",
        "--output",
        ".factory/diagnostic.json",
    ]
    main(args)
    assert (
        json.loads((tmp_path / ".factory/diagnostic.json").read_bytes())["status"]
        == "missing-question"
    )
    assert "No model calls" in capsys.readouterr().out
    assert source.read_text(encoding="utf-8") == original
    with pytest.raises(FileExistsError):
        main(args)
    with pytest.raises(ValueError):
        main(args[:-1] + ["../escape.json"])
    with pytest.raises(ValueError):
        main(args[:-1] + [".factory/../escape.json"])
    assert not (tmp_path / "escape.json").exists()
