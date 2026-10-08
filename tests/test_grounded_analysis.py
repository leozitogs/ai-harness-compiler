"""Typed coverage/linkage and mocked provider execution, not semantic model evals."""

import copy
import hashlib
import json
from pathlib import Path

import httpx
import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.adapters.ollama import (
    GROUNDING_PROMPT,
    SYSTEM_PROMPT,
    OllamaSettings,
    OllamaUnderstandingModel,
    prompt_digest,
)
from ai_harness_compiler.cli import main
from ai_harness_compiler.grounding import analyze_project, extract_grounding
from ai_harness_compiler.model_sessions import make_plan, run_session, validate_session
from ai_harness_compiler.model_worker import execute as execute_worker
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.grounded_analysis import (
    GroundedAnalysisProposal,
    GroundedAnalysisSpec,
)
from ai_harness_compiler.models.model_session import (
    ModelIdentity,
    ProviderObservation,
    SessionSettings,
    WorkerRequest,
    WorkerResult,
)
from ai_harness_compiler.semantic_eval import FrozenCorpus

CORPUS = Path(__file__).resolve().parents[1] / "evals/understanding/v1"


def analysis_value(extraction, disposition="business-rule"):
    proposal = {"business_rules": [], "statements": [], "questions": []}
    rows = []
    for index, atom in enumerate(a for a in extraction.atoms if a.kind == "acceptance-criterion"):
        finding = {"id": f"finding-{index}", "source_refs": [atom.source_ref]}
        if disposition == "business-rule":
            finding.update(
                description=atom.quote,
                condition="Fixture condition",
                outcome="Fixture outcome",
                origin="extracted",
            )
            proposal["business_rules"].append(finding)
        elif disposition == "requirement":
            finding.update(text=atom.quote, subject="capability", status="declared")
            proposal["statements"].append(finding)
        else:
            finding.update(question="Which behavior is intended?", blocking=True)
            proposal["questions"].append(finding)
        rows.append(
            {
                "atom_id": atom.id,
                "disposition": disposition,
                "finding_ids": [finding["id"]],
                "note": "Fixture linkage only, not semantic support.",
            }
        )
    return {"proposal": proposal, "criterion_dispositions": rows}


@pytest.mark.parametrize("disposition", ["business-rule", "requirement", "needs-clarification"])
def test_complete_typed_analysis_is_not_semantic_approval(project, disposition):
    extraction = extract_grounding(project)
    analysis = GroundedAnalysisProposal.model_validate(analysis_value(extraction, disposition))
    spec = GroundedAnalysisSpec(extraction=extraction, analysis=analysis)
    assert len(spec.analysis.criterion_dispositions) == sum(
        a.kind == "acceptance-criterion" for a in extraction.atoms
    )
    assert spec.semantic_status == spec.model_qualification == "not-established"
    assert spec.understanding.review is None
    Draft202012Validator(spec.model_json_schema()).validate(spec.model_dump())
    assert GroundedAnalysisSpec.model_validate_json(spec.model_dump_json()) == spec


@pytest.mark.parametrize(
    "tamper",
    [
        "omit",
        "duplicate",
        "order",
        "wrong-atom",
        "wrong-finding",
        "duplicate-finding",
        "wrong-type",
        "semantic-pass",
    ],
)
def test_analysis_rejects_omissions_and_contradictory_dispositions(project, tamper):
    extraction = extract_grounding(project)
    value = {"extraction": extraction.model_dump(), "analysis": analysis_value(extraction)}
    rows = value["analysis"]["criterion_dispositions"]
    if tamper == "omit":
        rows.pop()
    elif tamper == "duplicate":
        rows.append(copy.deepcopy(rows[0]))
    elif tamper == "order":
        rows.reverse()
    elif tamper == "wrong-atom":
        rows[0]["atom_id"] = "atom-1"
    elif tamper == "wrong-finding":
        rows[0]["finding_ids"] = ["not-present"]
    elif tamper == "duplicate-finding":
        rows[0]["finding_ids"] *= 2
    elif tamper == "wrong-type":
        rows[0]["disposition"] = "requirement"
    else:
        value["semantic_status"] = "pass"
    with pytest.raises(ValidationError):
        GroundedAnalysisSpec.model_validate(value)


def test_nonblocking_question_cannot_account_for_unresolved_criterion(project):
    extraction = extract_grounding(project)
    analysis = analysis_value(extraction, "needs-clarification")
    analysis["proposal"]["questions"][0]["blocking"] = False
    with pytest.raises(ValidationError, match="blocking question"):
        GroundedAnalysisSpec.model_validate(
            {"extraction": extraction.model_dump(), "analysis": analysis}
        )


def test_quotes_cannot_account_for_a_different_identical_criterion(project):
    project.backlog[0].acceptance_criteria.append(project.backlog[0].acceptance_criteria[0])
    extraction = extract_grounding(project)
    analysis = analysis_value(extraction)
    analysis["criterion_dispositions"][-1]["finding_ids"] = ["finding-0"]
    with pytest.raises(ValidationError, match="quoted rule"):
        GroundedAnalysisSpec.model_validate(
            {"extraction": extraction.model_dump(), "analysis": analysis}
        )


