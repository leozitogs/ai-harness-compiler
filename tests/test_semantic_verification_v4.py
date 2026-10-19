"""Synthetic component audits test contracts, not business support or human approval."""

import copy

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_verification import VerificationFinding
from ai_harness_compiler.models.semantic_verification_v3 import verification_v3_program_digest
from ai_harness_compiler.models.semantic_verification_v4 import (
    ComponentJudgment,
    SemanticVerifierReportV4,
    VerifierProposalV4,
    verification_v4_program_digest,
)


def fixture_analysis(project):
    extraction = extract_grounding(project)
    atoms = [atom for atom in extraction.atoms if atom.kind == "acceptance-criterion"]
    guard_source = next(atom for atom in extraction.atoms if atom.kind == "constraint")
    return SemanticAnalysisV3.model_validate(
        {
            "extraction": extraction.model_dump(),
            "proposal": {
                "criteria": [
                    {
                        "source_atom_id": atom.id,
                        "kind": "business-rule",
                        "condition": {"text": "Synthetic trigger", "source_atom_ids": [atom.id]},
                        "outcome": {"text": atom.quote, "source_atom_ids": [atom.id]},
                        "exceptions": [
                            {"text": "Synthetic exception", "source_atom_ids": [atom.id]}
                        ],
                        "note": "Contract fixture, not actual business assessment",
                    }
                    for atom in atoms
                ],
                "guards": [
                    {
                        "id": "operational-guard",
                        "condition": {
                            "text": "Synthetic guard applicability",
                            "source_atom_ids": [guard_source.id],
                        },
                        "effect": {
                            "text": "Synthetic operational obligation",
                            "source_atom_ids": [guard_source.id],
                        },
                        "target_scope": "criteria",
                        "target_criterion_atom_ids": [atoms[0].id],
                        "note": "Guard is not permission or implementation evidence",
                    }
                ],
            },
        }
    )


def advice(analysis):
    return {
        "analysis_sha256": analysis.snapshot_sha256,
        "findings": [
            {
                "finding_id": finding.id,
                "finding_sha256": finding.sha256,
                "source_atom_ids": finding.source_atom_ids,
                "support": "supports",
                "materiality": "appropriate" if finding.kind == "question" else "not-applicable",
                "note": "Synthetic advice, not actual support",
            }
            for finding in analysis.findings
        ],
        "component_judgments": [
            {
                "finding_id": finding.id,
                "component_name": binding.name,
                "component_index": binding.index,
                "source_atom_ids": binding.source_atom_ids,
                "support": "supports",
                "note": "Synthetic component advice only",
            }
            for finding in analysis.findings
            for binding in finding.component_bindings
        ],
        "omissions": [],
        "source_coverage": [
            {
                "atom_id": source.atom_id,
                "quote_sha256": source.quote_sha256,
                "disposition": "represented"
                if any(source.atom_id in finding.source_atom_ids for finding in analysis.findings)
                else "not-applicable",
                "finding_ids": [
                    finding.id
                    for finding in analysis.findings
                    if source.atom_id in finding.source_atom_ids
                ],
                "omission_ids": [],
                "note": "Synthetic ledger classification only",
            }
            for source in analysis.sources
        ],
    }


def report(analysis, proposal):
    return SemanticVerifierReportV4(
        analysis=analysis,
        proposal=VerifierProposalV4.model_validate(proposal),
        requested_model="synthetic-model",
        program_sha256=verification_v4_program_digest(),
    )


def test_component_complete_report_is_advisory_and_roundtrips(project):
    analysis = fixture_analysis(project)
    result = report(analysis, advice(analysis))
    assert result.authority == "model-advisory"
    assert result.semantic_status == result.model_qualification == "not-established"
    assert result.compilation_eligibility == "not-authorized"
    assert SemanticVerifierReportV4.model_validate_json(result.model_dump_json()) == result
    Draft202012Validator(result.model_json_schema()).validate(result.model_dump())
    guard = next(finding for finding in analysis.findings if finding.id == "operational-guard")
    assert not set(guard.source_atom_ids) & set(guard.guard_target_atom_ids)
    assert (
        len([item for item in result.proposal.component_judgments if item.finding_id == guard.id])
        == 2
    )


