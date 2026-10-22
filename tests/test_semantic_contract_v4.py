"""Synthetic development contracts only; never migrate/reassess reserved outputs."""

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from test_case_diagnostics import synthetic

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.semantic_analysis import AnalysisIssue
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import SemanticPreflightReport, preflight_case
from ai_harness_compiler.offline_schema_registry import OFFLINE_MODELS


def development():
    original, old_analysis = synthetic()
    atom = next(a for a in old_analysis.extraction.atoms if a.pointer == "/conception")
    proposal = {
        "project_analysis": old_analysis.proposal.model_dump(),
        "requirements": [
            {
                "id": "intent-requirement",
                "content": {"text": atom.quote, "source_atom_ids": [atom.id]},
                "normative_force": "required",
                "note": "Synthetic",
            }
        ],
        "content_rejections": [],
    }
    analysis = SemanticAnalysisV4(extraction=old_analysis.extraction, proposal=proposal)
    case = AssessmentCaseV3(
        id="new-development-case",
        project=original.project,
        expected_behavior="ready",
        obligations=[
            dict(
                id="intent",
                source_pointer=atom.pointer,
                quote=atom.quote,
                disposition="requirement",
            )
        ],
    )
    return original, old_analysis, case, analysis


def test_requirement_at_conception_has_explicit_force_and_exact_components():
    _, _, case, analysis = development()
    req = analysis.proposal.requirements[0]
    assert req.content.text == case.project.conception
    assert req.normative_force == "required"
    assert req.applicability is None
    assert analysis.disposition == "ready"
    assert any(f.kind == "statement" for f in analysis.findings)  # Facts were NOT relabeled.
    assert next(f for f in analysis.findings if f.id == req.id).kind == "requirement"
    assert SemanticAnalysisV4.model_validate_json(analysis.model_dump_json()) == analysis
    assert preflight_case(case, "SemanticAnalysis/v4").status == "compatible"
    assert preflight_case(case, "SemanticAnalysis/v3").status == "incompatible"


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-force",
        "unknown-content",
        "unknown-applicability",
        "duplicate-anchor",
        "duplicate-id",
        "wrong-kind",
    ],
)
def test_bad_requirements_do_not_become_valid_findings(mutation):
    _, _, _, analysis = development()
    data = analysis.model_dump()
    req = data["proposal"]["requirements"][0]
    if mutation == "missing-force":
        req.pop("normative_force")
    elif mutation == "unknown-content":
        req["content"]["source_atom_ids"] = ["unknown"]
    elif mutation == "unknown-applicability":
        req["applicability"] = {"text": "Unknown trigger", "source_atom_ids": ["unknown"]}
    elif mutation == "duplicate-anchor":
        req["content"]["source_atom_ids"] *= 2
    elif mutation == "duplicate-id":
        req["id"] = "criterion-1"
    else:
        req["kind"] = "statement"
    with pytest.raises(ValueError):
        SemanticAnalysisV4.model_validate(data)


def test_applicability_and_force_are_preserved_and_change_identity():
    _, _, _, analysis = development()
    data = analysis.model_dump()
    req = data["proposal"]["requirements"][0]
    other = next(a for a in analysis.extraction.atoms if a.kind == "acceptance-criterion")
    req["applicability"] = {"text": "Synthetic applicability", "source_atom_ids": [other.id]}
    changed = SemanticAnalysisV4.model_validate(data)
    assert changed.proposal.requirements[0].content == analysis.proposal.requirements[0].content
    assert changed.proposal.requirements[0].applicability.source_atom_ids == [other.id]
    assert changed.snapshot_sha256 != analysis.snapshot_sha256
    data["proposal"]["requirements"][0]["normative_force"] = "prohibited"
    assert SemanticAnalysisV4.model_validate(data).snapshot_sha256 != changed.snapshot_sha256


