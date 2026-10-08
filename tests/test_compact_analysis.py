"""Compact protocol tests establish literal assembly, never model semantic success."""

import copy
import json
from pathlib import Path

import httpx
import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError
from test_grounded_analysis import fake_result

from ai_harness_compiler.adapters.ollama import (
    COMPACT_PROMPT,
    OllamaSettings,
    OllamaUnderstandingModel,
    compact_response_schema,
    prompt_digest,
)
from ai_harness_compiler.cli import main
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.model_sessions import (
    IsolatedOllamaExecutor,
    make_plan,
    run_session,
    validate_session,
)
from ai_harness_compiler.models.compact_analysis import (
    CompactAnalysisSpec,
    CompactProposal,
    compact_input,
)
from ai_harness_compiler.models.model_session import SessionSettings, WorkerResult
from ai_harness_compiler.semantic_eval import FrozenCorpus

CORPUS = Path(__file__).resolve().parents[1] / "evals/understanding/v1"


def test_conflict_can_bind_branding_and_acceptance_criterion():
    case = FrozenCorpus(CORPUS).case("development", "dev-branding-conflict")
    extraction = extract_grounding(case.project)
    packet = compact_input(extraction)
    brand = next(
        i for i, c in enumerate(packet.context) if c.source_path == "/branding/principles/0"
    )
    criterion = next(i for i, c in enumerate(packet.context) if c.kind == "acceptance-criterion")
    data = value(extraction)
    data["issues"] = [
        {
            "kind": "conflict",
            "text": "Approval declarations conflict",
            "context_indices": [brand, criterion],
        }
    ]
    spec = CompactAnalysisSpec(
        extraction=extraction, interpretation=CompactProposal.model_validate(data)
    )
    assert spec.understanding.proposal.conflicts[0].source_refs == ["input-2", "input-5"]
    assert spec.semantic_status == "not-established"
    assert packet.context[criterion].text == packet.criteria[0]


def test_context_paths_preserve_numeric_constraint_meaning_and_old_positions():
    case = FrozenCorpus(CORPUS).case("development", "dev-branding-conflict")
    extraction = extract_grounding(case.project)
    packet = compact_input(extraction)
    original = [
        a for a in extraction.atoms if a.kind not in {"acceptance-criterion", "asset-metadata"}
    ]
    assert [c.text for c in packet.context[: len(original)]] == [a.quote for a in original]
    cost = next(c for c in packet.context if c.source_path == "/constraints/max_build_cost_usd")
    assert cost.text == "0.0"


def value(extraction, kind="business-rule"):
    count = len(compact_input(extraction).criteria)
    criteria = []
    for _ in range(count):
        item = {"kind": kind, "note": "Fixture classification, not semantic evidence"}
        if kind == "business-rule":
            item.update(condition="Fixture condition", outcome="Fixture outcome")
        elif kind == "needs-clarification":
            item["question"] = "Which behavior is intended?"
        criteria.append(item)
    return {
        "criteria": criteria,
        "context_findings": [
            {
                "subject": "domain",
                "text": "unregistered-domain",
                "note": "Fixture hypothesis",
                "context_indices": [0],
            }
        ],
        "issues": [],
    }


@pytest.mark.parametrize("kind", ["business-rule", "requirement", "needs-clarification"])
def test_compiler_owns_literal_quotes_and_keeps_inference_hypothetical(project, kind):
    extraction = extract_grounding(project)
    spec = CompactAnalysisSpec(
        extraction=extraction,
        interpretation=CompactProposal.model_validate(value(extraction, kind)),
    )
    criteria = [a for a in extraction.atoms if a.kind == "acceptance-criterion"]
    proposal = spec.understanding.proposal
    items = (
        proposal.business_rules
        if kind == "business-rule"
        else proposal.statements
        if kind == "requirement"
        else proposal.questions
    )
    assert [i.id for i in items] == [f"criterion-{n}" for n in range(1, len(criteria) + 1)]
    assert [i.source_refs for i in items] == [[a.source_ref] for a in criteria]
    if kind == "business-rule":
        assert [r.description for r in items] == [a.quote for a in criteria]
        assert all(r.origin == "hypothesis" for r in items)
    if kind == "requirement":
        assert [s.text for s in items] == [a.quote for a in criteria]
    assert proposal.domain_candidates[0].confidence is None
    assert spec.understanding.review is None
    assert spec.semantic_status == spec.model_qualification == "not-established"
    Draft202012Validator(spec.model_json_schema()).validate(spec.model_dump())
    assert CompactAnalysisSpec.model_validate_json(spec.model_dump_json()) == spec


