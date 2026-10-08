"""Budget/history tests with fixtures; no claims of model or semantic performance."""

import copy
import json
from pathlib import Path

import httpx
import pytest
from pydantic import ValidationError
from test_grounded_analysis import analysis_value, fake_result

from ai_harness_compiler.adapters.ollama import (
    REPAIR_PROMPT,
    OllamaSettings,
    OllamaUnderstandingModel,
    prompt_digest,
)
from ai_harness_compiler.cli import main
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.model_sessions import IsolatedOllamaExecutor, make_plan
from ai_harness_compiler.models.grounded_analysis import GroundedRepairInput, GroundingDiagnostic
from ai_harness_compiler.models.model_session import SessionSettings, WorkerRequest, WorkerResult
from ai_harness_compiler.models.repair import RepairPlan, RepairReport
from ai_harness_compiler.repairs import run_repair, validate_repair
from ai_harness_compiler.semantic_eval import FrozenCorpus

CORPUS = Path(__file__).resolve().parents[1] / "evals/understanding/v1"


def plan(max_repairs=1, **settings):
    session = make_plan(
        FrozenCorpus(CORPUS),
        SessionSettings(
            model="fixture", analysis_mode="grounded", expected_model_sha256="a" * 64, **settings
        ),
        prompt_digest("grounded"),
        ["dev-compatible-rules"],
    )
    return RepairPlan(
        session=session, max_repairs=max_repairs, repair_prompt_sha256=prompt_digest("repair")
    )


def diagnostic(request):
    extraction = extract_grounding(request.request.original_input)
    atom = next(a for a in extraction.atoms if a.kind == "acceptance-criterion")
    return GroundingDiagnostic(
        input_sha256=request.request.original_sha256,
        proposal_sha256="e" * 64,
        error_code="criterion-rule-link-invalid",
        atom_ids=[atom.id],
        reason="wrong-origin",
    )


class Executor:
    def __init__(self, always_fail=False, error=None):
        self.requests = []
        self.always_fail = always_fail
        self.error = error

    def execute(self, request, timeout):
        self.requests.append(copy.deepcopy(request))
        if self.error:
            return WorkerResult(status="error", error_code=self.error)
        if self.always_fail or len(self.requests) == 1:
            return WorkerResult(
                status="error",
                error_code="criterion-rule-link-invalid",
                failure_diagnostic=diagnostic(request),
            )
        return fake_result(request)


def test_repair_charges_each_call_and_binds_previous_diagnostic(tmp_path):
    executor = Executor()
    report = run_repair(plan(), tmp_path / "new", executor)
    assert report.termination == "completed" and len(report.attempts) == 2
    assert executor.requests[0].repair_feedback is None
    assert executor.requests[1].repair_feedback == report.attempts[0].result.failure_diagnostic
    assert executor.requests[1].prompt_sha256 == prompt_digest("repair")
    assert report.evaluation.status == "not-run" and report.evaluation.review is None
    assert report.model_qualification == "not-established"
    assert validate_repair(FrozenCorpus(CORPUS), tmp_path / "new") == report
    with pytest.raises(FileExistsError):
        run_repair(plan(), tmp_path / "new", Executor())


@pytest.mark.parametrize("max_repairs", [0, 1, 2])
def test_repair_limit_is_explicit_and_no_hidden_fourth_call(tmp_path, max_repairs):
    executor = Executor(always_fail=True)
    report = run_repair(plan(max_repairs=max_repairs), tmp_path / "new", executor)
    assert report.termination == "repair-limit"
    assert len(executor.requests) == len(report.attempts) == max_repairs + 1
    assert report.evaluation is None


def test_attempt_limit_skips_eligible_repair(tmp_path):
    executor = Executor()
    report = run_repair(plan(max_attempts=1), tmp_path / "new", executor)
    assert report.termination == "attempt-limit" and len(executor.requests) == 1
    assert report.attempts[0].result.failure_diagnostic