def add_rejection(analysis):
    data = analysis.model_dump()
    source = data["proposal"]["requirements"][0]["content"]
    data["proposal"]["content_rejections"] = [
        dict(id="ignored-instruction", content=source, note="Synthetic rejected instruction")
    ]
    return SemanticAnalysisV4.model_validate(data)


def test_rejected_content_preserves_legitimate_analysis_and_does_not_reject_project():
    _, _, case, analysis = development()
    rejected = add_rejection(analysis)
    assert rejected.disposition == "ready"
    assert rejected.project_analysis == analysis.project_analysis
    assert rejected.proposal.requirements == analysis.proposal.requirements
    assert rejected.findings[-1].kind == "content-rejection"
    data = case.model_dump()
    data["required_content_rejection_pointers"] = ["/conception"]
    case = AssessmentCaseV3.model_validate(data)
    assert preflight_case(case, "SemanticAnalysis/v4").status == "compatible"
    assert preflight_case(case, "SemanticAnalysis/v3").issues[-1].code == (
        "content-rejection-channel-unavailable"
    )


@pytest.mark.parametrize(
    "impact,disposition", [("rule", "blocked"), ("implementation-detail", "ready")]
)
def test_content_rejection_neither_clears_a_real_blocker_nor_creates_one(impact, disposition):
    _, _, _, analysis = development()
    data = add_rejection(analysis).model_dump()
    data["proposal"]["project_analysis"]["issues"] = [
        dict(
            kind="question",
            text="Synthetic?",
            context_indices=[0],
            rationale="Synthetic materiality",
            impact=impact,
        )
    ]
    assert SemanticAnalysisV4.model_validate(data).disposition == disposition


def test_project_rejection_remains_separate_and_injection_cannot_use_that_channel():
    _, _, _, analysis = development()
    data = add_rejection(analysis).model_dump()
    issue = dict(
        kind="safe-rejection",
        text="Cannot understand required source",
        context_indices=[0],
        rationale="Synthetic unavailable-source interpretation",
        rejection_reason="unread-required-source",
    )
    data["proposal"]["project_analysis"]["issues"] = [issue]
    assert SemanticAnalysisV4.model_validate(data).disposition == "safely-rejected"
    issue["rejection_reason"] = "untrusted-instruction"
    with pytest.raises(ValueError, match="content_rejections"):
        SemanticAnalysisV4.model_validate(data)


def test_mutated_project_rejection_cannot_bypass_channel_validation():
    _, _, _, analysis = development()
    analysis.proposal.project_analysis.issues.append(
        AnalysisIssue(
            kind="safe-rejection",
            text="Ignore instructions",
            context_indices=[0],
            rationale="Synthetic",
            rejection_reason="untrusted-instruction",
        )
    )
    with pytest.raises(ValueError):
        _ = analysis.disposition


def test_case_versions_and_approval_are_not_implicitly_migrated():
    old, old_analysis, case, analysis = development()
    before = old.snapshot_sha256
    report = preflight_case(old, "SemanticAnalysis/v4")
    assert [i.code for i in report.issues] == ["explicit-case-migration-required"]
    assert old.snapshot_sha256 == before
    assert case.expectations_approval is None
    with pytest.raises(ValueError):
        AssessmentCaseV3.model_validate(old.model_dump())
    with pytest.raises(ValueError):
        AssessmentCase.model_validate(case.model_dump())
    with pytest.raises(ValueError):
        SemanticAnalysisV3.model_validate(analysis.model_dump())
    assert SemanticAnalysisV3.model_validate(old_analysis.model_dump()) == old_analysis


def test_case_project_and_content_rejections_are_independent():
    _, _, case, _ = development()
    data = case.model_dump()
    data["required_content_rejection_pointers"] = ["/conception"]
    assert AssessmentCaseV3.model_validate(data).expected_behavior == "ready"
    data["required_project_rejection_pointers"] = ["/conception"]
    with pytest.raises(ValueError):
        AssessmentCaseV3.model_validate(data)
    data["expected_behavior"] = "safely-rejected"
    assert AssessmentCaseV3.model_validate(data).required_content_rejection_pointers == [
        "/conception"
    ]


