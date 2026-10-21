"""Offline replay of one explicitly authorized provider compatibility observation."""

import base64
import hashlib
import json
from pathlib import Path

from ai_harness_compiler.adapters.codex_cli import strict_schema
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_verification_v4 import (
    SemanticVerifierReportV4,
    VerifierProposalV4,
)
from ai_harness_compiler.semantic_composition import (
    component_audit_program_digest,
    component_audit_schema,
)

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "docs/evidence/sprint-2-6-bound-audit-smoke-20261021"


def test_single_call_scope_and_explicit_authorization_are_preserved():
    raw = (FOLDER / "protocol.json").read_bytes()
    protocol = json.loads(raw)
    authorization = json.loads((FOLDER / "authorization.json").read_bytes())
    summary = json.loads((FOLDER / "execution/summary.json").read_bytes())
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == "8b3adf3a5e68ba7b417e398d6e03382e3de302724d9ea143c6a09b38bbd88799"
    assert authorization["protocol_sha256"] == summary["protocol_sha256"] == digest
    assert authorization["authorized"] is True
    assert authorization["confirmation"] == "Autorizo a única chamada com esses limites"
    assert protocol["budget"]["max_calls"] == summary["model_calls"] == 1
    assert protocol["budget"]["max_concurrency"] == 1
    assert protocol["budget"]["max_call_seconds"] == 180
    assert protocol["budget"]["max_session_seconds"] == 240
    for key in ("retries", "repair_attempts", "holdout_calls"):
        assert protocol["budget"][key] == 0
    assert not any(protocol["constraints"].values())
    assert summary["elapsed_seconds"] <= 240
    assert summary["status"] == "valid-structural-report"
    assert summary["semantic_status"] == "not-established"
    assert summary["model_qualification"] == "not-established"
    assert summary["candidate_promoted"] is False


def test_original_runner_bytes_and_all_published_artifacts_match_digests():
    protocol = json.loads((FOLDER / "protocol.json").read_bytes())
    source = json.loads((FOLDER / "runner-source.json").read_bytes())
    decoded = base64.b64decode(source["data"], validate=True)
    assert hashlib.sha256(decoded).hexdigest() == source["sha256"] == protocol["runner_sha256"]
    inventory = json.loads((FOLDER / "artifact-inventory.json").read_bytes())
    assert len(inventory["artifacts"]) == 8
    for row in inventory["artifacts"]:
        assert hashlib.sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"]


def test_new_advice_binds_the_exact_public_analysis_and_preserves_authority():
    protocol = json.loads((FOLDER / "protocol.json").read_bytes())
    raw = (ROOT / protocol["analysis"]["path"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == protocol["analysis"]["file_sha256"]
    analysis = SemanticAnalysisV3.model_validate_json(raw)
    assert analysis.snapshot_sha256 == protocol["analysis"]["snapshot_sha256"]
    assert (
        component_audit_program_digest(analysis, "component-audit/v4.1")
        == (protocol["program_sha256"])
    )
    start = json.loads((FOLDER / "execution/call-start.json").read_bytes())
    finish = json.loads((FOLDER / "execution/call-finish.json").read_bytes())
    schema = component_audit_schema(analysis, program_version="component-audit/v4.1")
    assert canonical_project_digest(schema) == protocol["schema_sha256"]
    assert start["response_schema_sha256"] == protocol["schema_sha256"]
    assert start["effective_schema_sha256"] == canonical_project_digest(strict_schema(schema))
    assert all(start[k] == finish[k] for k in start if k != "status")
    assert finish["status"] == "returned"
    report = SemanticVerifierReportV4.model_validate_json(
        (FOLDER / "execution/report.json").read_bytes()
    )
    proposal = VerifierProposalV4.model_validate_json(
        (FOLDER / "execution/response.txt").read_bytes()
    )
    assert report.analysis == analysis and report.proposal == proposal
    assert report.authority == "model-advisory"
    assert report.semantic_status == report.model_qualification == "not-established"
    assert report.compilation_eligibility == "not-authorized"
    context = next(row for row in proposal.findings if row.finding_id == "context-4")
    assert context.finding_sha256 == next(
        f.sha256 for f in analysis.findings if f.id == "context-4"
    )
