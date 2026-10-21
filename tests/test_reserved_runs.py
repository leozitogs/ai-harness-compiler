"""Entirely synthetic reserved workspaces and fake providers; never reads the real cases."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from test_reserved_evaluation import binding
from test_semantic_analysis_v3 import fixture_analysis
from test_semantic_assessment import fixtures
from test_semantic_assessment_v3 import inputs
from test_semantic_verification_v4 import advice

from ai_harness_compiler.cli import main
from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.reserved_evaluation import ReservedEvaluationProtocol
from ai_harness_compiler.models.reserved_run import (
    ReservedRunAuthorization,
    ReservedRunReport,
    ReservedRunRequest,
    ReservedSemanticAssessment,
    assess_reserved,
    relative_file,
)
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_eval import semantic_snapshot_digest
from ai_harness_compiler.reserved_runs import (
    CANDIDATE_SOURCES,
    RUNNER_SOURCES,
    run_reserved,
    sha256,
    validate_reserved_run,
)

ROOT = Path(__file__).resolve().parents[1]
PREPARATION = ROOT / "evals/understanding/v2/reserved-preparation"


@pytest.fixture
def workspace(tmp_path, project):
    original_case, rubric, _ = fixtures(project)
    scenarios = [
        "novel-intent",
        "contrasting-rules",
        "contrasting-rules",
        "ambiguous-process",
        "conflicting-sources",
        "compatible-rules",
        "unread-assets",
        "untrusted-instruction",
    ]
    cases, bindings, responses = [], [], []
    for i, scenario in enumerate(scenarios):
        data = original_case.model_dump()
        data.update(id=f"synthetic-case-{i}", expectations_approval=None)
        data["project"].update(id=f"synthetic-project-{i}", conception=f"Synthetic process {i}")
        case = AssessmentCase.model_validate(data)
        relative = f".factory/synthetic-cases/case-{i}.json"
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = case.model_dump_json().encode()
        path.write_bytes(raw)
        bindings.append(
            {
                "case_id": case.id,
                "project_id": case.project.id,
                "family_id": f"synthetic-family-{i}",
                "scenario": scenario,
                "artifact_path": relative,
                "artifact_sha256": sha256(raw),
                "case_sha256": case.snapshot_sha256,
                "input_sha256": canonical_project_digest(case.project.model_dump()),
                "semantic_sha256": semantic_snapshot_digest(case.project),
            }
        )
        analysis = fixture_analysis(case.project)
        responses.extend([analysis.proposal.model_dump_json(), json.dumps(advice(analysis))])
        cases.append(case)
    rubric_raw = rubric.model_dump_json().encode()
    (tmp_path / "rubric.json").write_bytes(rubric_raw)
    code = json.loads((PREPARATION / "candidate-code.json").read_bytes())
    profile = json.loads((PREPARATION / "requested-profile.json").read_bytes())
    candidate = json.loads((PREPARATION / "candidate.json").read_bytes())
    protocol = ReservedEvaluationProtocol.model_validate(
        {
            "id": "synthetic-protocol",
            "rubric_sha256": sha256(rubric_raw),
            "candidate_designer": "synthetic-designer",
            "curator": "synthetic-curator",
            "curator_exposure": "blind-declared",
            "candidate": candidate,
            "development": [binding("synthetic-development")],
            "reserved": bindings,
            "budget": {
                "max_calls": 16,
                "repetitions": 1,
                "max_call_seconds": 180,
                "max_session_seconds": 3600,
            },
        }
    )
    protocol.corpus_candidate_sha256 = protocol.candidate.sha256
    protocol.review = {
        "reviewer": "synthetic-po",
        "note": "Synthetic expectation fixture only",
        "corpus_sha256": protocol.corpus_sha256,
    }
    runner_sources = []
    for relative in sorted(CANDIDATE_SOURCES | RUNNER_SOURCES):
        source = (ROOT / relative).read_bytes()
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source)
        if relative in RUNNER_SOURCES:
            runner_sources.append({"path": relative, "sha256": sha256(source)})
    request = ReservedRunRequest(
        id="synthetic-run",
        protocol=protocol,
        profile=profile,
        candidate_code=code,
        runner_sources=runner_sources,
        rubric_path="rubric.json",
        output_path=".factory/reserved-v2-executions/synthetic-run",
    )
    authorization = ReservedRunAuthorization(
        reviewer="synthetic-po",
        note="Synthetic invocation authorization, never actual PO permission",
        request_sha256=request.sha256,
        authorized=True,
    )
    return tmp_path, request, authorization, cases, rubric, responses


class FakeGenerator:
    def __init__(self, responses):
        self.responses, self.calls = iter(responses), []

    def generate_json(self, prompt, schema):
        assert '"expected_behavior"' not in prompt
        assert '"expectations_approval"' not in prompt
        assert '"obligations"' not in prompt
        self.calls.append((prompt, schema))
        value = next(self.responses)
        if isinstance(value, Exception):
            raise value
        return value


def test_complete_synthetic_run_is_not_semantic_success(workspace):
    root, request, auth, cases, _, responses = workspace
    provider = FakeGenerator(responses)
    report = run_reserved(root, request, auth, generator_factory=lambda _: provider)
    assert len(provider.calls) == report.model_invocations_charged == 16
    assert report.state == "completed"
    assert report.semantic_status == report.model_qualification == "not-established"
    assert report.provider_calls_observed is None
    assert report.compilation_eligibility == "not-authorized"
    assert ReservedRunReport.model_validate_json(report.model_dump_json()) == report
    assert validate_reserved_run(root, root / request.output_path) == report
    output = root / request.output_path
    for case in cases:
        assert (output / f"cases/{case.id}.json").read_bytes() == (
            root / next(c.artifact_path for c in request.protocol.reserved if c.case_id == case.id)
        ).read_bytes()
    assert not any(case.expectations_approval for case in cases)


@pytest.mark.parametrize("failure", ["bad-json", "timeout", "provider"])
def test_failures_are_charged_preserved_and_never_retried(workspace, failure):
    root, request, auth, _, _, _ = workspace
    value = {
        "bad-json": "{invalid",
        "timeout": TimeoutError("private details"),
        "provider": ValueError("private details"),
    }[failure]
    provider = FakeGenerator([value])
    report = run_reserved(root, request, auth, generator_factory=lambda _: provider)
    assert report.model_invocations_charged == len(provider.calls) == 1
    assert report.jobs[0].state == "error"
    assert all(j.state == "not-run" for j in report.jobs[1:])
    assert report.state == "stopped"
    assert validate_reserved_run(root, root / request.output_path) == report
    inconsistent = report.model_dump()
    inconsistent["stop_reason"] = "unrelated-cause"
    with pytest.raises(ValidationError):
        ReservedRunReport.model_validate(inconsistent)
    folder = root / request.output_path / "job-001"
    assert (folder / "call-start.json").exists() and (folder / "call-finish.json").exists()
    assert "private details" not in (root / request.output_path / "session.json").read_text()
    if failure == "bad-json":
        assert (folder / "response.txt").read_text() == value


def test_invalid_authorization_opens_neither_sources_nor_cases(workspace, monkeypatch):
    root, request, auth, _, _, _ = workspace
    auth.request_sha256 = "0" * 64
    monkeypatch.setattr(
        "ai_harness_compiler.reserved_runs.bounded_read", lambda _: pytest.fail("Unauthorized read")
    )
    with pytest.raises(ValueError, match="AUTHORIZATION_STALE"):
        run_reserved(root, request, auth)
    assert not (root / ".factory/reserved-run-claims").exists()


def test_single_use_claim_prevents_retry_even_after_zero_call_preflight_failure(workspace):
    root, request, auth, _, _, _ = workspace
    path = root / request.protocol.reserved[-1].artifact_path
    original = path.read_bytes()
    path.write_bytes(b"{}")
    with pytest.raises(ValueError, match="PAYLOAD_PREFLIGHT_FAILED"):
        run_reserved(
            root, request, auth, generator_factory=lambda _: pytest.fail("Unexpected model")
        )
    preflight = json.loads((root / request.output_path / "preflight-error.json").read_bytes())
    assert preflight["model_invocations_charged"] == 0
    path.write_bytes(original)
    with pytest.raises(FileExistsError):
        run_reserved(root, request, auth)


def test_changed_source_blocks_before_payload_access(workspace):
    root, request, auth, _, _, _ = workspace
    path = root / request.runner_sources[0].path
    path.write_bytes(path.read_bytes() + b"\n# changed")
    with pytest.raises(ValueError, match="SOURCE_CHANGED"):
        run_reserved(root, request, auth)
    assert not (root / request.output_path).exists()


def test_renaming_output_invalidates_authorization(workspace):
    root, request, auth, _, _, _ = workspace
    data = request.model_dump()
    data["output_path"] += "-different"
    with pytest.raises(ValueError, match="AUTHORIZATION_STALE"):
        run_reserved(root, ReservedRunRequest.model_validate(data), auth)


@pytest.mark.parametrize(
    "path", ["../secret", "/absolute", "C:/secret", "a\\b", "a/../b", "a//b", "."]
)
def test_nonportable_or_escaping_paths_are_rejected(path):
    with pytest.raises(ValueError):
        relative_file(path)


def test_session_time_exhaustion_before_call_is_not_a_false_attempt(workspace, monkeypatch):
    root, request, auth, _, _, responses = workspace
    clock = [0.0]
    monkeypatch.setattr("ai_harness_compiler.reserved_runs.monotonic", lambda: clock[0])

    def factory(_):
        clock[0] = 3500.0
        return FakeGenerator(responses)

    report = run_reserved(root, request, auth, generator_factory=factory)
    assert report.model_invocations_charged == 0
    assert all(j.state == "not-run" for j in report.jobs)


@pytest.mark.parametrize("mutation", ["count", "state", "missing", "audit-binding", "late-success"])
def test_contradictory_reports_are_invalid(workspace, mutation):
    root, request, auth, _, _, responses = workspace
    provider = FakeGenerator(responses)
    data = run_reserved(root, request, auth, generator_factory=lambda _: provider).model_dump()
    if mutation == "count":
        data["model_invocations_charged"] = 0
    elif mutation == "state":
        data["state"] = "stopped"
    elif mutation == "missing":
        data["jobs"].pop()
    elif mutation == "audit-binding":
        data["jobs"][1]["analysis_sha256"] = "0" * 64
    else:
        data["elapsed_seconds"] = 3601.0
    with pytest.raises(ValidationError):
        ReservedRunReport.model_validate(data)


def test_preparation_cli_reads_only_metadata_and_public_sources(workspace, monkeypatch):
    root, request, _, _, _, _ = workspace
    request_path, output = root / "request.json", root / "prepared.json"
    request_path.write_text(request.model_dump_json())
    original = Path.open

    def guarded_open(path, mode="r", *args, **kwargs):
        assert "synthetic-cases" not in str(path), "Preparation opened private cases"
        return original(path, mode, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", guarded_open)
        assert (
            main(
                [
                    "prepare-reserved-run",
                    str(request_path),
                    "--repository",
                    str(root),
                    "--output",
                    str(output),
                ]
            )
            == 0
        )
    data = json.loads(output.read_bytes())
    assert data["execution_authorized"] is False and data["model_calls"] == 0


def test_external_expectation_approval_never_rewrites_original_case(workspace, project):
    _, request, _, _, _, _ = workspace
    case, rubric, analysis, review = inputs(project)
    case.expectations_approval = None
    review.case_sha256 = case.snapshot_sha256
    data = request.protocol.model_dump()
    target = data["reserved"][0]
    target.update(
        case_id=case.id,
        project_id=case.project.id,
        case_sha256=case.snapshot_sha256,
        input_sha256=canonical_project_digest(case.project.model_dump()),
        semantic_sha256=semantic_snapshot_digest(case.project),
    )
    data["review"] = None
    protocol = ReservedEvaluationProtocol.model_validate(data)
    protocol.review = {
        "reviewer": "synthetic-po",
        "note": "Synthetic expectation approval",
        "corpus_sha256": protocol.corpus_sha256,
    }
    before = case.snapshot_sha256
    rubric_raw = rubric.model_dump_json().encode()
    pending = assess_reserved(protocol, case, rubric, analysis, rubric_raw)
    assert pending.status == "not-run"
    result = assess_reserved(protocol, case, rubric, analysis, rubric_raw, review)
    assert result.status == "pass" and result.original_assessment.status == "not-run"
    assert result.original_assessment.case_sha256 == before == case.snapshot_sha256
    assert result.original_assessment.case.expectations_approval is None
    assert result.compilation_eligibility == "not-authorized"
    assert ReservedSemanticAssessment.model_validate_json(result.model_dump_json()) == result
    changed = copy.deepcopy(result.model_dump())
    changed["original_assessment"]["case_sha256"] = "0" * 64
    with pytest.raises(ValidationError):
        ReservedSemanticAssessment.model_validate(changed)
    # Even mutually coherent parsed rubric/review hashes cannot contradict frozen raw bytes.
    changed = copy.deepcopy(result.model_dump())
    base = changed["original_assessment"]
    base["rubric"]["criteria"][0]["description"] = "Tampered criterion"
    base["rubric_sha256"] = canonical_project_digest(base["rubric"])
    base["review"]["rubric_sha256"] = base["rubric_sha256"]
    with pytest.raises(ValidationError, match="rubric bytes contradict"):
        ReservedSemanticAssessment.model_validate(changed)


@pytest.mark.parametrize("mutation", ["response", "schema", "unaccounted-call"])
def test_replay_rejects_cross_artifact_contradictions(workspace, mutation):
    root, request, auth, _, _, responses = workspace
    provider = FakeGenerator(responses)
    report = run_reserved(root, request, auth, generator_factory=lambda _: provider)
    folder = root / request.output_path / "job-001"
    if mutation == "response":
        data = json.loads((folder / "response.txt").read_bytes())
        data["criteria"][0]["note"] = "Changed response with otherwise coherent hashes"
        raw = json.dumps(data).encode()
        (folder / "response.txt").write_bytes(raw)
        session = report.model_dump()
        session["jobs"][0]["response_sha256"] = sha256(raw)
        (root / request.output_path / "session.json").write_text(json_text(session))
        (folder / "job.json").write_text(json_text(session["jobs"][0]))
        finish = json.loads((folder / "call-finish.json").read_bytes())
        finish["response_sha256"] = sha256(raw)
        (folder / "call-finish.json").write_text(json_text(finish))
    elif mutation == "schema":
        for name in ("call-start.json", "call-finish.json"):
            data = json.loads((folder / name).read_bytes())
            data["effective_schema_sha256"] = "0" * 64
            (folder / name).write_text(json_text(data))
    else:
        extra = root / request.output_path / "job-999"
        extra.mkdir()
        (extra / "call-start.json").write_text("{}")
    with pytest.raises(ValueError, match="CONTRADICTION|UNACCOUNTED"):
        validate_reserved_run(root, root / request.output_path)


def test_factory_failure_is_persisted_without_false_charge(workspace):
    root, request, auth, _, _, _ = workspace

    def factory(_):
        raise RuntimeError("private details")

    report = run_reserved(root, request, auth, generator_factory=factory)
    assert report.state == "stopped" and report.model_invocations_charged == 0
    assert all(job.state == "not-run" for job in report.jobs)


def test_missing_output_judgment_cli_stays_not_run(workspace):
    root, request, auth, cases, _, responses = workspace
    provider = FakeGenerator(responses)
    run_reserved(root, request, auth, generator_factory=lambda _: provider)
    folder = root / request.output_path
    target = folder / "pending-assessment.json"
    assert (
        main(
            [
                "assess-reserved-analysis",
                str(folder),
                "--repository",
                str(root),
                "--case-id",
                cases[0].id,
                "--output",
                str(target),
            ]
        )
        == 1
    )
    assessment = ReservedSemanticAssessment.model_validate_json(target.read_bytes())
    assert assessment.status == "not-run"
    assert assessment.original_assessment.case.expectations_approval is None


def test_changed_budget_requires_new_authorization(workspace):
    root, request, auth, _, _, _ = workspace
    data = request.model_dump()
    data["protocol"]["budget"].update(max_calls=32, repetitions=2)
    changed = ReservedRunRequest.model_validate(data)
    assert changed.protocol.corpus_sha256 == request.protocol.corpus_sha256
    with pytest.raises(ValueError, match="AUTHORIZATION_STALE"):
        run_reserved(root, changed, auth)


def test_failed_audit_factory_is_an_uncharged_unexecuted_stage(workspace):
    root, request, auth, _, _, responses = workspace
    provider = FakeGenerator(responses)
    constructed = [0]

    def factory(_):
        constructed[0] += 1
        if constructed[0] > 1:
            raise RuntimeError("provider unavailable")
        return provider

    report = run_reserved(root, request, auth, generator_factory=factory)
    assert report.jobs[0].state == "completed"
    assert report.jobs[1].state == "not-run"
    assert report.model_invocations_charged == 1
    assert validate_reserved_run(root, root / request.output_path) == report


@pytest.mark.parametrize("actor", ["synthetic-designer", "synthetic-curator", "gpt-6.1-sol"])
def test_producer_actor_cannot_declare_run_authorization(workspace, actor):
    root, request, auth, _, _, _ = workspace
    auth.reviewer = actor
    with pytest.raises(ValueError, match="REQUIRES_HUMAN"):
        run_reserved(root, request, auth)


def test_recorded_late_call_remains_error_not_success(workspace, monkeypatch):
    root, request, auth, _, _, responses = workspace
    clock = [0.0]
    monkeypatch.setattr("ai_harness_compiler.reserved_runs.monotonic", lambda: clock[0])

    class LateGenerator(FakeGenerator):
        def generate_json(self, prompt, schema):
            value = super().generate_json(prompt, schema)
            clock[0] += 181.0
            return value

    provider = LateGenerator(responses)
    report = run_reserved(root, request, auth, generator_factory=lambda _: provider)
    assert report.jobs[0].state == "error"
    assert report.jobs[0].response_sha256 is not None
    assert report.model_invocations_charged == 1 and report.state == "stopped"
    assert report.stop_reason == "call-time-limit-no-retry"