def test_packet_has_no_snapshot_duplication_assets_or_external_claims():
    from ai_harness_compiler.intake import load_project

    project = load_project(Path("examples/evidence-pack"))
    extraction = extract_grounding(project)
    packet = compact_input(extraction)
    assert len(packet.model_dump_json().encode()) < len(extraction.model_dump_json().encode())
    assert not {"original_input", "references", "atoms"} & packet.model_dump().keys()
    assert all(c.kind != "asset-metadata" for c in packet.context)
    for claim in project.evidence_pack.evidence:
        assert claim.claim not in packet.model_dump_json()


@pytest.mark.parametrize(
    "change",
    [
        "missing",
        "extra",
        "negative-index",
        "out-of-range",
        "duplicate-index",
        "same-source-conflict",
        "confidence",
        "promotion",
    ],
)
def test_compact_contract_rejects_invalid_interpretation_scope(project, change):
    extraction = extract_grounding(project)
    data = {"extraction": extraction.model_dump(), "interpretation": value(extraction)}
    if change == "missing":
        data["interpretation"]["criteria"].pop()
    elif change == "extra":
        data["interpretation"]["criteria"].append(
            copy.deepcopy(data["interpretation"]["criteria"][0])
        )
    elif change == "confidence":
        data["interpretation"]["context_findings"][0]["confidence"] = 0.99
    elif change == "promotion":
        data["semantic_status"] = "pass"
    elif change == "same-source-conflict":
        data["interpretation"]["issues"] = [
            {"kind": "conflict", "text": "Fixture", "context_indices": [0]}
        ]
    else:
        data["interpretation"]["context_findings"][0]["context_indices"] = {
            "negative-index": [-1],
            "out-of-range": [511],
            "duplicate-index": [0, 0],
        }[change]
    with pytest.raises(ValidationError):
        CompactAnalysisSpec.model_validate(data)


def test_uncertainty_requires_confirmation_without_promoting_rule(project):
    extraction = extract_grounding(project)
    proposed = value(extraction)
    proposed["criteria"][0]["uncertainties"] = ["Condition is inferred"]
    spec = CompactAnalysisSpec(
        extraction=extraction, interpretation=CompactProposal.model_validate(proposed)
    )
    assert spec.understanding.proposal.questions[0].blocking is True
    assert spec.understanding.proposal.business_rules[0].origin == "hypothesis"


@pytest.mark.parametrize("mutation", ["quote", "interpretation"])
def test_projection_revalidates_nested_mutations(project, mutation):
    extraction = extract_grounding(project)
    spec = CompactAnalysisSpec(
        extraction=extraction, interpretation=CompactProposal.model_validate(value(extraction))
    )
    if mutation == "quote":
        next(
            a for a in spec.extraction.atoms if a.kind == "acceptance-criterion"
        ).quote = "Altered source"
    else:
        spec.interpretation.criteria.pop()
    with pytest.raises(ValueError):
        _ = spec.understanding


def test_dynamic_response_schema_binds_dimensions_without_mutating_generic_schema():
    original = CompactProposal.model_json_schema()
    first = compact_response_schema(4, 16)
    second = compact_response_schema(1, 3)
    assert (
        first["properties"]["criteria"]["minItems"]
        == first["properties"]["criteria"]["maxItems"]
        == 4
    )
    assert second["properties"]["criteria"]["maxItems"] == 1
    assert first["$defs"]["ContextIssue"]["properties"]["context_indices"]["items"]["maximum"] == 15
    assert CompactProposal.model_json_schema() == original
    with pytest.raises(ValueError):
        compact_response_schema(65, 1)


def test_adapter_uses_compact_payload_and_bounded_schema(project):
    extraction = extract_grounding(project)
    packet = compact_input(extraction)
    seen = []

    def respond(wire):
        payload = json.loads(wire.content)
        seen.append(payload)
        assert payload["format"] == compact_response_schema(
            len(packet.criteria), len(packet.context)
        )
        assert payload["messages"][0]["content"] == COMPACT_PROMPT
        assert json.loads(payload["messages"][1]["content"]) == packet.model_dump()
        assert "tools" not in payload and payload["think"] is False
        return httpx.Response(
            200,
            json={
                "done": True,
                "message": {"content": json.dumps(value(extraction)), "thinking": "PRIVATE"},
            },
        )

    model = OllamaUnderstandingModel(
        OllamaSettings(model="fixture"), transport=httpx.MockTransport(respond)
    )
    interpretation, observation = model.generate_compact(extraction)
    assert len(seen) == 1 and "PRIVATE" not in interpretation.model_dump_json()
    assert observation.response_sha256


