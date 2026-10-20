"""Replay a bounded real run offline without granting semantic approval."""

import hashlib
import json
from pathlib import Path

import pytest

from ai_harness_compiler.models.semantic_analysis_v3 import AnalysisProposalV3, SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment_v3 import (
    SemanticAssessmentV3,
    SemanticHumanReviewV3,
    assess_v3,
)
from ai_harness_compiler.models.semantic_verification_v4 import (
    SemanticVerifierReportV4,
    VerifierProposalV4,
)
from ai_harness_compiler.semantic_composition import audit_composition, composition_program_digest

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/evidence/sprint-2-6-v34-development-20261020"


def test_v34_authorization_preserves_prior_rejection_and_protocol():
    raw = (FOLDER / "protocol.json").read_bytes()
    protocol = json.loads(raw)
    authorization = json.loads((FOLDER / "authorization.json").read_bytes())
    rejection = json.loads((FOLDER / "execution-status.json").read_bytes())
    assert authorization["confirmation"] == "autorizo, podes efetuar a rodada."
    assert authorization["protocol_sha256"] == hashlib.sha256(raw).hexdigest()
    assert rejection["protocol_sha256"] == authorization["protocol_sha256"]
    assert rejection["executor_started"] is False and rejection["calls_used"] == 0
    assert authorization["supersedes_permission_state"] == rejection["status"]
    assert authorization["authority"] == "human-declared-not-authenticated"
    assert protocol["budget"]["max_calls"] == 16
    assert protocol["budget"]["max_concurrency"] == 1
    assert protocol["budget"]["repetitions"] == 1
    for field in ("retries", "repair_attempts", "holdout_calls"):
        assert protocol["budget"][field] == 0
    for binding in ("baseline_manifest", "development_manifest", "previous_round_review"):
        source = protocol[binding]
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    assert (
        hashlib.sha256((FOLDER / "runner-source.txt").read_bytes()).hexdigest()
        == protocol["runner_sha256"]
    )


def test_v34_real_run_retains_all_attempts_and_artifact_bytes():
    run = json.loads((FOLDER / "execution/summary.json").read_bytes())
    assert (
        run["protocol_sha256"]
        == hashlib.sha256((FOLDER / "protocol.json").read_bytes()).hexdigest()
    )
    starts = list((FOLDER / "execution").glob("*/*-call-start.json"))
    assert len(starts) == run["calls_used"] <= run["max_calls"] == 16
    assert sorted(json.loads(p.read_bytes())["number"] for p in starts) == list(
        range(1, run["calls_used"] + 1)
    )
    assert len(run["cases"]) == 8
    assert run["holdout_read"] is False
    assert run["semantic_status"] == "not-run"
    assert run["model_qualification"] == "not-established"
    for path in starts:
        start = json.loads(path.read_bytes())
        finish = json.loads(path.with_name(path.name.replace("-start", "-finish")).read_bytes())
        assert all(start[k] == finish[k] for k in start if k != "status")
        assert finish["status"] in {"returned", "error"}
        assert 1 <= start["timeout_seconds"] <= 180
    inventory = json.loads((FOLDER / "artifact-inventory.json").read_bytes())
    for artifact in inventory["artifacts"]:
        assert (
            hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
        )