def test_component_source_union_above_32_is_preserved_without_relaxing_v2(project):
    project = project.model_copy(deep=True)
    project.branding.principles = [f"Synthetic principle {index}" for index in range(64)]
    original = fixture_analysis(project)
    atoms = [
        atom.id
        for atom in original.extraction.atoms
        if atom.pointer.startswith("/branding/principles/")
    ]
    data = original.model_dump()
    data["proposal"]["criteria"][0]["condition"]["source_atom_ids"] = atoms[:32]
    data["proposal"]["criteria"][0]["outcome"]["source_atom_ids"] = atoms[32:]
    analysis = SemanticAnalysisV3.model_validate(data)
    proposed = advice(analysis)
    assert len(proposed["findings"][0]["source_atom_ids"]) == 65
    result = report(analysis, proposed)
    assert result.proposal.findings[0].source_atom_ids == analysis.findings[0].source_atom_ids
    assert SemanticVerifierReportV4.model_validate_json(result.model_dump_json()) == result
    with pytest.raises(ValidationError):
        VerificationFinding.model_validate(proposed["findings"][0])


@pytest.mark.parametrize("support", ["contradicts", "insufficient-evidence"])
def test_aggregate_support_cannot_hide_an_unsupported_component(project, support):
    analysis = fixture_analysis(project)
    data = advice(analysis)
    data["component_judgments"][0]["support"] = support
    with pytest.raises(ValidationError, match="unsupported component"):
        report(analysis, data)
    data["findings"][0]["support"] = support
    assert report(analysis, data).semantic_status == "not-established"


@pytest.mark.parametrize(
    "change", ["missing", "duplicate", "foreign-finding", "wrong-placement", "wrong-source"]
)
def test_component_inventory_and_own_sources_are_exact(project, change):
    analysis = fixture_analysis(project)
    data = advice(analysis)
    if change == "missing":
        data["component_judgments"].pop()
    elif change == "duplicate":
        data["component_judgments"].append(copy.deepcopy(data["component_judgments"][0]))
    elif change == "foreign-finding":
        data["component_judgments"][0]["finding_id"] = "foreign-finding"
    elif change == "wrong-placement":
        next(item for item in data["component_judgments"] if item["component_name"] == "exception")[
            "component_index"
        ] = 1
    else:
        guard = next(
            item
            for item in data["component_judgments"]
            if item["finding_id"] == "operational-guard"
        )
        guard["source_atom_ids"] = analysis.findings[0].source_atom_ids
    with pytest.raises(ValidationError):
        report(analysis, data)


@pytest.mark.parametrize("index", [None, -1, True, 0.0, "0"])
def test_exception_judgment_requires_strict_nonnegative_index(index):
    with pytest.raises(ValidationError):
        ComponentJudgment(
            finding_id="fixture",
            component_name="exception",
            component_index=index,
            source_atom_ids=["atom-1"],
            support="supports",
            note="Synthetic fixture",
        )


def test_nonexception_component_cannot_claim_index_or_duplicate_atoms():
    data = {
        "finding_id": "fixture",
        "component_name": "condition",
        "component_index": 0,
        "source_atom_ids": ["atom-1"],
        "support": "supports",
        "note": "Synthetic fixture",
    }
    with pytest.raises(ValidationError):
        ComponentJudgment.model_validate(data)
    data.update(component_index=None, source_atom_ids=["atom-1", "atom-1"])
    with pytest.raises(ValidationError):
        ComponentJudgment.model_validate(data)


@pytest.mark.parametrize(
    "change", ["analysis", "finding", "source", "materiality", "missing", "duplicate"]
)
def test_finding_level_v2_guards_remain_required(project, change):
    analysis = fixture_analysis(project)
    data = advice(analysis)
    if change == "analysis":
        data["analysis_sha256"] = "0" * 64
    elif change == "finding":
        data["findings"][0]["finding_sha256"] = "0" * 64
    elif change == "source":
        data["findings"][0]["source_atom_ids"] = ["unknown-atom"]
    elif change == "materiality":
        data["findings"][0]["materiality"] = "appropriate"
    elif change == "missing":
        data["findings"].pop()
    else:
        data["findings"][-1] = copy.deepcopy(data["findings"][0])
    with pytest.raises(ValidationError):
        report(analysis, data)


