"""New source freeze keeps the approved case but never transfers a consumed budget."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.semantic_preflight import preflight_case
from ai_harness_compiler.models.supervised_transport import SupervisedFlowRequestV1

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "evals/understanding/v4"
PREVIOUS = BASE / "compatibility-reviewed"
CURRENT = BASE / "compatibility-utf8-reviewed"


def load(directory, name):
    return json.loads((directory / name).read_text(encoding="utf-8"))


def test_utf8_freeze_preserves_exact_case_programs_and_execution_limits():
    old = SupervisedFlowRequestV1.model_validate(load(PREVIOUS, "request.json"))
    new = SupervisedFlowRequestV1.model_validate(load(CURRENT, "request.json"))
    assert new.flow.run_id != old.flow.run_id
    assert new.flow.model_dump(exclude={"run_id"}) == old.flow.model_dump(exclude={"run_id"})
    assert new.flow.case.expectations_approval is not None
    assert new.model_dump(exclude={"flow", "sources"}) == old.model_dump(
        exclude={"flow", "sources"}
    )
    before = {entry.path: entry.sha256 for entry in old.sources}
    after = {entry.path: entry.sha256 for entry in new.sources}
    assert before.keys() == after.keys()
    changes = [
        dict(path=path, before=before[path], after=after[path])
        for path in sorted(before)
        if before[path] != after[path]
    ]
    assert changes == load(CURRENT, "protocol.json")["source_changes"]
    assert [entry["path"] for entry in changes] == [
        "src/ai_harness_compiler/adapters/semantic_worker_v4.py"
    ]


def test_utf8_request_manifest_binds_prior_closed_execution_and_approved_case():
    protocol = load(CURRENT, "protocol.json")
    request = SupervisedFlowRequestV1.model_validate(load(CURRENT, "request.json"))
    assert protocol["request_sha256"] == request.sha256
    assert protocol["case_sha256"] == request.flow.case.snapshot_sha256
    assert (
        hashlib.sha256((CURRENT / "request.json").read_bytes()).hexdigest()
        == (protocol["request_file_sha256"])
    )
    for source_field, hash_field in [
        ("case_source", "case_file_sha256"),
        ("expectations_decision_source", "expectations_decision_file_sha256"),
        ("previous_execution_source", "previous_execution_file_sha256"),
    ]:
        assert (
            hashlib.sha256((ROOT / protocol[source_field]).read_bytes()).hexdigest()
            == (protocol[hash_field])
        )
    previous = SupervisedFlowRequestV1.model_validate_json(
        (ROOT / protocol["previous_request_source"]).read_bytes()
    )
    assert previous.sha256 == protocol["previous_request_sha256"] != request.sha256
    execution = json.loads((ROOT / protocol["previous_execution_source"]).read_bytes())
    assert execution["request_sha256"] == previous.sha256
    assert execution["budget"] == protocol["previous_budget_status"] == "closed"
    assert execution["invocations"] == 1 and execution["status"] == "failed"


def test_utf8_preparation_is_compatible_but_does_not_authorize_execution():
    protocol = load(CURRENT, "protocol.json")
    request = SupervisedFlowRequestV1.model_validate(load(CURRENT, "request.json"))
    preflight = preflight_case(request.flow.case, "SemanticAnalysis/v4")
    assert preflight.status == "compatible"
    assert preflight.model_dump(mode="json") == load(CURRENT, "preflight.json")
    assert protocol["expectations_approved"] is True
    assert protocol["execution_authorized"] is False
    assert protocol["status"] == "pending-execution-authorization"
    assert protocol["limits"] == request.limits.model_dump()
    assert protocol["model_invocations_observed"] == 0
    assert protocol["max_proposed_invocations"] == request.flow.max_generator_calls == 2
    assert all(protocol[key] is False for key in ["retry", "repair", "fallback", "resume"])
    assert protocol["compilation_eligibility"] == "not-authorized"
    assert protocol["model_qualification"] == "not-established"
    assert not list(CURRENT.glob("*authorization*"))