def test_external_excluded_reference_cannot_support_domain_candidate():
    from ai_harness_compiler.intake import load_project

    extraction = extract_grounding(load_project(Path("examples/evidence-pack")))
    analysis = analysis_value(extraction)
    analysis["proposal"]["domain_candidates"] = [
        {
            "id": "external-domain",
            "domain": "unregistered",
            "rationale": "Fixture",
            "source_refs": [extraction.excluded_references[0].source_ref],
        }
    ]
    with pytest.raises(ValidationError, match="Excluded references"):
        GroundedAnalysisSpec.model_validate(
            {"extraction": extraction.model_dump(), "analysis": analysis}
        )


def test_model_receives_independent_snapshot_and_is_called_once(project):
    calls = []
    before = copy.deepcopy(project.model_dump())

    class MutatingModel:
        def analyze(self, extraction):
            calls.append(extraction)
            value = analysis_value(extraction, "requirement")
            extraction.atoms[0].quote = "Changed by provider"
            extraction.request.original_input.conception = "Changed by provider"
            return GroundedAnalysisProposal.model_validate(value)

    spec = analyze_project(project, MutatingModel())
    assert len(calls) == 1
    assert spec.extraction.request.original_input.model_dump() == project.model_dump() == before


def test_grounded_adapter_sends_atoms_without_tools_or_eval_answers(project):
    seen = []
    extraction = extract_grounding(project)

    def respond(wire):
        payload = json.loads(wire.content)
        seen.append(payload)
        assert payload["format"] == GroundedAnalysisProposal.model_json_schema()
        assert payload["messages"][0]["content"] == GROUNDING_PROMPT
        assert json.loads(payload["messages"][1]["content"]) == extraction.model_dump()
        assert "tools" not in payload and not payload["think"] and not payload["stream"]
        return httpx.Response(
            200,
            json={
                "done": True,
                "message": {
                    "content": json.dumps(analysis_value(extraction)),
                    "thinking": "PRIVATE",
                },
            },
        )

    model = OllamaUnderstandingModel(
        OllamaSettings(model="fixture"), transport=httpx.MockTransport(respond)
    )
    result = analyze_project(project, model)
    assert len(seen) == 1 and "PRIVATE" not in result.model_dump_json()


def test_grounded_adapter_input_limit_fails_before_provider_call(project):
    def forbidden(wire):
        raise AssertionError("Budget failure must precede provider I/O")

    model = OllamaUnderstandingModel(
        OllamaSettings(model="fixture", max_input_bytes=1), transport=httpx.MockTransport(forbidden)
    )
    with pytest.raises(ValueError, match="STUDY_INPUT_LIMIT"):
        analyze_project(project, model)


def fake_result(request):
    extraction = extract_grounding(request.request.original_input)
    grounded = GroundedAnalysisSpec(
        extraction=extraction,
        analysis=GroundedAnalysisProposal.model_validate(analysis_value(extraction)),
    )
    identity = ModelIdentity(
        requested_model=request.settings.model,
        model_sha256="a" * 64,
        parameters_sha256="b" * 64,
        quantization="fixture",
        family="fixture",
        model_size_bytes=1,
        provider_version="fixture",
        compiler_version="fixture",
        compiler_source_sha256="c" * 64,
        python_version="fixture",
        platform_system="fixture",
        observed_at="fixture",
        prompt_sha256=request.prompt_sha256,
    )
    return WorkerResult(
        status="completed",
        identity=identity,
        settings=request.settings,
        understanding=grounded.understanding,
        grounded_analysis=grounded,
        observation=ProviderObservation(
            returned_model=request.settings.model, response_sha256="d" * 64
        ),
    )


def grounded_plan():
    return make_plan(
        FrozenCorpus(CORPUS),
        SessionSettings(model="fixture", analysis_mode="grounded", max_attempts=1),
        prompt_digest("grounded"),
        ["dev-rules-a", "dev-rules-b"],
    )


@pytest.mark.parametrize(
    "tamper", ["missing-analysis", "baseline-analysis", "error-analysis", "wrong-proposal"]
)
def test_worker_cannot_claim_grounded_execution_inconsistently(tamper):
    plan = grounded_plan()
    from ai_harness_compiler.understanding import prepare_understanding

    request = WorkerRequest(
        settings=plan.settings,
        request=prepare_understanding(plan.cases[0].project),
        prompt_sha256=plan.prompt_sha256,
    )
    value = fake_result(request).model_dump()
    if tamper == "missing-analysis":
        value["grounded_analysis"] = None
    elif tamper == "baseline-analysis":
        value["settings"]["analysis_mode"] = "baseline"
    elif tamper == "error-analysis":
        value["status"] = "error"
        value["error_code"] = "fixture-error"
    else:
        value["understanding"]["proposal"]["business_rules"][0]["condition"] = "Changed"
    with pytest.raises(ValidationError):
        WorkerResult.model_validate(value)


