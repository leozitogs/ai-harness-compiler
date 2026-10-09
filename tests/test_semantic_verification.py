"""Model boundaries and atom invariants with fakes; never semantic performance claims."""

import copy
import json

import pytest
from pydantic import ValidationError
from test_semantic_assessment import fixtures

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.semantic_analysis import SemanticAnalysis
from ai_harness_compiler.models.semantic_verification import SemanticVerifierReport
from ai_harness_compiler.semantic_verification import analyze, verify


class FakeGenerator:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def generate_json(self, prompt, schema):
        self.calls.append((prompt, schema))
        return json.dumps(self.result)


def advice(analysis):
    return {
        "analysis_sha256": analysis.snapshot_sha256,
        "findings": [
            {
                "finding_id": f.id,
                "finding_sha256": f.sha256,
                "source_atom_ids": f.source_atom_ids,
                "support": "insufficient-evidence",
                "materiality": "appropriate" if f.kind == "question" else "not-applicable",
                "note": "Synthetic advisory only",
            }
            for f in analysis.findings
        ],
    }


def test_generator_returns_bound_v2_without_legacy_projection(project):
    _, _, original = fixtures(project)
    generator = FakeGenerator(original.proposal.model_dump())
    result = analyze(original.extraction, generator)
    assert result == original
    assert "criterion_atom_ids" in generator.calls[0][0]
    assert generator.calls[0][1]["properties"]["criteria"]["minItems"] == len(
        result.proposal.criteria
    )


def test_independent_verifier_remains_advisory(project):
    _, _, analysis = fixtures(project)
    generator = FakeGenerator(advice(analysis))
    result = verify(analysis, generator, "fixture-model")
    assert result.authority == "model-advisory"
    assert result.semantic_status == "not-established"
    assert result.compilation_eligibility == "not-authorized"
    assert "expectations_approval" not in generator.calls[0][0]


@pytest.mark.parametrize(
    "change", ["hash", "source", "missing", "duplicate", "human", "materiality"]
)
def test_invalid_verifier_advice_rejected(project, change):
    _, _, analysis = fixtures(project)
    data = advice(analysis)
    if change == "hash":
        data["findings"][0]["finding_sha256"] = "0" * 64
    elif change == "source":
        data["findings"][0]["source_atom_ids"] = ["atom-999"]
    elif change == "missing":
        data["findings"].pop()
    elif change == "duplicate":
        data["findings"][-1] = copy.deepcopy(data["findings"][0])
    elif change == "human":
        data["authority"] = "human-declared"
    else:
        data["findings"][0]["materiality"] = "appropriate"
    with pytest.raises(ValidationError):
        verify(analysis, FakeGenerator(data), "fixture-model")


def test_review_stale_on_rule_exception_change(project):
    _, _, analysis = fixtures(project)
    report = verify(analysis, FakeGenerator(advice(analysis)), "fixture-model")
    data = report.model_dump()
    data["analysis"]["proposal"]["criteria"][0]["exceptions"] = ["New exception"]
    with pytest.raises(ValidationError, match="snapshot"):
        SemanticVerifierReport.model_validate(data)


def test_verifier_logical_program_fingerprint_tamper_rejected(project):
    _, _, analysis = fixtures(project)
    report = verify(analysis, FakeGenerator(advice(analysis)), "fixture-model")
    data = report.model_dump()
    data["program_sha256"] = "0" * 64
    with pytest.raises(ValidationError, match="program fingerprint"):
        SemanticVerifierReport.model_validate(data)


@pytest.mark.parametrize("index", [True, 0.0, "0", -1, 9999])
def test_indices_strict_and_bounded(project, index):
    _, _, analysis = fixtures(project)
    data = analysis.model_dump()
    data["proposal"]["context_findings"] = [
        {"subject": "purpose", "text": "Fixture", "note": "Fixture", "context_indices": [index]}
    ]
    with pytest.raises(ValidationError):
        SemanticAnalysis.model_validate(data)


def test_exact_atoms_and_classification_change_finding_hash(project):
    _, _, analysis = fixtures(project)
    data = analysis.model_dump()
    data["proposal"]["context_findings"] = [
        {"subject": "audience", "text": "Fixture", "note": "Fixture", "context_indices": [0]}
    ]
    first = SemanticAnalysis.model_validate(data)
    data["proposal"]["context_findings"][0]["subject"] = "constraint"
    second = SemanticAnalysis.model_validate(data)
    assert first.findings[-1].sha256 != second.findings[-1].sha256
    data["proposal"]["context_findings"][0]["context_indices"] = [1]
    third = SemanticAnalysis.model_validate(data)
    assert third.findings[-1].sha256 != second.findings[-1].sha256


def test_two_conflicting_atoms_in_same_parent_are_preserved(project):
    project = project.model_copy(deep=True)
    project.branding.principles = ["Approval mandatory", "Approval prohibited"]
    _, _, analysis = fixtures(project)
    indices = [
        i
        for i, a in enumerate(compact_context(analysis.extraction))
        if a.pointer.startswith("/branding/principles/")
    ]
    data = analysis.model_dump()
    data["proposal"]["issues"] = [
        {
            "kind": "conflict",
            "text": "Approval conflict",
            "rationale": "Opposite mandates",
            "context_indices": indices,
        }
    ]
    result = SemanticAnalysis.model_validate(data)
    assert result.disposition == "blocked"
    ids = result.findings[-1].source_atom_ids
    sources = [s for s in result.sources if s.atom_id in ids]
    assert len(sources) == 2 and sources[0].source_ref == sources[1].source_ref


def test_criterion_reordering_rejected(project):
    _, _, analysis = fixtures(project)
    data = analysis.model_dump()
    data["proposal"]["criteria"].reverse()
    with pytest.raises(ValidationError, match="identity/order"):
        SemanticAnalysis.model_validate(data)


def test_rejection_reason_changes_finding_hash(project):
    _, _, analysis = fixtures(project, behavior="safely-rejected")
    data = analysis.model_dump()
    data["proposal"]["issues"][0]["rejection_reason"] = "unread-required-source"
    changed = SemanticAnalysis.model_validate(data)
    assert changed.findings[-1].sha256 != analysis.findings[-1].sha256


def test_cli_refuses_existing_output_before_call(project, tmp_path, monkeypatch):
    output = tmp_path / "existing.json"
    output.write_text("keep", encoding="utf-8")
    assert main(["analyze-project-v2", "does-not-exist", "--output", str(output)]) == 1
    assert output.read_text() == "keep"


def test_offline_cli_pending_assessment(project, tmp_path):
    case, rubric, analysis = fixtures(project, approved=False)
    paths = {}
    for key, obj in {"case": case, "rubric": rubric, "analysis": analysis}.items():
        paths[key] = tmp_path / f"{key}.json"
        paths[key].write_text(obj.model_dump_json(), encoding="utf-8")
    output = tmp_path / "assessment.json"
    assert (
        main(
            [
                "assess-analysis-v2",
                str(paths["analysis"]),
                "--case",
                str(paths["case"]),
                "--rubric",
                str(paths["rubric"]),
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert json.loads(output.read_text())["status"] == "not-run"