def test_v34_initial_assessments_never_transfer_older_approvals():
    comparison = json.loads((FOLDER / "comparison.json").read_bytes())
    protocol = json.loads((FOLDER / "protocol.json").read_bytes())
    assert comparison["human_reviews_reused"] == 0
    assert comparison["previous_round_assessments"] == {
        "pass_count": 6,
        "fail_count": 2,
        "not_run_count": 0,
    }
    for row in comparison["cases"]:
        if row["new_generation"] != "valid":
            assert row["assessment"] == "error"
            continue
        folder = FOLDER / "execution" / row["case"]
        assessment = SemanticAssessmentV3.model_validate_json(
            (folder / "assessment.json").read_bytes()
        )
        assert assessment.review is None
        assert assessment == assess_v3(assessment.case, assessment.rubric, assessment.analysis)
        assert assessment.status != "pass"
        assert assessment.model_qualification == "not-established"
        assert assessment.compilation_eligibility == "not-authorized"
        assert assessment.analysis_sha256 == row["analysis_sha256"]
        assert composition_program_digest(
            assessment.analysis.extraction, "semantic-composition/v3.4"
        ) == next(c["program_sha256"] for c in protocol["cases"] if c["case"] == row["case"])
        assert (
            AnalysisProposalV3.model_validate_json(
                (folder / "generation-response.txt").read_bytes()
            )
            == assessment.analysis.proposal
        )
        if row["new_audit"] == "valid":
            advice = SemanticVerifierReportV4.model_validate_json(
                (folder / "advice.json").read_bytes()
            )
            assert advice.analysis == assessment.analysis
            assert (
                VerifierProposalV4.model_validate_json((folder / "audit-response.txt").read_bytes())
                == advice.proposal
            )


def test_v34_rejects_returned_audit_with_mutated_digest_without_repair():
    folder = FOLDER / "execution/dev-new-domain"
    analysis = SemanticAnalysisV3.model_validate_json((folder / "analysis.json").read_bytes())
    raw = (folder / "audit-response.txt").read_bytes()
    proposal = VerifierProposalV4.model_validate_json(raw)
    mismatches = [
        row.finding_id
        for row in proposal.findings
        if row.finding_sha256
        != next(finding.sha256 for finding in analysis.findings if finding.id == row.finding_id)
    ]
    assert mismatches == ["context-4"]

    class SavedResponse:
        calls = 0

        def generate_json(self, prompt, schema):
            self.calls += 1
            return raw.decode("utf-8")

    saved = SavedResponse()
    with pytest.raises(ValueError, match="Verifier finding digest or exact source binding differs"):
        audit_composition(analysis, saved, "gpt-6.1-sol")
    assert saved.calls == 1
    assert (folder / "audit-response.txt").read_bytes() == raw
    summary = json.loads((folder / "summary.json").read_bytes())
    receipt = json.loads((folder / "audit-call-finish.json").read_bytes())
    assert summary["audit"] == "error" and summary["calls_used"] == 2
    assert receipt["status"] == "returned"


def test_v34_human_judgments_are_bound_to_new_snapshots_without_approving_failed_audit():
    manifest = json.loads((FOLDER / "human-review/manifest.json").read_bytes())
    assert manifest["assessments"] == {"pass_count": 8, "fail_count": 0, "not_run_count": 0}
    assert manifest["criteria_judged"] == manifest["criteria_pass"] == 48
    assert manifest["criteria_pending"] == manifest["criteria_fail"] == 0
    assert manifest["candidate_promoted"] is False
    assert manifest["calls_during_review"] == 0
    assert manifest["confirmations"] == {
        "ready_cases": "Aprovo os seis critérios das seis análises ready v3.4",
        "branding_conflict": "Aprovo os seis critérios de dev-branding-conflict v3.4",
        "ambiguous": "Aprovo a interpretação e os seis critérios de dev-ambiguous v3.4",
    }
    for row in manifest["cases"]:
        for key in ("review", "assessment"):
            source = row[key]
            assert (
                hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
            )
        assessment = SemanticAssessmentV3.model_validate_json(
            (ROOT / row["assessment"]["path"]).read_bytes()
        )
        review = SemanticHumanReviewV3.model_validate_json(
            (ROOT / row["review"]["path"]).read_bytes()
        )
        assert assessment.review == review
        assert assessment == assess_v3(
            assessment.case, assessment.rubric, assessment.analysis, review
        )
        assert assessment.status == row["status"] == "pass"
        assert assessment.analysis_sha256 == row["analysis_sha256"]
        assert assessment.analysis.disposition == assessment.case.expected_behavior
        assert assessment.model_qualification == "not-established"
        assert assessment.compilation_eligibility == "not-authorized"
        assert row["audit_status"] == ("error" if row["case"] == "dev-new-domain" else "valid")
