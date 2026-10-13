"""Synthetic source-complete audits verify invariants, never model semantic success."""

import copy

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from test_semantic_assessment import fixtures

from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.semantic_analysis import SemanticAnalysis
from ai_harness_compiler.models.semantic_verification import (
    VERIFIER_PROMPT,
    verification_program_digest,
)
from ai_harness_compiler.models.semantic_verification_v3 import (
    MissingFinding,
    SemanticVerifierReportV3,
    VerifierProposalV3,
    verification_v3_program_digest,
)


def advice(analysis):
    return {
        "analysis_sha256": analysis.snapshot_sha256,
        "findings": [
            {
                "finding_id": finding.id,
                "finding_sha256": finding.sha256,
                "source_atom_ids": finding.source_atom_ids,
                "support": "insufficient-evidence",
                "materiality": "appropriate" if finding.kind == "question" else "not-applicable",
                "note": "Synthetic model advice only",
            }
            for finding in analysis.findings
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


def missing_question(analysis):
    data = advice(analysis)
    atom_id = analysis.findings[0].source_atom_ids[0]
    data["omissions"] = [
        {
            "id": "missing-question",
            "kind": "question",
            "text": "Which authorization rule applies?",
            "rationale": "Synthetic material authorization gap",
            "source_atom_ids": [atom_id],
            "impact": "authorization",
        }
    ]
    row = next(row for row in data["source_coverage"] if row["atom_id"] == atom_id)
    row["disposition"] = "missing"
    row["omission_ids"] = ["missing-question"]
    return data


def report(analysis, proposal):
    return SemanticVerifierReportV3(
        analysis=analysis,
        proposal=VerifierProposalV3.model_validate(proposal),
        requested_model="fixture-model",
        program_sha256=verification_v3_program_digest(),
    )


def test_source_complete_report_stays_model_advice_without_omissions(project):
    _, _, analysis = fixtures(project)
    result = report(analysis, advice(analysis))
    assert {row.atom_id for row in result.proposal.source_coverage} == {
        source.atom_id for source in analysis.sources
    }
    assert result.proposal.omissions == []
    assert result.authority == "model-advisory"
    assert result.semantic_status == result.model_qualification == "not-established"
    assert result.compilation_eligibility == "not-authorized"
    assert SemanticVerifierReportV3.model_validate_json(result.model_dump_json()) == result
    Draft202012Validator(result.model_json_schema()).validate(result.model_dump())


def test_missing_material_question_preserves_known_findings_on_same_atom(project):
    _, _, analysis = fixtures(project)
    data = missing_question(analysis)
    result = report(analysis, data)
    row = next(row for row in result.proposal.source_coverage if row.disposition == "missing")
    assert row.finding_ids == [analysis.findings[0].id]
    assert row.omission_ids == ["missing-question"]
    assert result.proposal.omissions[0].impact == "authorization"
    assert result.compilation_eligibility == "not-authorized"


@pytest.mark.parametrize(
    "change",
    [
        "missing-source",
        "unknown-source",
        "duplicate-source",
        "quote-hash",
        "unknown-finding",
        "wrong-finding-source",
        "unknown-omission",
        "orphan-omission",
        "wrong-omission-source",
        "duplicate-omission",
        "finding-collision",
    ],
)
def test_source_ledger_and_omission_bindings_reject_contradictions(project, change):
    _, _, analysis = fixtures(project)
    data = missing_question(analysis)
    missing = next(row for row in data["source_coverage"] if row["disposition"] == "missing")
    if change == "missing-source":
        data["source_coverage"].pop()
    elif change == "unknown-source":
        data["source_coverage"][0]["atom_id"] = "unknown-atom"
    elif change == "duplicate-source":
        data["source_coverage"].append(copy.deepcopy(data["source_coverage"][0]))
    elif change == "quote-hash":
        data["source_coverage"][0]["quote_sha256"] = "0" * 64
    elif change == "unknown-finding":
        missing["finding_ids"] = ["unknown-finding"]
    elif change == "wrong-finding-source":
        missing["finding_ids"] = [analysis.findings[1].id]
    elif change == "unknown-omission":
        missing["omission_ids"] = ["unknown-omission"]
    elif change == "orphan-omission":
        missing.update(disposition="represented", omission_ids=[])
    elif change == "wrong-omission-source":
        data["omissions"][0]["source_atom_ids"] = ["unknown-atom"]
    elif change == "duplicate-omission":
        data["omissions"].append(copy.deepcopy(data["omissions"][0]))
    else:
        data["omissions"][0]["id"] = analysis.findings[0].id
        missing["omission_ids"] = [analysis.findings[0].id]
    with pytest.raises(ValidationError):
        report(analysis, data)


@pytest.mark.parametrize(
    "change",
    [
        "analysis-hash",
        "finding-hash",
        "finding-atom",
        "missing-finding",
        "duplicate-finding",
        "materiality",
    ],
)
def test_v2_finding_invariants_remain_required(project, change):
    _, _, analysis = fixtures(project)
    data = advice(analysis)
    if change == "analysis-hash":
        data["analysis_sha256"] = "0" * 64
    elif change == "finding-hash":
        data["findings"][0]["finding_sha256"] = "0" * 64
    elif change == "finding-atom":
        data["findings"][0]["source_atom_ids"] = ["unknown-atom"]
    elif change == "missing-finding":
        data["findings"].pop()
    elif change == "duplicate-finding":
        data["findings"][1] = copy.deepcopy(data["findings"][0])
    else:
        data["findings"][0]["materiality"] = "appropriate"
    with pytest.raises(ValidationError):
        report(analysis, data)


@pytest.mark.parametrize(
    "change",
    [
        "nonmaterial-question",
        "question-without-impact",
        "rule-with-impact",
        "conflict-one-source",
        "duplicate-atoms",
    ],
)
def test_missing_findings_have_material_typed_observable_bindings(change):
    data = {
        "id": "missing",
        "kind": "question",
        "text": "Synthetic gap",
        "rationale": "Fixture reason",
        "source_atom_ids": ["atom-1"],
        "impact": "authorization",
    }
    if change == "nonmaterial-question":
        data["impact"] = "implementation-detail"
    elif change == "question-without-impact":
        data["impact"] = None
    elif change == "rule-with-impact":
        data["kind"] = "rule"
    elif change == "conflict-one-source":
        data.update(kind="conflict", impact=None)
    else:
        data["source_atom_ids"] = ["atom-1", "atom-1"]
    with pytest.raises(ValidationError):
        MissingFinding.model_validate(data)


def test_missing_conflict_binds_both_source_ledger_rows(project):
    _, _, analysis = fixtures(project)
    data = advice(analysis)
    ids = [source.atom_id for source in analysis.sources[:2]]
    data["omissions"] = [
        {
            "id": "missing-conflict",
            "kind": "conflict",
            "text": "Synthetic conflict",
            "rationale": "Two fixture sources disagree",
            "source_atom_ids": ids,
        }
    ]
    for row in data["source_coverage"]:
        if row["atom_id"] in ids:
            row.update(disposition="missing", omission_ids=["missing-conflict"])
    report(analysis, data)
    data["source_coverage"][1].update(disposition="not-applicable", omission_ids=[], finding_ids=[])
    with pytest.raises(ValidationError, match="matching missing coverage"):
        report(analysis, data)


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
def test_v3_report_never_promotes_authority_or_accepts_stale_program(project, field, value):
    _, _, analysis = fixtures(project)
    data = report(analysis, advice(analysis)).model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        SemanticVerifierReportV3.model_validate(data)


def test_v2_fingerprint_cannot_substitute_for_v3_program(project):
    _, _, analysis = fixtures(project)
    data = report(analysis, advice(analysis)).model_dump()
    data["program_sha256"] = verification_program_digest(VERIFIER_PROMPT)
    with pytest.raises(ValidationError, match="v3 logical program"):
        SemanticVerifierReportV3.model_validate(data)


def test_mutated_child_coverage_is_revalidated(project):
    _, _, analysis = fixtures(project)
    value = report(analysis, advice(analysis))
    value.proposal.source_coverage[0].__dict__["quote_sha256"] = "0" * 64
    with pytest.raises(ValidationError):
        SemanticVerifierReportV3.model_validate(value.model_dump())


@pytest.mark.parametrize("disposition", ["represented", "missing"])
def test_ledger_cannot_erase_partial_findings_that_share_a_source(project, disposition):
    _, _, original = fixtures(project)
    atom_id = original.findings[0].source_atom_ids[0]
    index = next(
        i for i, atom in enumerate(compact_context(original.extraction)) if atom.id == atom_id
    )
    value = original.model_dump()
    value["proposal"]["context_findings"] = [
        {
            "subject": "purpose",
            "text": "Another fixture interpretation of the same source",
            "note": "Synthetic interpretation, not verified support",
            "context_indices": [index],
        }
    ]
    analysis = SemanticAnalysis.model_validate(value)
    data = missing_question(analysis) if disposition == "missing" else advice(analysis)
    row = next(row for row in data["source_coverage"] if row["atom_id"] == atom_id)
    assert len(row["finding_ids"]) == 2
    report(analysis, data)
    row["finding_ids"].pop()
    with pytest.raises(ValidationError, match="preserve every existing finding citation"):
        report(analysis, data)


@pytest.mark.parametrize("disposition", ["not-applicable", "untrusted-instruction"])
def test_ledger_cannot_silently_ignore_a_source_cited_by_an_existing_finding(project, disposition):
    _, _, analysis = fixtures(project)
    data = advice(analysis)
    atom_id = analysis.findings[0].source_atom_ids[0]
    row = next(row for row in data["source_coverage"] if row["atom_id"] == atom_id)
    row.update(disposition=disposition, finding_ids=[])
    with pytest.raises(ValidationError, match="preserve every existing finding citation"):
        report(analysis, data)


def test_incorrect_finding_stays_in_ledger_with_explicit_contradiction(project):
    _, _, analysis = fixtures(project)
    data = advice(analysis)
    data["findings"][0]["support"] = "contradicts"
    data["findings"][0]["note"] = "Synthetic evidence rejects this interpretation"
    result = report(analysis, data)
    atom_id = analysis.findings[0].source_atom_ids[0]
    row = next(row for row in result.proposal.source_coverage if row.atom_id == atom_id)
    assert row.disposition == "represented"
    assert row.finding_ids == [analysis.findings[0].id]
    assert result.proposal.findings[0].support == "contradicts"
    assert result.semantic_status == "not-established"
    assert result.compilation_eligibility == "not-authorized"
