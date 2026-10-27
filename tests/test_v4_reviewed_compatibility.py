"""PO expectation approval changes identity without granting an execution budget."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import preflight_case
from ai_harness_compiler.models.supervised_transport import SupervisedFlowRequestV1

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evals/understanding/v4"
ORIGINAL = BASE / "compatibility-proposal"
REVIEWED = BASE / "compatibility-reviewed"


def load(directory, name):
    return json.loads((directory / name).read_text(encoding="utf-8"))


def test_reviewed_case_changes_only_human_expectations_declaration():
    original = AssessmentCaseV3.model_validate(load(ORIGINAL, "case.json"))
    reviewed = AssessmentCaseV3.model_validate(load(REVIEWED, "case.json"))
    decision = load(REVIEWED, "expectations-decision.json")
    assert original.expectations_approval is None
    assert reviewed.expectations_approval is not None
    assert reviewed.model_dump(exclude={"expectations_approval"}) == original.model_dump(
        exclude={"expectations_approval"}
    )
    assert decision["answer"] == "Aprovo as cinco expectativas deste caso"
    assert decision["original_case_sha256"] == original.snapshot_sha256
    assert decision["reviewed_case_sha256"] == reviewed.snapshot_sha256
    assert reviewed.snapshot_sha256 != original.snapshot_sha256
    assert decision["approval"] == reviewed.expectations_approval.model_dump()
    assert (
        hashlib.sha256((ROOT / decision["original_review_document"]).read_bytes()).hexdigest()
        == (decision["original_review_document_sha256"])
    )
    assert decision["execution_authorized"] is False
    assert decision["output_review"] == "not-run"


def test_final_request_preserves_programs_sources_destination_and_budget_bounds():
    original = SupervisedFlowRequestV1.model_validate(load(ORIGINAL, "request.proposed.json"))
    reviewed = SupervisedFlowRequestV1.model_validate(load(REVIEWED, "request.json"))
    assert reviewed.flow.run_id != original.flow.run_id
    assert reviewed.flow.model_dump(exclude={"case", "run_id"}) == original.flow.model_dump(
        exclude={"case", "run_id"}
    )
    assert reviewed.model_dump(exclude={"flow"}) == original.model_dump(exclude={"flow"})
    assert reviewed.flow.case == AssessmentCaseV3.model_validate(load(REVIEWED, "case.json"))
    preflight = preflight_case(reviewed.flow.case, "SemanticAnalysis/v4")
    assert preflight.status == "compatible"
    assert preflight.model_dump(mode="json") == load(REVIEWED, "preflight.json")


def test_reviewed_protocol_binds_final_files_without_granting_execution():
    protocol = load(REVIEWED, "protocol.json")
    request = SupervisedFlowRequestV1.model_validate(load(REVIEWED, "request.json"))
    assert request.sha256 == protocol["request_sha256"]
    assert request.flow.case.snapshot_sha256 == protocol["reviewed_case_sha256"]
    for file, field in [
        ("request.json", "request_file_sha256"),
        ("case.json", "case_file_sha256"),
        ("expectations-decision.json", "expectations_decision_file_sha256"),
    ]:
        assert hashlib.sha256((REVIEWED / file).read_bytes()).hexdigest() == protocol[field]
    assert (
        hashlib.sha256((ROOT / protocol["original_proposal_source"]).read_bytes()).hexdigest()
        == (protocol["original_proposal_file_sha256"])
    )
    assert protocol["limits"] == request.limits.model_dump()
    assert protocol["status"] == "pending-execution-authorization"
    assert protocol["expectations_approved"] is True
    assert protocol["execution_authorized"] is False
    assert protocol["model_invocations_observed"] == 0
    assert protocol["model_qualification"] == "not-established"
    assert protocol["compilation_eligibility"] == "not-authorized"
    assert not list(REVIEWED.glob("*authorization*"))