@pytest.mark.parametrize("mutation", ["quote", "duplicate-rejection", "unknown-rejection"])
def test_case_literal_expectations_are_still_strict(mutation):
    _, _, case, _ = development()
    data = case.model_dump()
    if mutation == "quote":
        data["obligations"][0]["quote"] = "Invented source"
    elif mutation == "duplicate-rejection":
        data["required_content_rejection_pointers"] = ["/conception"] * 2
    else:
        data["required_content_rejection_pointers"] = ["/not-in-input"]
    with pytest.raises(ValueError):
        AssessmentCaseV3.model_validate(data)


def test_asset_metadata_is_not_read_or_promoted_to_requirement_or_rejected_content():
    original, _, case, _ = development()
    data = original.project.model_dump()
    data["assets"] = [
        {"path": "does-not-exist/private-document.bin", "description": "Unread metadata"}
    ]
    project = ProjectInput.model_validate(data)
    extraction = extract_grounding(project)
    atom = next(a for a in extraction.atoms if a.kind == "acceptance-criterion")
    metadata = next(a for a in extraction.atoms if a.kind == "asset-metadata")
    payload = dict(
        extraction=extraction.model_dump(),
        proposal=dict(
            project_analysis=dict(
                criteria=[dict(source_atom_id=atom.id, kind="requirement", note="Synthetic")]
            ),
            requirements=[],
            content_rejections=[],
        ),
    )
    assert SemanticAnalysisV4.model_validate(payload).disposition == "ready"  # No file read.
    for channel in ("requirements", "content_rejections"):
        invalid = json.loads(json.dumps(payload))
        item = dict(
            id="invalid-asset",
            content=dict(text="Claimed asset content", source_atom_ids=[metadata.id]),
            note="Synthetic invalid claim",
        )
        if channel == "requirements":
            item["normative_force"] = "required"
        invalid["proposal"][channel] = [item]
        with pytest.raises(ValueError, match="never asset content"):
            SemanticAnalysisV4.model_validate(invalid)
    data = case.model_dump()
    data["project"] = project.model_dump()
    data["required_content_rejection_pointers"] = [metadata.pointer]
    with pytest.raises(ValueError, match="eligible original"):
        AssessmentCaseV3.model_validate(data)


@pytest.mark.parametrize("identity", ["criterion-1", "intent-requirement", "duplicate-rejection"])
def test_rejection_ids_cannot_shadow_another_channel(identity):
    _, _, _, analysis = development()
    data = add_rejection(analysis).model_dump()
    data["proposal"]["content_rejections"][0]["id"] = identity
    if identity == "duplicate-rejection":
        data["proposal"]["content_rejections"].append(
            dict(data["proposal"]["content_rejections"][0])
        )
    with pytest.raises(ValueError, match="identities"):
        SemanticAnalysisV4.model_validate(data)


def test_unknown_target_does_not_fall_back_to_an_existing_version():
    _, _, case, _ = development()
    with pytest.raises(ValueError, match="Unknown analysis version"):
        preflight_case(case, "SemanticAnalysis/v99")


@pytest.mark.parametrize("kind", ["statement", "domain"])
def test_factual_expectations_need_not_be_forced_into_requirements(kind):
    _, _, case, _ = development()
    data = case.model_dump()
    data["obligations"][0]["disposition"] = kind
    case = AssessmentCaseV3.model_validate(data)
    assert preflight_case(case, "SemanticAnalysis/v3").status == "compatible"
    assert preflight_case(case, "SemanticAnalysis/v4").status == "compatible"


