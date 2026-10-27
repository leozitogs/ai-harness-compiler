"""Exposed development expectations are proposals, never migrated PO approvals."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import preflight_case

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evals/understanding/v4/development-proposal"


def manifest():
    return json.loads((CORPUS / "manifest.json").read_bytes())


def test_proposed_corpus_preserves_all_eight_historical_public_inputs():
    data = manifest()
    original_raw = (ROOT / data["original_manifest_source"]).read_bytes()
    assert hashlib.sha256(original_raw).hexdigest() == data["original_manifest_sha256"]
    original = json.loads(original_raw)
    assert len(data["cases"]) == len(original["cases"]) == 8
    assert {e["original_case_id"] for e in data["cases"]} == {
        Path(e["path"]).stem for e in original["cases"]
    }
    for entry in data["cases"]:
        source_raw = (ROOT / entry["source"]).read_bytes()
        assert hashlib.sha256(source_raw).hexdigest() == entry["source_sha256"]
        old = AssessmentCase.model_validate_json(source_raw)
        new_raw = (CORPUS / entry["path"]).read_bytes()
        new = AssessmentCaseV3.model_validate_json(new_raw)
        assert hashlib.sha256(new_raw).hexdigest() == entry["file_sha256"]
        assert old.snapshot_sha256 == entry["original_case_sha256"]
        assert new.snapshot_sha256 == entry["case_sha256"]
        assert new.project == old.project
        assert canonical_project_digest(new.project.model_dump()) == entry["project_sha256"]
        assert new.expected_behavior == old.expected_behavior == entry["expected_behavior"]
        assert old.expectations_approval is not None and new.expectations_approval is None
        assert new.id == old.id + "-v4"


def test_normative_context_and_injection_have_explicit_source_bound_expectations():
    for entry in manifest()["cases"]:
        case = AssessmentCaseV3.model_validate_json((CORPUS / entry["path"]).read_bytes())
        preflight = preflight_case(case, "SemanticAnalysis/v4")
        assert preflight.status == "compatible"
        assert preflight.model_dump(mode="json") == entry["preflight"]
        obligations = {o.id: o for o in case.obligations}
        if entry["original_case_id"] == "dev-compatible-rules":
            assert "responsible-identity" not in obligations
            assert obligations["trace-privacy"].source_pointer == "/constraints/security/0"
            assert obligations["technical-1"].disposition == "requirement"
            assert obligations["technical-2"].disposition == "requirement"
            assert obligations["accessible-interface"].disposition == "requirement"
        else:
            identity = obligations["responsible-identity"]
            assert identity.source_pointer == "/constraints/business/0"
            assert identity.disposition == "requirement"
            assert identity.quote == case.project.constraints.business[0]
        assert case.required_content_rejection_pointers == (
            ["/branding/tone/0"] if entry["original_case_id"] == "dev-adversarial" else []
        )
        assert not case.required_project_rejection_pointers


def test_proposal_cannot_grant_a_campaign_or_claim_independent_evaluation():
    data = manifest()
    assert data["status"] == "pending-po-expectations" and data["split"] == "development"
    assert data["expectations_approved"] is False
    assert data["execution_authorized"] is False and data["model_invocations"] == 0
    assert data["holdout_accessed"] is False and data["assets_read"] is False
    assert data["output_review"] == "not-run"
    assert data["model_qualification"] == "not-established"
    assert all(e["expectations_approved"] is False for e in data["cases"])
    assert (
        hashlib.sha256((ROOT / data["rubric_source"]).read_bytes()).hexdigest()
        == (data["rubric_sha256"])
    )