def test_time_limit_skips_eligible_repair_and_uses_remaining_allowance(tmp_path, monkeypatch):
    clock = [0.0]
    monkeypatch.setattr("ai_harness_compiler.repairs.monotonic", lambda: clock[0])

    class Timed(Executor):
        def execute(self, request, timeout):
            assert timeout == 1.0
            result = super().execute(request, timeout)
            clock[0] = 2.0
            return result

    executor = Timed()
    report = run_repair(plan(session_seconds=1), tmp_path / "new", executor)
    assert report.termination == "time-limit" and len(executor.requests) == 1


@pytest.mark.parametrize(
    "error,cause",
    [
        ("worker-timeout", "worker-timeout"),
        ("model-changed", "model-changed"),
        ("grounded-output-invalid", "not-repairable"),
        ("provider-call-error", "not-repairable"),
    ],
)
def test_nonrepairable_and_fatal_errors_never_retry(tmp_path, error, cause):
    executor = Executor(error=error)
    report = run_repair(plan(), tmp_path / "new", executor)
    assert report.termination == cause and len(executor.requests) == 1


@pytest.mark.parametrize(
    "tamper",
    [
        "omit",
        "feedback",
        "input",
        "program",
        "time",
        "timeout",
        "limit",
        "termination",
        "evaluation",
        "qualification",
        "reference-inventory",
        "overlap",
    ],
)
def test_repair_report_rejects_contradictory_history(tmp_path, tamper):
    value = run_repair(plan(), tmp_path / "new", Executor()).model_dump()
    if tamper == "omit":
        value["attempts"].pop(0)
    elif tamper == "feedback":
        value["attempts"][1]["request"]["repair_feedback"] = None
    elif tamper == "input":
        value["attempts"][1]["request"]["repair_feedback"]["input_sha256"] = "f" * 64
    elif tamper == "program":
        value["attempts"][1]["request"]["prompt_sha256"] = "f" * 64
    elif tamper == "time":
        value["attempts"][0]["elapsed_seconds"] = 1.0
        value["elapsed_seconds"] = 0.0
    elif tamper == "timeout":
        value["attempts"][0]["effective_timeout_seconds"] = 300.0
    elif tamper == "limit":
        value["plan"]["max_repairs"] = 0
    elif tamper == "termination":
        value["termination"] = "repair-limit"
    elif tamper == "evaluation":
        value["evaluation"] = None
    elif tamper == "reference-inventory":
        value["attempts"][0]["request"]["request"]["references"].pop()
    elif tamper == "overlap":
        value["elapsed_seconds"] = 2.0
        value["attempts"][0]["elapsed_seconds"] = 1.0
        value["attempts"][1]["started_after_seconds"] = 0.0
    else:
        value["model_qualification"] = "qualified"
    with pytest.raises(ValidationError):
        RepairReport.model_validate(value)


def test_invalid_failure_scope_is_sanitized_and_not_forwarded(tmp_path):
    class Invalid(Executor):
        def execute(self, request, timeout):
            result = super().execute(request, timeout)
            result.failure_diagnostic.atom_ids = ["atom-1"]
            return result

    executor = Invalid()
    report = run_repair(plan(), tmp_path / "new", executor)
    assert report.termination == "not-repairable" and len(executor.requests) == 1
    assert report.attempts[0].result.error_code == "worker-result-error"
    assert report.attempts[0].result.failure_diagnostic is None


def test_journal_attempt_tampering_is_rejected(tmp_path):
    run_repair(plan(), tmp_path / "new", Executor())
    path = tmp_path / "new/attempt-001.json"
    value = json.loads(path.read_text(encoding="utf-8"))
    value["result"]["failure_diagnostic"]["proposal_sha256"] = "f" * 64
    path.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(ValueError, match="attempt differs"):
        validate_repair(FrozenCorpus(CORPUS), tmp_path / "new")


