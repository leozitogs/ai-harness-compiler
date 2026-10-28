"""Candidate preparation preserves approved data and cannot inherit execution authority."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.semantic_campaign import SemanticCampaignRequestV1
from ai_harness_compiler.semantic_generation_programs import program_prompt, resolve_program
from ai_harness_compiler.semantic_generation_v4 import (
    audit_v5_program_digest,
    generation_prompt_v4,
    generation_schema_v4,
)

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evals/understanding/v4/development-candidate-v41"


def test_candidate_has_new_identity_without_changing_reviewed_inputs_or_audit():
    new = SemanticCampaignRequestV1.model_validate_json((BASE / "request.json").read_bytes())
    old = SemanticCampaignRequestV1.model_validate_json(
        (ROOT / "evals/understanding/v4/development-campaign/request.json").read_bytes()
    )
    assert new.sha256 == "84bf9677d4e5fd3468bc5b19e41461b9790656ccaa07d0bc2b99957a22114bbc"
    assert new.sha256 != old.sha256 and new.campaign_id != old.campaign_id
    assert new.corpus_sha256 == old.corpus_sha256
    assert len(new.flows) == len(old.flows) == 8
    for candidate, baseline in zip(new.flows, old.flows, strict=True):
        assert candidate.run_id != baseline.run_id
        assert candidate.case == baseline.case and candidate.rubric == baseline.rubric
        assert candidate.requested_model == baseline.requested_model == "gpt-6.1-sol"
        assert (
            candidate.audit_program_sha256
            == baseline.audit_program_sha256
            == audit_v5_program_digest()
        )
        extraction = extract_grounding(candidate.case.project)
        assert (
            resolve_program(extraction, candidate.generation_program_sha256)
            == "semantic-composition/v4.1"
        )
        assert (
            resolve_program(extraction, baseline.generation_program_sha256)
            == "semantic-composition/v4.0"
        )
        assert candidate.generation_program_sha256 != baseline.generation_program_sha256
        assert (
            program_prompt(extraction, candidate.generation_program_sha256).split(
                "\nINPUT DATA:\n"
            )[1]
            == generation_prompt_v4(extraction).split("\nINPUT DATA:\n")[1]
        )
        assert generation_schema_v4(extraction)["title"] == "AnalysisProposalV4"


def test_candidate_freeze_matches_all_current_execution_sources_and_keeps_limits():
    request = SemanticCampaignRequestV1.model_validate_json((BASE / "request.json").read_bytes())
    expected = {
        p.relative_to(ROOT).as_posix() for p in (ROOT / "src/ai_harness_compiler").rglob("*.py")
    }
    assert {s.path for s in request.sources} == expected | {"pyproject.toml", "uv.lock"}
    for source in request.sources:
        assert hashlib.sha256((ROOT / source.path).read_bytes()).hexdigest() == source.sha256
    assert request.max_calls == 16 and request.limits.session_timeout_seconds == 3600
    assert (
        request.limits.call_timeout_seconds == 180 and request.limits.cleanup_timeout_seconds == 20
    )
    assert request.limits.max_input_bytes == 1048576 and request.limits.max_output_bytes == 4194304


def test_candidate_protocol_cannot_transfer_closed_budget_or_human_output_reviews():
    protocol = json.loads((BASE / "protocol.json").read_bytes())
    assert protocol["status"] == "pending-exact-execution-authorization"
    assert protocol["execution_authorized"] is False and protocol["model_invocations"] == 0
    assert protocol["inputs_or_expectations_changed"] is False
    assert protocol["output_schema_changed"] is False and protocol["audit_program_changed"] is False
    assert (
        protocol["output_review"] == "not-run"
        and protocol["model_qualification"] == "not-established"
    )
    assert protocol["compilation_eligibility"] == "not-authorized"
    assert protocol["assets_read"] is False and protocol["holdout_accessed"] is False
    assert protocol["defaults_changed"] is False and not (BASE / "authorization.json").exists()