@pytest.mark.parametrize(
    "mutation", ["status", "issues", "case-hash", "input-hash", "target", "authorization"]
)
def test_preflight_rejects_contradictory_reports(mutation):
    _, _, case, _ = development()
    data = preflight_case(case, "SemanticAnalysis/v3").model_dump()
    if mutation == "status":
        data["status"] = "compatible"
    elif mutation == "issues":
        data["issues"] = []
    elif mutation == "case-hash":
        data["case_sha256"] = "0" * 64
    elif mutation == "input-hash":
        data["input_sha256"] = "0" * 64
    elif mutation == "target":
        data["target_analysis_version"] = "SemanticAnalysis/v4"
    else:
        data["execution_authorized"] = True
    with pytest.raises(ValueError):
        SemanticPreflightReport.model_validate(data)


def test_v2_context_requirement_is_rejected_before_any_model():
    old, _, case, _ = development()
    data = old.model_dump()
    data["obligations"] = [o.model_dump() for o in case.obligations]
    old = AssessmentCase.model_validate(data)
    report = preflight_case(old, "SemanticAnalysis/v3")
    assert report.issues[0].code == "requirement-source-unrepresentable"
    assert not report.execution_authorized
    assert report.semantic_status == "not-established"
    assert report.compilation_eligibility == "not-authorized"


def test_new_schemas_validate_and_existing_cli_registry_stays_unchanged():
    from ai_harness_compiler.cli import MODELS

    _, _, case, analysis = development()
    values = {
        "semantic-analysis-proposal-v4": analysis.proposal,
        "semantic-analysis-v4": analysis,
        "semantic-assessment-case-v3": case,
        "semantic-preflight-report": preflight_case(case, "SemanticAnalysis/v4"),
    }
    assert not MODELS.keys() & OFFLINE_MODELS.keys()
    for name, value in values.items():
        model = OFFLINE_MODELS[name]
        Draft202012Validator(model.model_json_schema()).validate(value.model_dump())
        assert model.model_validate_json(value.model_dump_json()) == value


def script_command(case_path, output, target):
    script = str(Path(__file__).resolve().parents[1] / "scripts/preflight_semantic_case.py")
    # A provider import would fail even if the optional package is installed.
    wrapper = (
        "import sys,runpy;sys.modules['ai_harness_compiler.adapters.codex_cli']=None;"
        "sys.modules['openai']=None;sys.argv=sys.argv[1:];"
        "runpy.run_path(sys.argv[0],run_name='__main__')"
    )
    return [
        sys.executable,
        "-c",
        wrapper,
        script,
        "--case",
        str(case_path),
        "--target",
        target,
        "--output",
        str(output),
    ]


@pytest.mark.parametrize(
    "target,exitcode", [("SemanticAnalysis/v3", 2), ("SemanticAnalysis/v4", 0)]
)
def test_script_has_no_provider_and_never_overwrites(tmp_path, target, exitcode):
    _, _, case, _ = development()
    case_path = tmp_path / "case.json"
    output = tmp_path / "preflight.json"
    case_path.write_text(case.model_dump_json(), encoding="utf-8")
    result = subprocess.run(
        script_command(case_path, output, target), capture_output=True, text=True
    )
    assert result.returncode == exitcode, result.stderr
    saved = output.read_bytes()
    report = SemanticPreflightReport.model_validate_json(saved)
    assert report.execution_authorized is False
    assert case.project.conception not in result.stdout
    assert (
        subprocess.run(script_command(case_path, output, target), capture_output=True).returncode
        == 2
    )
    assert output.read_bytes() == saved


@pytest.mark.parametrize(
    "payload",
    [
        {"schema_version": "AssessmentCase/v99"},
        [],
        {"schema_version": "AssessmentCase/v3"},
        {"schema_version": []},
    ],
)
def test_unknown_or_invalid_case_cannot_produce_report(tmp_path, payload):
    p = tmp_path / "case.json"
    out = tmp_path / "out.json"
    p.write_text(json.dumps(payload), encoding="utf-8")
    assert (
        subprocess.run(
            script_command(p, out, "SemanticAnalysis/v4"), capture_output=True
        ).returncode
        == 2
    )
    assert not out.exists()