@pytest.mark.parametrize("mutation", ["baseline", "digest", "repeats", "cases"])
def test_plan_refuses_unfixed_or_multi_case_scope(mutation):
    value = plan().model_dump()
    settings = value["session"]["settings"]
    if mutation == "baseline":
        settings["analysis_mode"] = "baseline"
    elif mutation == "digest":
        settings["expected_model_sha256"] = None
    elif mutation == "repeats":
        settings["repeats"] = 2
    else:
        value["session"]["cases"] = []
    with pytest.raises(ValidationError):
        RepairPlan.model_validate(value)


def test_feedback_is_fixed_codes_and_scoped_atoms_only(project):
    extraction = extract_grounding(project)
    request = WorkerRequest(
        settings=SessionSettings(model="fixture", analysis_mode="grounded"),
        request=extraction.request,
        prompt_sha256=prompt_digest("grounded"),
    )
    feedback = diagnostic(request)
    for changes in [
        {"reason": "PRIVATE"},
        {"reason": "quote-mismatch", "error_code": "criterion-inventory-invalid"},
        {"atom_ids": ["atom-1"]},
    ]:
        value = feedback.model_dump() | changes
        with pytest.raises(ValidationError):
            GroundedRepairInput.model_validate(
                {"extraction": extraction.model_dump(), "feedback": value}
            )


def test_adapter_repair_uses_only_validated_evidence_feedback(project):
    extraction = extract_grounding(project)
    request = WorkerRequest(
        settings=SessionSettings(model="fixture", analysis_mode="grounded"),
        request=extraction.request,
        prompt_sha256=prompt_digest("grounded"),
    )
    feedback = diagnostic(request)
    seen = []

    def respond(wire):
        payload = json.loads(wire.content)
        seen.append(payload)
        assert payload["messages"][0]["content"] == REPAIR_PROMPT
        assert (
            json.loads(payload["messages"][1]["content"])
            == GroundedRepairInput(extraction=extraction, feedback=feedback).model_dump()
        )
        assert "tools" not in payload and payload["think"] is False
        return httpx.Response(
            200, json={"done": True, "message": {"content": json.dumps(analysis_value(extraction))}}
        )

    model = OllamaUnderstandingModel(
        OllamaSettings(model="fixture"), transport=httpx.MockTransport(respond)
    )
    model.generate_grounded(extraction, feedback)
    assert len(seen) == 1


def test_cli_run_and_validate_repair_without_semantic_approval(tmp_path, monkeypatch):
    executor = Executor()
    monkeypatch.setattr(
        IsolatedOllamaExecutor,
        "execute",
        lambda self, request, timeout: executor.execute(request, timeout),
    )
    assert (
        main(
            [
                "run-understanding-repair",
                "--corpus",
                str(CORPUS),
                "--case",
                "dev-compatible-rules",
                "--model",
                "fixture",
                "--expected-model-sha256",
                "a" * 64,
                "--output",
                str(tmp_path / "new"),
            ]
        )
        == 0
    )
    assert (
        main(["validate-understanding-repair", str(tmp_path / "new"), "--corpus", str(CORPUS)]) == 0
    )
    assert len(executor.requests) == 2


def test_journal_rejects_unreported_attempt_file(tmp_path):
    run_repair(plan(), tmp_path / "new", Executor())
    (tmp_path / "new/attempt-003.json").write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError, match="unexpected"):
        validate_repair(FrozenCorpus(CORPUS), tmp_path / "new")