def test_missing_obligation_preserves_partial_findings_and_bidirectional_links(project):
    analysis = fixture_analysis(project)
    data = advice(analysis)
    atom_id = analysis.findings[0].source_atom_ids[0]
    data["omissions"] = [
        {
            "id": "missing-question",
            "kind": "question",
            "text": "Synthetic authorization gap",
            "rationale": "Synthetic material gap",
            "source_atom_ids": [atom_id],
            "impact": "authorization",
        }
    ]
    row = next(item for item in data["source_coverage"] if item["atom_id"] == atom_id)
    row.update(disposition="missing", omission_ids=["missing-question"])
    value = report(analysis, data)
    assert value.proposal.source_coverage != []
    row["finding_ids"] = []
    with pytest.raises(ValidationError, match="preserve every existing finding"):
        report(analysis, data)


@pytest.mark.parametrize(
    "change", ["quote", "missing-source", "ignore", "unknown-omission", "orphan"]
)
def test_source_complete_v3_guards_remain_required(project, change):
    analysis = fixture_analysis(project)
    data = advice(analysis)
    row = next(item for item in data["source_coverage"] if item["disposition"] == "represented")
    if change == "quote":
        row["quote_sha256"] = "0" * 64
    elif change == "missing-source":
        data["source_coverage"].pop()
    elif change == "ignore":
        row.update(disposition="untrusted-instruction", finding_ids=[])
    elif change == "unknown-omission":
        row.update(disposition="missing", omission_ids=["unknown-omission"])
    else:
        data["omissions"] = [
            {
                "id": "missing-rule",
                "kind": "rule",
                "text": "Synthetic missing rule",
                "rationale": "Synthetic rationale",
                "source_atom_ids": [row["atom_id"]],
            }
        ]
    with pytest.raises(ValidationError):
        report(analysis, data)


@pytest.mark.parametrize("change", ["condition", "outcome", "exception", "target"])
def test_changed_analysis_components_or_guard_targets_invalidate_advice(project, change):
    analysis = fixture_analysis(project)
    value = report(analysis, advice(analysis)).model_dump()
    if change == "target":
        atom_ids = [item["source_atom_id"] for item in value["analysis"]["proposal"]["criteria"]]
        value["analysis"]["proposal"]["guards"][0]["target_criterion_atom_ids"] = [atom_ids[1]]
    elif change == "exception":
        value["analysis"]["proposal"]["criteria"][0]["exceptions"][0]["text"] = "Changed exception"
    else:
        value["analysis"]["proposal"]["criteria"][0][change]["text"] = "Changed component"
    with pytest.raises(ValidationError):
        SemanticVerifierReportV4.model_validate(value)


@pytest.mark.parametrize(
    "field,value",
    [
        ("authority", "human-approved"),
        ("semantic_status", "pass"),
        ("compilation_eligibility", "authorized"),
        ("model_qualification", "qualified"),
        ("program_sha256", "0" * 64),
    ],
)
def test_advisory_report_cannot_promote_authority_or_change_program(project, field, value):
    analysis = fixture_analysis(project)
    data = report(analysis, advice(analysis)).model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        SemanticVerifierReportV4.model_validate(data)


def test_previous_verifier_fingerprint_and_mutated_children_are_rejected(project):
    analysis = fixture_analysis(project)
    data = report(analysis, advice(analysis)).model_dump()
    data["program_sha256"] = verification_v3_program_digest()
    with pytest.raises(ValidationError, match="v4 logical program"):
        SemanticVerifierReportV4.model_validate(data)
    value = report(analysis, advice(analysis))
    value.proposal.component_judgments[0].__dict__["source_atom_ids"] = ["unknown-atom"]
    with pytest.raises(ValidationError):
        SemanticVerifierReportV4.model_validate(value.model_dump())
