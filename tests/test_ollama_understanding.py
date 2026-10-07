"""Mock transport tests verify boundaries; they are not semantic model evals."""

import json

import httpx
import pytest
from pydantic import ValidationError

from ai_harness_compiler.adapters.ollama import OllamaSettings, OllamaUnderstandingModel
from ai_harness_compiler.cli import main
from ai_harness_compiler.models.understanding import UnderstandingProposal
from ai_harness_compiler.understanding import prepare_understanding, study_project


def proposal_for(project):
    ref = prepare_understanding(project).references[0]
    return {
        "statements": [
            {
                "id": "purpose",
                "subject": "purpose",
                "text": ref.value,
                "status": "declared",
                "source_refs": [ref.id],
            }
        ],
    }


def envelope(proposal):
    return {"done": True, "message": {"role": "assistant", "content": json.dumps(proposal)}}


def adapter(response, **settings):
    return OllamaUnderstandingModel(
        OllamaSettings(model="test-model:fixture", **settings),
        transport=httpx.MockTransport(lambda request: response),
    )


def test_real_adapter_protocol_and_proposed_state(project, monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://untrusted.example:1234")
    seen = []

    def respond(request):
        seen.append(request)
        payload = json.loads(request.content)
        assert str(request.url) == "http://127.0.0.1:11434/api/chat"
        assert request.method == "POST"
        assert payload["format"] == UnderstandingProposal.model_json_schema()
        assert payload["stream"] is False and payload["think"] is False
        assert "tools" not in payload
        assert payload["options"] == {"temperature": 0, "num_predict": 4096}
        assert (
            json.loads(payload["messages"][1]["content"])
            == prepare_understanding(project).model_dump()
        )
        return httpx.Response(200, json=envelope(proposal_for(project)))

    model = OllamaUnderstandingModel(
        OllamaSettings(model="test-model:fixture"), transport=httpx.MockTransport(respond)
    )
    result = study_project(project, model)
    assert len(seen) == 1
    assert result.review is None
    assert result.request.original_input == project


@pytest.mark.parametrize(
    "value,code",
    [
        ([], "STUDY_INCOMPLETE"),
        ({"done": False}, "STUDY_INCOMPLETE"),
        ({"done": True, "done_reason": "length"}, "STUDY_TRUNCATED"),
        ({"done": True, "message": []}, "STUDY_MESSAGE"),
        ({"done": True, "message": {"content": 1}}, "STUDY_MESSAGE"),
        ({"done": True, "message": {"tool_calls": [{}]}}, "STUDY_MESSAGE"),
        (envelope({}), "STUDY_INVALID"),
        (envelope({"review": "approved"}), "STUDY_INVALID"),
    ],
)
def test_invalid_envelopes(project, value, code):
    with pytest.raises(ValueError, match=code):
        study_project(project, adapter(httpx.Response(200, json=value)))


@pytest.mark.parametrize("raw", [b"not-json", b"\xff", b"[" * 2000])
def test_invalid_wire_json_is_sanitized(project, raw):
    with pytest.raises(ValueError, match="STUDY_INVALID"):
        study_project(project, adapter(httpx.Response(200, content=raw)))


@pytest.mark.parametrize("status", [302, 400, 404, 500])
def test_http_failure_no_redirect_or_retry(project, status):
    calls = []

    def fail(request):
        calls.append(request)
        return httpx.Response(status, headers={"location": "https://example.com"}, text="private")

    model = OllamaUnderstandingModel(
        OllamaSettings(model="fixture"), transport=httpx.MockTransport(fail)
    )
    with pytest.raises(ValueError, match="STUDY_PROVIDER") as error:
        study_project(project, model)
    assert "private" not in str(error.value)
    assert len(calls) == 1


@pytest.mark.parametrize("error", [httpx.ConnectError, httpx.ReadTimeout])
def test_network_error_sanitized(project, error):
    def fail(request):
        raise error("private provider error")

    model = OllamaUnderstandingModel(
        OllamaSettings(model="fixture"), transport=httpx.MockTransport(fail)
    )
    with pytest.raises(ValueError, match="STUDY_PROVIDER"):
        study_project(project, model)


@pytest.mark.parametrize(
    "limit,code",
    [
        ("max_input_bytes", "STUDY_INPUT_LIMIT"),
        ("max_response_bytes", "STUDY_RESPONSE_LIMIT"),
        ("max_proposal_bytes", "STUDY_PROPOSAL_LIMIT"),
    ],
)
def test_byte_limits(project, limit, code):
    with pytest.raises(ValueError, match=code):
        study_project(
            project,
            adapter(httpx.Response(200, json=envelope(proposal_for(project))), **{limit: 1}),
        )


@pytest.mark.parametrize(
    "settings",
    [
        {"model": ""},
        {"model": "http://host with space"},
        {"timeout_seconds": 0},
        {"timeout_seconds": True},
        {"timeout_seconds": 301},
        {"max_input_bytes": 1048577},
        {"max_response_bytes": -1},
        {"max_proposal_bytes": 1048577},
        {"max_output_tokens": 16385},
    ],
)
def test_config_bounds(settings):
    with pytest.raises(ValueError, match="STUDY_(MODEL|LIMIT)"):
        OllamaSettings(**({"model": "fixture"} | settings))


def test_deadline(project, monkeypatch):
    times = iter([0, 61])
    monkeypatch.setattr("ai_harness_compiler.adapters.ollama.monotonic", lambda: next(times))
    with pytest.raises(ValueError, match="STUDY_DEADLINE"):
        study_project(project, adapter(httpx.Response(200, json=envelope(proposal_for(project)))))


def test_core_rejects_unknown_reference_from_provider(project):
    value = proposal_for(project)
    value["statements"][0]["source_refs"] = ["foreign-ref"]
    with pytest.raises(ValidationError):
        study_project(project, adapter(httpx.Response(200, json=envelope(value))))


def test_provider_cannot_mutate_authoritative_snapshot(project):
    class MutatingFake:
        def propose(self, request):
            request.original_input.conception = "private injected conception"
            value = proposal_for(project)
            value["statements"][0]["text"] = "private injected conception"
            return UnderstandingProposal.model_validate(value)

    with pytest.raises(ValidationError):
        study_project(project, MutatingFake())
    assert project.conception != "private injected conception"


def test_study_cli_preserves_existing_file_before_model_call(tmp_path, monkeypatch):
    output = tmp_path / "existing.json"
    output.write_text("keep", encoding="utf-8")
    monkeypatch.setattr(OllamaUnderstandingModel, "propose", lambda *_: pytest.fail("No call"))
    assert main(["study", "absent.yaml", "--model", "fixture", "--output", str(output)]) == 1
    assert output.read_text(encoding="utf-8") == "keep"


def test_study_cli_success_with_test_fake(tmp_path, project, monkeypatch):
    output = tmp_path / "new.json"
    monkeypatch.setattr(
        OllamaUnderstandingModel,
        "propose",
        lambda *_: UnderstandingProposal.model_validate(proposal_for(project)),
    )
    assert (
        main(
            [
                "study",
                "examples/project-definition",
                "--model",
                "fixture",
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert json.loads(output.read_text(encoding="utf-8"))["review"] is None


def test_study_cli_failure_creates_no_artifact(tmp_path, monkeypatch):
    output = tmp_path / "new.json"

    def fail(*_):
        raise ValueError("STUDY_PROVIDER: unavailable")

    monkeypatch.setattr(OllamaUnderstandingModel, "propose", fail)
    assert (
        main(
            [
                "study",
                "examples/project-definition",
                "--model",
                "fixture",
                "--output",
                str(output),
            ]
        )
        == 1
    )
    assert not output.exists()
