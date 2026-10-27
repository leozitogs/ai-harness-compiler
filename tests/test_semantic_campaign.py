"""Global budget and provenance attacks with synthetic workers, never model calls."""

import hashlib
import json
import shutil
import sys
from pathlib import Path
from time import monotonic, sleep

import pytest
from jsonschema import Draft202012Validator
from test_semantic_assessment import declaration
from test_semantic_flow_v4 import audit_proposal, fixtures, request_pair

import ai_harness_compiler.semantic_campaign as campaign
import ai_harness_compiler.supervised_semantic_flow as supervised
from ai_harness_compiler.adapters.process_supervisor import WorkerOutcome, invoke_json_worker
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_analysis_v4 import SemanticAnalysisV4
from ai_harness_compiler.models.semantic_campaign import (
    SemanticCampaignAuthorizationV1,
    SemanticCampaignReportV1,
    SemanticCampaignRequestV1,
)
from ai_harness_compiler.models.supervised_transport import TransportLimitsV1, TransportReceiptV1
from ai_harness_compiler.semantic_generation_v4 import generation_program_v4

ROOT = Path(__file__).resolve().parents[1]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False) + "\n", encoding="utf-8")


def prepare(tmp_path, monkeypatch, count=2):
    root = tmp_path / "repository"
    shutil.copytree(
        ROOT / "src/ai_harness_compiler",
        root / "src/ai_harness_compiler",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    for name in ("pyproject.toml", "uv.lock"):
        shutil.copyfile(ROOT / name, root / name)
    corpus = root / "evals/synthetic-reviewed"
    corpus.mkdir(parents=True)
    case, rubric, analysis = fixtures()
    flows, analyses, entries = [], [], []
    for index in range(count):
        changed = case.model_copy(deep=True)
        changed.id = f"synthetic-case-{index}"
        changed.project.constraints.max_build_cost_usd = float(index)
        current = SemanticAnalysisV4(
            extraction=extract_grounding(changed.project), proposal=analysis.proposal
        )
        flow, _ = request_pair(changed, rubric, current)
        flow.run_id = f"synthetic-campaign-case-{index}"
        flows.append(flow)
        analyses.append(current)
        path = corpus / f"case-{index}.json"
        save(path, changed.model_dump(mode="json"))
        entries.append(
            dict(
                id=changed.id,
                path=path.name,
                case_sha256=changed.snapshot_sha256,
                project_sha256=canonical_project_digest(changed.project.model_dump()),
                file_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            )
        )
    save(corpus / "rubric.json", rubric.model_dump(mode="json"))
    save(
        corpus / "manifest.json",
        dict(
            status="expectations-approved",
            split="development",
            target_analysis="SemanticAnalysis/v4",
            cases=entries,
            rubric_source="evals/synthetic-reviewed/rubric.json",
            rubric_sha256=hashlib.sha256((corpus / "rubric.json").read_bytes()).hexdigest(),
        ),
    )
    policy = TransportLimitsV1(
        call_timeout_seconds=3, cleanup_timeout_seconds=2, session_timeout_seconds=30
    )
    request = campaign.prepare_campaign(
        root,
        campaign_id="synthetic-campaign",
        corpus_source="evals/synthetic-reviewed/manifest.json",
        flows=flows,
        limits=policy,
    )
    auth = SemanticCampaignAuthorizationV1(
        **declaration().model_dump(), request_sha256=request.sha256, authorized=True
    )
    clock, seen = [1000.0], []
    monkeypatch.setattr(campaign, "monotonic", lambda: clock[0])

    def worker(command, payload, *, cwd, limits, session_deadline, index):
        position = len(seen)
        seen.append((payload, session_deadline, index))
        # The global debit must exist before calling the transport.
        directory = root / ".factory/semantic-v4-campaigns" / request.campaign_id
        assert (directory / f"attempt-{position + 1}.json").is_file()
        current = analyses[position // 2]
        response = current.proposal.model_dump() if index == 1 else audit_proposal(current)
        grant = min(float(limits.call_timeout_seconds), session_deadline - clock[0] - 2)
        clock[0] += 1.0
        receipt = TransportReceiptV1(
            index=index,
            payload_sha256=canonical_project_digest(payload),
            command_sha256=canonical_project_digest({"argv": command}),
            granted_seconds=max(0.0, grant),
            elapsed_seconds=0.5,
            worker_pid=123,
            containment="posix-session",
            root_reaped=True,
            tree_termination_requested=True,
            exit_code=0,
            response_sha256=canonical_project_digest(response),
            status="succeeded",
        )
        return WorkerOutcome(receipt, json.dumps(response))

    monkeypatch.setattr(campaign, "invoke_json_worker", worker)
    return root, request, auth, clock, seen, worker


def test_global_success_replays_without_granting_semantic_approval(tmp_path, monkeypatch):
    root, req, auth, clock, seen, _ = prepare(tmp_path, monkeypatch)
    assert not (root / ".factory").exists()  # Preparation never consumes execution.
    result = campaign.run_campaign(root, req, auth)
    assert result.status == "completed" and len(seen) == req.max_calls == 4
    assert {s[1] for s in seen} == {1030.0}  # No clock reset between cases/stages.
    assert [s[2] for s in seen] == [1, 2, 1, 2]
    assert result.elapsed_seconds == clock[0] - 1000.0 == 4
    assert all(r.assessment.status == "not-run" for r in result.results)
    assert result.model_qualification == "not-established"
    assert result.compilation_eligibility == "not-authorized" and result.budget_closed
    assert campaign.validate_campaign(root, req.campaign_id) == result
    for value in (req, auth, result, result.calls[0]):
        Draft202012Validator(type(value).model_json_schema()).validate(
            value.model_dump(mode="json")
        )
    for payload, _, _ in seen:
        assert set(payload) == {"model", "prompt", "response_schema", "timeout_seconds"}
        assert "expectations_approval" not in payload["prompt"]
        assert declaration().note not in payload["prompt"]
    with pytest.raises(FileExistsError):
        campaign.run_campaign(root, req, auth)


@pytest.mark.parametrize("gate", ["authorization", "manifest", "case", "source", "rubric"])
def test_global_preflight_gates_precede_claims_and_workers(tmp_path, monkeypatch, gate):
    root, req, auth, _, seen, _ = prepare(tmp_path, monkeypatch)
    if gate == "authorization":
        auth.request_sha256 = "0" * 64
    elif gate == "manifest":
        (root / req.corpus_source).write_text("{}")
    elif gate == "case":
        save(root / "evals/synthetic-reviewed/case-0.json", {})
    elif gate == "source":
        (root / req.sources[0].path).write_text("changed")
    else:
        save(root / "evals/synthetic-reviewed/rubric.json", {})
    with pytest.raises(ValueError):
        campaign.run_campaign(root, req, auth)
    assert not seen and not (root / ".factory").exists()


@pytest.mark.parametrize("mutation", ["run", "case", "clone", "limit", "model", "approval", "path"])
def test_request_rejects_duplicate_unapproved_or_inconsistent_inputs(
    tmp_path, monkeypatch, mutation
):
    _, req, _, _, _, _ = prepare(tmp_path, monkeypatch)
    data = req.model_dump()
    flows = data["flows"]
    if mutation == "run":
        flows[1]["run_id"] = flows[0]["run_id"]
    elif mutation == "case":
        flows[1]["case"]["id"] = flows[0]["case"]["id"]
    elif mutation == "clone":
        second = req.flows[1].case.model_copy(deep=True)
        second.project = req.flows[0].case.project.model_copy(deep=True)
        second.project.id = "renamed-clone"
        second.project.name = "Renamed clone"
        flows[1]["case"] = second.model_dump()
        flows[1]["generation_program_sha256"] = generation_program_v4(
            extract_grounding(second.project)
        )
    elif mutation == "limit":
        data["max_calls"] = 16
    elif mutation == "model":
        flows[1]["requested_model"] = "other-model"
    elif mutation == "approval":
        flows[1]["case"]["expectations_approval"] = None
    else:
        data["corpus_source"] = "evals/../outside.json"
    with pytest.raises(ValueError):
        SemanticCampaignRequestV1.model_validate(data)


def test_global_deadline_between_cases_never_launches_next_worker(tmp_path, monkeypatch):
    root, req, auth, clock, seen, worker = prepare(tmp_path, monkeypatch)

    def near_deadline(*args, **kwargs):
        outcome = worker(*args, **kwargs)
        if len(seen) == 2:
            clock[0] = 1029.0
        return outcome

    monkeypatch.setattr(campaign, "invoke_json_worker", near_deadline)
    result = campaign.run_campaign(root, req, auth)
    assert result.failure_code == "budget-exhausted" and result.budget_closed
    assert len(result.results) == 1 and len(seen) == 2
    assert not (root / ".factory/semantic-v4-runs" / req.flows[1].run_id).exists()
    assert campaign.validate_campaign(root, req.campaign_id) == result


@pytest.mark.parametrize("fault", ["audit", "cancelled", "exception", "overflow"])
def test_first_failure_stops_campaign_and_consumes_authorization(tmp_path, monkeypatch, fault):
    root, req, auth, _, seen, worker = prepare(tmp_path, monkeypatch)

    def broken(*args, **kwargs):
        if fault == "cancelled":
            raise KeyboardInterrupt
        if fault == "exception":
            raise RuntimeError("secret diagnostic must not persist")
        outcome = worker(*args, **kwargs)
        if fault == "audit" and len(seen) == 2:
            response = {}
            receipt = outcome.receipt.model_copy(
                update={"response_sha256": canonical_project_digest(response)}
            )
            return WorkerOutcome(receipt, json.dumps(response))
        if fault == "overflow":
            receipt = outcome.receipt.model_copy(
                update={"status": "failed", "failure_code": "output-limit", "response_sha256": None}
            )
            return WorkerOutcome(receipt, None)
        return outcome

    monkeypatch.setattr(campaign, "invoke_json_worker", broken)
    result = campaign.run_campaign(root, req, auth)
    assert result.status == "failed" and len(result.results) == 1
    assert len(result.calls) == (2 if fault == "audit" else 1)
    assert result.failure_code == ("cancelled" if fault == "cancelled" else "case-failed")
    assert campaign.validate_campaign(root, req.campaign_id) == result
    assert "secret diagnostic" not in result.model_dump_json()
    with pytest.raises(FileExistsError):
        campaign.run_campaign(root, req, auth)


@pytest.mark.parametrize("mutation", ["calls", "order", "grant", "elapsed", "command", "failure"])
def test_report_rejects_global_accounting_contradictions(tmp_path, monkeypatch, mutation):
    root, req, auth, _, _, _ = prepare(tmp_path, monkeypatch)
    result = campaign.run_campaign(root, req, auth)
    data = result.model_dump()
    if mutation == "calls":
        data["calls"].pop()
    elif mutation == "order":
        data["calls"][1]["started_offset_seconds"] = 0.0
    elif mutation == "grant":
        data["calls"][0]["receipt"]["granted_seconds"] = 300.0
    elif mutation == "elapsed":
        data["elapsed_seconds"] = 0.0
    elif mutation == "command":
        data["calls"][0]["receipt"]["command_sha256"] = "0" * 64
    else:
        data["calls"][0]["receipt"].update(status="failed", failure_code="call-timeout")
    with pytest.raises(ValueError):
        SemanticCampaignReportV1.model_validate(data)


@pytest.mark.parametrize("artifact", ["attempt", "call", "claim", "extra", "response"])
def test_replay_rejects_mutation_and_unaccounted_attempts(tmp_path, monkeypatch, artifact):
    root, req, auth, _, _, _ = prepare(tmp_path, monkeypatch)
    campaign.run_campaign(root, req, auth)
    directory = root / ".factory/semantic-v4-campaigns" / req.campaign_id
    path = {
        "attempt": directory / "attempt-1.json",
        "call": directory / "call-1.json",
        "claim": root / ".factory/semantic-v4-campaign-claims" / f"{req.sha256}.json",
        "extra": directory / "attempt-5.json",
        "response": root
        / ".factory/semantic-v4-runs"
        / req.flows[0].run_id
        / "analysis-response.json",
    }[artifact]
    save(path, {})
    with pytest.raises(ValueError):
        campaign.validate_campaign(root, req.campaign_id)


def test_eight_cases_share_a_single_sixteen_call_budget(tmp_path, monkeypatch):
    root, req, auth, _, seen, _ = prepare(tmp_path, monkeypatch, count=8)
    result = campaign.run_campaign(root, req, auth)
    assert result.status == "completed" and len(seen) == req.max_calls == 16
    assert {s[1] for s in seen} == {1030.0}
    assert campaign.validate_campaign(root, req.campaign_id) == result


def test_deadline_before_first_case_creates_no_worker_or_nested_run(tmp_path, monkeypatch):
    root, req, auth, clock, seen, _ = prepare(tmp_path, monkeypatch)
    original = campaign._validate_request

    def slow_validation(*args):
        original(*args)
        clock[0] = 1031.0

    monkeypatch.setattr(campaign, "_validate_request", slow_validation)
    result = campaign.run_campaign(root, req, auth)
    assert result.failure_code == "budget-exhausted" and result.calls == []
    assert result.results == [] and not seen
    assert campaign.validate_campaign(root, req.campaign_id) == result


def test_real_local_workers_and_reaping_integrate_with_campaign(tmp_path, monkeypatch):
    root, req, _, _, _, _ = prepare(tmp_path, monkeypatch, count=1)
    _, _, analysis = fixtures()
    first, second = tmp_path / "analysis.json", tmp_path / "audit.json"
    save(first, analysis.proposal.model_dump())
    save(second, audit_proposal(analysis))
    argv = [
        sys.executable,
        str(ROOT / "tests/fixtures/json_worker.py"),
        "flow",
        str(first),
        str(second),
    ]
    monkeypatch.setattr(campaign, "worker_command", lambda: argv)
    monkeypatch.setattr(supervised, "worker_command", lambda: argv)
    monkeypatch.setattr(campaign, "monotonic", monotonic)
    monkeypatch.setattr(campaign, "invoke_json_worker", invoke_json_worker)
    policy = req.limits.model_copy(update={"session_timeout_seconds": 120})
    req = campaign.prepare_campaign(
        root,
        campaign_id=req.campaign_id,
        corpus_source=req.corpus_source,
        flows=req.flows,
        limits=policy,
    )
    auth = SemanticCampaignAuthorizationV1(
        **declaration().model_dump(), request_sha256=req.sha256, authorized=True
    )
    result = campaign.run_campaign(root, req, auth)
    assert result.status == "completed"
    assert all(c.receipt.root_reaped and c.receipt.tree_termination_requested for c in result.calls)
    assert campaign.validate_campaign(root, req.campaign_id) == result


def test_keyboard_interrupt_still_cleans_owned_worker_and_descendant(tmp_path, monkeypatch):
    from test_supervised_transport import command, limits, process_running

    import ai_harness_compiler.adapters.process_supervisor as supervisor

    pidfile = tmp_path / "cancel-child-pid"
    original = supervisor.subprocess.Popen

    def interruptible(*args, **kwargs):
        process = original(*args, **kwargs)
        original_wait = process.wait
        interrupted = False

        def wait(*args, **kwargs):
            nonlocal interrupted
            if not interrupted:
                interrupted = True
                deadline = monotonic() + 2
                while not pidfile.is_file() and monotonic() < deadline:
                    sleep(0.01)
                raise KeyboardInterrupt
            return original_wait(*args, **kwargs)

        monkeypatch.setattr(process, "wait", wait)
        return process

    monkeypatch.setattr(supervisor.subprocess, "Popen", interruptible)
    with pytest.raises(KeyboardInterrupt):
        supervisor.invoke_json_worker(
            command("child", pidfile),
            {},
            cwd=tmp_path,
            limits=limits(),
            session_deadline=monotonic() + 15,
            index=1,
        )
    assert pidfile.is_file()
    deadline = monotonic() + 2
    while process_running(int(pidfile.read_text())) and monotonic() < deadline:
        sleep(0.01)
    assert not process_running(int(pidfile.read_text()))


def test_source_drift_between_stages_prevents_second_worker(tmp_path, monkeypatch):
    root, req, auth, _, seen, worker = prepare(tmp_path, monkeypatch)
    source = root / req.sources[0].path
    original = source.read_bytes()

    def changed_source(*args, **kwargs):
        outcome = worker(*args, **kwargs)
        source.write_bytes(b"# changed after campaign entry\n")
        return outcome

    monkeypatch.setattr(campaign, "invoke_json_worker", changed_source)
    result = campaign.run_campaign(root, req, auth)
    assert result.status == "failed" and len(seen) == 1
    assert len(result.calls) == 2 and result.calls[-1].interruption == "transport-exception"
    assert result.results[0].audit is None
    with pytest.raises(ValueError):
        campaign.validate_campaign(root, req.campaign_id)
    source.write_bytes(original)
    assert campaign.validate_campaign(root, req.campaign_id) == result


def test_incomplete_io_journal_never_becomes_a_resumable_campaign(tmp_path, monkeypatch):
    root, req, auth, _, seen, _ = prepare(tmp_path, monkeypatch)
    write = campaign._write

    def disk_failure(path, data):
        if path.name == "call-1.json":
            raise OSError("synthetic full disk")
        return write(path, data)

    monkeypatch.setattr(campaign, "_write", disk_failure)
    with pytest.raises(OSError):
        campaign.run_campaign(root, req, auth)
    assert len(seen) == 1
    directory = root / ".factory/semantic-v4-campaigns" / req.campaign_id
    assert (directory / "attempt-1.json").exists() and not (directory / "report.json").exists()
    assert (root / ".factory/semantic-v4-campaign-claims" / f"{req.sha256}.json").exists()
    with pytest.raises(FileExistsError):
        campaign.run_campaign(root, req, auth)
