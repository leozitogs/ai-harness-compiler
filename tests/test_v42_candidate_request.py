"""Offline candidate identity is not a new execution grant or semantic qualification."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.semantic_campaign import SemanticCampaignRequestV1
from ai_harness_compiler.semantic_generation_programs import program_prompt, resolve_program
from ai_harness_compiler.semantic_generation_v4 import audit_v5_program_digest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evals/understanding/v4/development-candidate-v42"
DIGEST = "20684db385afc73a5d9326d9946369e76284b4a8a60e199cefe77f7fcdc3a12a"


def test_v42_preserves_the_approved_cases_rubric_sources_and_audit():
    new = SemanticCampaignRequestV1.model_validate_json((BASE / "request.json").read_bytes())
    old = SemanticCampaignRequestV1.model_validate_json(
        (BASE.parent / "development-candidate-v41/request.json").read_bytes()
    )
    assert new.sha256 == DIGEST and new.campaign_id != old.campaign_id
    assert new.corpus_sha256 == old.corpus_sha256 and len(new.flows) == len(old.flows) == 8
    for candidate, baseline in zip(new.flows, old.flows, strict=True):
        assert candidate.case == baseline.case and candidate.rubric == baseline.rubric
        assert candidate.run_id != baseline.run_id
        assert candidate.requested_model == baseline.requested_model == "gpt-6.1-sol"
        assert (
            candidate.audit_program_sha256
            == baseline.audit_program_sha256
            == audit_v5_program_digest()
        )
        extraction = extract_grounding(candidate.case.project)
        assert (
            resolve_program(extraction, candidate.generation_program_sha256)
            == "semantic-composition/v4.2"
        )
        assert (
            resolve_program(extraction, baseline.generation_program_sha256)
            == "semantic-composition/v4.1"
        )
        assert (
            program_prompt(extraction, candidate.generation_program_sha256).split(
                "\nINPUT DATA:\n"
            )[1]
            == program_prompt(extraction, baseline.generation_program_sha256).split(
                "\nINPUT DATA:\n"
            )[1]
        )


def test_prepared_v42_freeze_matches_the_entire_current_implementation():
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


def test_protocol_is_unexecuted_and_historical_diagnostics_do_not_regrade_outputs():
    protocol = json.loads((BASE / "protocol.json").read_bytes())
    assert protocol["request_sha256"] == DIGEST
    assert protocol["execution_authorized"] is False and protocol["model_invocations"] == 0
    assert protocol["status"] == "pending-exact-execution-authorization"
    assert protocol["inputs_or_expectations_changed"] is False
    assert protocol["output_schema_changed"] is False and protocol["audit_program_changed"] is False
    assert protocol["defaults_changed"] is False and protocol["holdout_accessed"] is False
    assert (
        protocol["output_review"] == "not-run"
        and protocol["model_qualification"] == "not-established"
    )
    assert protocol["compilation_eligibility"] == "not-authorized"
    assert not (BASE / "authorization.json").exists()
    observed = json.loads(
        (
            ROOT / "docs/evidence/sprint-2-6-v42-preparation-20261028/offline-diagnostics.json"
        ).read_bytes()
    )
    reviewed = json.loads(
        (ROOT / "docs/evidence/sprint-2-6-v41-development-20261028/human-review.json").read_bytes()
    )
    assert observed["new_model_invocations"] == 0 and observed["original_outputs_preserved"] is True
    assert (
        observed["semantic_judgments_changed"] is False
        and observed["expectations_changed"] is False
    )
    assert (
        observed["historical_worker_exit"] == 2
        and observed["historical_worker_category"] == "unknown"
    )
    assert (
        observed["original_human_review_file_sha256"]
        == hashlib.sha256(
            (
                ROOT / "docs/evidence/sprint-2-6-v41-development-20261028/human-review.json"
            ).read_bytes()
        ).hexdigest()
    )
    for entry, original in zip(observed["cases"], reviewed["cases"], strict=True):
        assert entry["analysis_sha256"] == original["analysis_sha256"]
        assert entry["original_human_verdict"] == original["reviewed_assessment_status"]
        assert entry["status"] == (
            "missing-question" if entry["case_id"] == "dev-branding-conflict-v4" else "no-conflicts"
        )