@pytest.mark.parametrize("fault", [None, "model-name", "model-digest"])
def test_worker_diagnostic_then_repair_with_mock_provider(monkeypatch, fault):
    from ai_harness_compiler.model_worker import execute
    from ai_harness_compiler.understanding import prepare_understanding

    planned = plan()
    extraction = extract_grounding(planned.session.cases[0].project)
    request = WorkerRequest(
        settings=planned.session.settings,
        request=prepare_understanding(planned.session.cases[0].project),
        prompt_sha256=planned.session.prompt_sha256,
    )
    chats = []
    tag_count = [0]
    real_client = httpx.Client

    def respond(wire):
        if wire.url.path == "/api/tags":
            tag_count[0] += 1
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "fixture",
                            "digest": ("b" if fault == "model-digest" and tag_count[0] > 1 else "a")
                            * 64,
                            "size": 1,
                            "details": {
                                "format": "gguf",
                                "family": "fixture",
                                "quantization_level": "fixture",
                            },
                        }
                    ]
                },
            )
        if wire.url.path == "/api/show":
            return httpx.Response(200, json={"parameters": "temperature 0", "system": "PRIVATE"})
        if wire.url.path == "/api/version":
            return httpx.Response(200, json={"version": "fixture"})
        payload = json.loads(wire.content)
        chats.append(payload)
        value = analysis_value(extraction)
        if len(chats) == 1:
            value["proposal"]["business_rules"][0]["origin"] = "hypothesis"
        return httpx.Response(
            200,
            json={
                "done": True,
                "model": "wrong" if fault == "model-name" else "fixture",
                "message": {"content": json.dumps(value), "thinking": "PRIVATE"},
            },
        )

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: real_client(**{**kwargs, "transport": httpx.MockTransport(respond)}),
    )
    failed = execute(request)
    if fault:
        assert failed.error_code == "model-changed" and failed.failure_diagnostic is None
        assert len(chats) == 1
        return
    assert failed.status == "error" and failed.failure_diagnostic.reason == "wrong-origin"
    retried = execute(
        WorkerRequest(
            settings=request.settings,
            request=request.request,
            prompt_sha256=prompt_digest("repair"),
            repair_feedback=failed.failure_diagnostic,
        )
    )
    assert retried.status == "completed" and len(chats) == 2
    assert (
        json.loads(chats[1]["messages"][1]["content"])["feedback"]
        == failed.failure_diagnostic.model_dump()
    )
    assert "PRIVATE" not in failed.model_dump_json() + retried.model_dump_json()
    assert retried.understanding.review is None


@pytest.mark.parametrize(
    "fault,code",
    [
        ("statement", "declared-quote-invalid"),
        ("rule", "extracted-quote-invalid"),
        ("reference", "proposal-reference-invalid"),
    ],
)
def test_quote_and_reference_feedback_does_not_persist_candidate_text(project, fault, code):
    from ai_harness_compiler.models.evidence import canonical_project_digest
    from ai_harness_compiler.models.grounded_analysis import (
        GroundedAnalysisProposal,
        GroundedAnalysisSpec,
        GroundingInvariantError,
    )

    extraction = extract_grounding(project)
    value = analysis_value(extraction, "requirement" if fault == "statement" else "business-rule")
    if fault == "statement":
        value["proposal"]["statements"][0]["text"] = "PRIVATE paraphrase"
    elif fault == "rule":
        value["proposal"]["business_rules"][0]["description"] = "PRIVATE paraphrase"
    else:
        value["proposal"]["business_rules"][0]["source_refs"] = ["private-unresolved-reference"]
    analysis = GroundedAnalysisProposal.model_validate(value)
    with pytest.raises(ValidationError) as caught:
        GroundedAnalysisSpec(extraction=extraction, analysis=analysis)
    invariant = next(
        error["ctx"]["error"]
        for error in caught.value.errors(include_input=False)
        if isinstance(error.get("ctx", {}).get("error"), GroundingInvariantError)
    )
    assert invariant.code == code
    feedback = GroundingDiagnostic(
        input_sha256=extraction.request.original_sha256,
        proposal_sha256=canonical_project_digest(analysis.model_dump()),
        error_code=invariant.code,
        atom_ids=invariant.atom_ids,
        source_ref_ids=invariant.source_ref_ids,
        reason=invariant.reason,
    )
    GroundedRepairInput(extraction=extraction, feedback=feedback)
    assert "PRIVATE" not in feedback.model_dump_json()
    assert "private-unresolved" not in feedback.model_dump_json()
