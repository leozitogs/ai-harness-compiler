"""PO approval adds a declaration; it cannot alter expectations or grant calls."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import preflight_case

ROOT = Path(__file__).resolve().parents[1]
REVIEWED = ROOT / "evals/understanding/v4/development-reviewed"
PROPOSED = ROOT / "evals/understanding/v4/development-proposal"
PROPOSAL_DIGEST = "952e1dd71495e950eb3d9ba625db82d31538eb6a5c5ac9bf10dadd03c6897a9b"
REVIEWED_DIGEST = "8f666df68dcc150caaa085051487784ec907219d8ab7f78de8b120f480f7381b"


def test_approval_is_bound_to_the_exact_proposal_and_human_reply():
    reviewed = json.loads((REVIEWED / "manifest.json").read_bytes())
    proposed_raw = (ROOT / reviewed["proposal_source"]).read_bytes()
    assert hashlib.sha256(proposed_raw).hexdigest() == reviewed["proposal_file_sha256"]
    assert canonical_project_digest(json.loads(proposed_raw)) == PROPOSAL_DIGEST
    assert reviewed["proposal_sha256"] == PROPOSAL_DIGEST
    assert canonical_project_digest(reviewed) == REVIEWED_DIGEST
    assert reviewed["approval"]["question_id"] == "call_1a520665d7ed48b58e348c28046906b2"
    assert reviewed["approval"]["answer"] == "Li e aprovo as expectativas dos oito casos"
    assert reviewed["approval"]["declaration"]["authority"] == ("human-declared-not-authenticated")


def test_reviewed_snapshots_add_only_the_explicit_approval_and_preserve_proposals():
    reviewed = json.loads((REVIEWED / "manifest.json").read_bytes())
    proposed = json.loads((PROPOSED / "manifest.json").read_bytes())
    originals = {e["id"]: e for e in proposed["cases"]}
    assert len(reviewed["cases"]) == len(originals) == 8
    assert [e["id"] for e in reviewed["cases"]] == list(originals)
    for entry in reviewed["cases"]:
        original = originals[entry["id"]]
        proposed_raw = (PROPOSED / original["path"]).read_bytes()
        reviewed_raw = (REVIEWED / entry["path"]).read_bytes()
        old = AssessmentCaseV3.model_validate_json(proposed_raw)
        new = AssessmentCaseV3.model_validate_json(reviewed_raw)
        assert hashlib.sha256(proposed_raw).hexdigest() == entry["proposed_file_sha256"]
        assert hashlib.sha256(reviewed_raw).hexdigest() == entry["file_sha256"]
        assert old.snapshot_sha256 == entry["proposed_case_sha256"] == original["case_sha256"]
        assert new.snapshot_sha256 == entry["case_sha256"] != old.snapshot_sha256
        assert new.model_dump(exclude={"expectations_approval"}) == old.model_dump(
            exclude={"expectations_approval"}
        )
        assert old.expectations_approval is None
        assert new.expectations_approval is not None
        assert new.expectations_approval.model_dump() == reviewed["approval"]["declaration"]
        assert canonical_project_digest(new.project.model_dump()) == entry["project_sha256"]
        assert new.expected_behavior == entry["expected_behavior"]
        report = preflight_case(new, "SemanticAnalysis/v4")
        assert report.status == "compatible"
        assert report.model_dump(mode="json") == entry["preflight"]


def test_expectations_approval_does_not_authorize_execution_or_judge_outputs():
    data = json.loads((REVIEWED / "manifest.json").read_bytes())
    assert data["status"] == "expectations-approved"
    assert data["split"] == "development"
    assert data["execution_authorized"] is False
    assert data["model_invocations"] == 0
    assert data["holdout_accessed"] is False and data["assets_read"] is False
    assert data["output_review"] == "not-run"
    assert data["model_qualification"] == "not-established"
    assert data["compilation_eligibility"] == "not-authorized"
    assert (
        hashlib.sha256((ROOT / data["rubric_source"]).read_bytes()).hexdigest()
        == (data["rubric_sha256"])
    )
    assert sorted(e["expected_behavior"] for e in data["cases"]) == (
        ["blocked"] * 2 + ["ready"] * 6
    )
