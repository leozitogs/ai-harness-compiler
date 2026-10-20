"""Injected proposals verify routing, never efficacy or new human acceptance."""

import hashlib
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from test_semantic_verification import FakeGenerator

from ai_harness_compiler.models.compact_analysis import compact_context
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_assessment_v3 import SemanticHumanReviewV3, assess_v3
from ai_harness_compiler.models.semantic_eval import UnderstandingRubric
from ai_harness_compiler.semantic_composition import (
    CANDIDATE_COMPOSITION_PROMPT,
    MULTISOURCE_COMPOSITION_PROGRAM_VERSION,
    analyze_composition,
    composition_program_digest,
    composition_response_schema,
)

ROOT = Path(__file__).resolve().parents[1]
LEGACY_ANALYSIS = (
    ROOT / "docs/evidence/sprint-2-5-final-20261019/baseline-v3/dev-branding-conflict/analysis.json"
)


def proposals():
    original = SemanticAnalysisV3.model_validate_json(LEGACY_ANALYSIS.read_bytes())
    data = original.proposal.model_dump()
    question = data["criteria"][0]["uncertainties"].pop()
    context = compact_context(original.extraction)
    pointers = {
        "/branding/principles/0",
        "/backlog/0/acceptance_criteria/0",
    }
    data["issues"].append(
        {
            "kind": "question",
            "text": question["text"],
            "rationale": question["rationale"],
            "impact": question["impact"],
            "rejection_reason": None,
            "context_indices": [i for i, atom in enumerate(context) if atom.pointer in pointers],
        }
    )
    return original, data


def test_previous_program_fingerprints_remain_identical():
    preparation = json.loads(
        (
            ROOT / "docs/evidence/sprint-2-6-human-judgments-20261020/candidate-preparation.json"
        ).read_text(encoding="utf-8")
    )
    packet = json.loads(
        (ROOT / "docs/evidence/sprint-2-6-kickoff-review-20261019/packet.json").read_text(
            encoding="utf-8"
        )
    )
    for row in preparation["cases"]:
        source = next(c for c in packet["cases"] if c["case"] == row["case"])["sources"][1]
        analysis = SemanticAnalysisV3.model_validate_json((ROOT / source["path"]).read_bytes())
        assert composition_program_digest(analysis.extraction) == row["baseline_program_sha256"]
        assert (
            composition_program_digest(analysis.extraction, "semantic-composition/v3.2")
            == row["candidate_program_sha256"]
        )
    assert hashlib.sha256(CANDIDATE_COMPOSITION_PROMPT.encode()).hexdigest() == (
        "3760b2451898b35c9aadfd3eaca652eead8f97895fe5606871e72d1af4742aac"
    )


def test_v33_rejects_legacy_local_secondary_question_without_rewriting():
    original, _ = proposals()
    generator = FakeGenerator(original.proposal.model_dump())
    with pytest.raises(ValueError, match="COMPOSITION_QUESTION_ROUTE"):
        analyze_composition(
            original.extraction, generator, program_version=MULTISOURCE_COMPOSITION_PROGRAM_VERSION
        )
    assert len(generator.calls) == 1
    assert next(f for f in original.findings if f.id == "uncertainty-1-1").source_atom_ids == [
        "atom-7"
    ]


def test_issue_route_preserves_both_sources_and_invalidates_old_review():
    original, data = proposals()
    generator = FakeGenerator(data)
    result = analyze_composition(
        original.extraction, generator, program_version=MULTISOURCE_COMPOSITION_PROGRAM_VERSION
    )
    question = next(f for f in result.findings if f.id == "issue-2")
    assert question.kind == "question"
    assert question.source_atom_ids == ["atom-3", "atom-7"]
    assert result.disposition == original.disposition == "blocked"
    assert result.snapshot_sha256 != original.snapshot_sha256
    assert not any(f.id == "uncertainty-1-1" for f in result.findings)
    packet = json.loads(generator.calls[0][0].split("\nINPUT DATA:\n", 1)[1])
    assert "expected_behavior" not in packet
    assert "review" not in packet
    case = AssessmentCase.model_validate_json(
        (ROOT / "evals/understanding/v2/development-draft/dev-branding-conflict.json").read_bytes()
    )
    rubric = UnderstandingRubric.model_validate_json(
        (ROOT / "evals/understanding/v2/rubric.json").read_bytes()
    )
    review = SemanticHumanReviewV3.model_validate_json(
        (
            ROOT
            / "docs/evidence/sprint-2-6-development-assessment-20261020"
            / "dev-branding-conflict-review.json"
        ).read_bytes()
    )
    with pytest.raises(ValueError, match="another case, rubric or analysis"):
        assess_v3(case, rubric, result, review)
    assert assess_v3(case, rubric, result).status == "not-run"


@pytest.mark.parametrize("bad_indices", [[-1], [999]])
def test_v33_schema_rejects_invalid_issue_sources(bad_indices):
    original, data = proposals()
    schema = composition_response_schema(
        original.extraction, program_version=MULTISOURCE_COMPOSITION_PROGRAM_VERSION
    )
    validator = Draft202012Validator(schema)
    validator.validate(data)
    data["issues"][-1]["context_indices"] = bad_indices
    assert list(validator.iter_errors(data))


def test_v33_host_rejects_duplicate_issue_sources():
    original, data = proposals()
    data["issues"][-1]["context_indices"] = [0, 0]
    with pytest.raises(ValueError, match="Context positions must resolve uniquely"):
        analyze_composition(
            original.extraction,
            FakeGenerator(data),
            program_version=MULTISOURCE_COMPOSITION_PROGRAM_VERSION,
        )


def test_v33_schema_forbids_local_secondary_questions():
    original, _ = proposals()
    schema = composition_response_schema(
        original.extraction, program_version=MULTISOURCE_COMPOSITION_PROGRAM_VERSION
    )
    assert list(Draft202012Validator(schema).iter_errors(original.proposal.model_dump()))
    assert composition_program_digest(
        original.extraction, MULTISOURCE_COMPOSITION_PROGRAM_VERSION
    ) != composition_program_digest(original.extraction, "semantic-composition/v3.2")