def result(request):
    legacy_request = request.model_copy(deep=True)
    legacy_request.settings.analysis_mode = "grounded"
    legacy = fake_result(legacy_request)
    extraction = extract_grounding(request.request.original_input)
    compact = CompactAnalysisSpec(
        extraction=extraction, interpretation=CompactProposal.model_validate(value(extraction))
    )
    return WorkerResult(
        status="completed",
        identity=legacy.identity,
        settings=request.settings,
        observation=legacy.observation,
        understanding=compact.understanding,
        compact_analysis=compact,
    )


def planned():
    return make_plan(
        FrozenCorpus(CORPUS),
        SessionSettings(model="fixture", analysis_mode="compact", max_attempts=1),
        prompt_digest("compact"),
        ["dev-compatible-rules", "dev-new-domain"],
    )


def test_supervised_session_records_compact_interpretation_and_pending_review(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(
        IsolatedOllamaExecutor, "execute", lambda self, request, timeout: result(request)
    )
    report = run_session(planned(), tmp_path / "new", IsolatedOllamaExecutor())
    assert report.attempts_used == 1 and report.jobs[1].state == "not-run"
    assert report.jobs[0].generation.compact_analysis
    assert report.jobs[0].evaluation.status == "not-run"
    assert validate_session(FrozenCorpus(CORPUS), tmp_path / "new/session.json") == report


@pytest.mark.parametrize("tamper", ["missing", "wrong-mode", "different-projection"])
def test_worker_result_binds_compact_record_to_actual_projection(tamper):
    from ai_harness_compiler.models.model_session import WorkerRequest
    from ai_harness_compiler.understanding import prepare_understanding

    p = planned()
    request = WorkerRequest(
        settings=p.settings,
        request=prepare_understanding(p.cases[0].project),
        prompt_sha256=p.prompt_sha256,
    )
    data = result(request).model_dump()
    if tamper == "missing":
        data["compact_analysis"] = None
    elif tamper == "wrong-mode":
        data["settings"]["analysis_mode"] = "baseline"
    else:
        data["understanding"]["proposal"]["business_rules"][0]["condition"] = "Changed"
    with pytest.raises(ValidationError):
        WorkerResult.model_validate(data)


def test_compact_cli_is_opt_in_and_does_not_qualify(tmp_path, monkeypatch):
    monkeypatch.setattr(
        IsolatedOllamaExecutor, "execute", lambda self, request, timeout: result(request)
    )
    assert (
        main(
            [
                "run-understanding-evals",
                "--corpus",
                str(CORPUS),
                "--model",
                "fixture",
                "--analysis-mode",
                "compact",
                "--case",
                "dev-compatible-rules",
                "--output",
                str(tmp_path / "new"),
            ]
        )
        == 0
    )
    assert (
        validate_session(FrozenCorpus(CORPUS), tmp_path / "new/session.json").model_qualification
        == "not-established"
    )


@pytest.mark.parametrize("fault", [None, "dimensions", "model-name"])
def test_real_worker_compact_path_with_mock_transport(monkeypatch, fault):
    from ai_harness_compiler.model_worker import execute
    from ai_harness_compiler.models.model_session import WorkerRequest
    from ai_harness_compiler.understanding import prepare_understanding

    plan = planned()
    extraction = extract_grounding(plan.cases[0].project)
    request = WorkerRequest(
        settings=plan.settings,
        request=prepare_understanding(plan.cases[0].project),
        prompt_sha256=plan.prompt_sha256,
    )
    real_client = httpx.Client
    chats = []

    def respond(wire):
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
        chats.append(payload)
        proposed = value(extraction)
        if fault == "dimensions":
            proposed["criteria"].pop()
        return httpx.Response(
            200,
            json={
                "done": True,
                "model": "wrong" if fault == "model-name" else "fixture",
                "message": {"content": json.dumps(proposed), "thinking": "PRIVATE"},
            },
        )

    monkeypatch.setattr(
        httpx,
        "Client",
        lambda **kwargs: real_client(**{**kwargs, "transport": httpx.MockTransport(respond)}),
    )
    response = execute(request)
    assert response.status == ("completed" if fault is None else "error")
    assert len(chats) == 1 and "PRIVATE" not in response.model_dump_json()
    if fault is None:
        assert response.compact_analysis and not response.grounded_analysis
        assert all(r.origin == "hypothesis" for r in response.understanding.proposal.business_rules)