def test_session_persists_verified_analysis_and_budget_not_run(tmp_path):
    class Executor:
        def execute(self, request, timeout):
            return fake_result(request)

    corpus = FrozenCorpus(CORPUS)
    report = run_session(grounded_plan(), tmp_path / "new", Executor())
    assert report.attempts_used == 1 and report.jobs[1].state == "not-run"
    assert report.jobs[0].generation.grounded_analysis
    assert report.jobs[0].evaluation.status != "pass"
    assert validate_session(corpus, tmp_path / "new/session.json") == report


@pytest.mark.parametrize("directory", ["ahc-021-live-session", "ahc-021-live-session-final"])
def test_old_session_journals_remain_readable(directory):
    report = validate_session(
        FrozenCorpus(CORPUS), Path("docs/evidence") / directory / "session.json"
    )
    assert report.plan.settings.analysis_mode == "baseline"
    assert report.jobs[0].generation.grounded_analysis is None


def test_baseline_prompt_and_candidate_digests_remain_compatible():
    assert prompt_digest("baseline") == hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest()
    plan = make_plan(
        FrozenCorpus(CORPUS),
        SessionSettings(model="fixture"),
        prompt_digest("baseline"),
        ["dev-rules-a"],
    )
    expected = {
        "model": "fixture",
        "model_sha256": None,
        "prompt_sha256": plan.prompt_sha256,
        "context_tokens": 8192,
        "output_tokens": 4096,
        "temperature": 0,
        "thinking": False,
    }
    assert plan.candidate_digest() == canonical_project_digest(expected)
    assert prompt_digest("grounded") != prompt_digest("baseline")
    with pytest.raises(ValueError):
        prompt_digest("not-registered")


def test_grounded_worker_rejects_baseline_prompt_before_io():
    from ai_harness_compiler.understanding import prepare_understanding

    plan = grounded_plan()
    request = WorkerRequest(
        settings=plan.settings,
        request=prepare_understanding(plan.cases[0].project),
        prompt_sha256=prompt_digest("baseline"),
    )
    assert execute_worker(request).error_code == "prompt-mismatch"


@pytest.mark.parametrize("fault", [None, "missing-disposition", "wrong-ref", "model-drift"])
def test_grounded_worker_with_mock_provider_and_metadata(monkeypatch, fault):
    from ai_harness_compiler.understanding import prepare_understanding

    plan = grounded_plan()
    worker_project = FrozenCorpus(CORPUS).case("development", "dev-compatible-rules").project
    request = WorkerRequest(
        settings=plan.settings,
        request=prepare_understanding(worker_project),
        prompt_sha256=plan.prompt_sha256,
    )
    real_client = httpx.Client
    calls = []

    def respond(wire):
        calls.append(wire.url.path)
        if wire.url.path == "/api/tags":
            return httpx.Response(
                200,
                json={
                    "models": [
                        {
                            "name": "fixture",
                            "digest": "a" * 64,
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
        assert payload["format"] == GroundedAnalysisProposal.model_json_schema()
        assert payload["messages"][0]["content"] == GROUNDING_PROMPT
        extraction = extract_grounding(worker_project)
        assert json.loads(payload["messages"][1]["content"]) == extraction.model_dump()
        value = analysis_value(extraction)
        if fault == "missing-disposition":
            value["criterion_dispositions"].pop()
        if fault == "wrong-ref":
            value["proposal"]["business_rules"][0]["source_refs"] = ["input-1"]
        return httpx.Response(
            200,
            json={
                "done": True,
                "model": "wrong" if fault == "model-drift" else "fixture",
                "message": {"content": json.dumps(value), "thinking": "PRIVATE"},
            },
        )

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: real_client(**{**kwargs, "transport": httpx.MockTransport(respond)}),
    )
    result = execute_worker(request)
    assert calls.count("/api/chat") == 1
    assert result.status == ("completed" if fault is None else "error")
    if fault == "missing-disposition":
        assert result.error_code == "criterion-inventory-invalid"
    elif fault == "wrong-ref":
        assert result.error_code == "grounded-analysis-invalid"
    if fault is None:
        assert result.grounded_analysis
        assert result.understanding.review is None
    assert "PRIVATE" not in result.model_dump_json()


def test_grounded_cli_selects_program_and_journals_without_approval(tmp_path, monkeypatch):
    from ai_harness_compiler.model_sessions import IsolatedOllamaExecutor

    monkeypatch.setattr(
        IsolatedOllamaExecutor, "execute", lambda self, request, timeout: fake_result(request)
    )
    result = main(
        [
            "run-understanding-evals",
            "--corpus",
            str(CORPUS),
            "--model",
            "fixture",
            "--analysis-mode",
            "grounded",
            "--case",
            "dev-rules-a",
            "--output",
            str(tmp_path / "new"),
        ]
    )
    assert result == 0
    report = validate_session(FrozenCorpus(CORPUS), tmp_path / "new/session.json")
    assert report.plan.settings.analysis_mode == "grounded"
    assert report.plan.rubric.approval is None
    assert report.model_qualification == "not-established"
