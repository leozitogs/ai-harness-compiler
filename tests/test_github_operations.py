"""Fixed-host adapter and actual subprocess bounds, with every remote call replaced."""

import io
import json
import subprocess

import pytest
from pydantic import ValidationError
from test_scrum_operations import plan_for

from ai_harness_compiler.adapters import github_operations as module


def issue_json():
    return {
        "number": 1,
        "html_url": "https://github.com/owner/repo/issues/1",
        "node_id": "issue-1",
        "updated_at": "2026-10-19T12:00:00Z",
        "state": "open",
        "title": "Title",
        "body": "Untrusted PRIVATE body",
        "labels": [{"name": "existing"}],
        "milestone": None,
        "assignees": [],
    }


def test_issue_projection_hashes_text_without_storing_it(monkeypatch):
    calls = []

    def request(method, endpoint, timeout, payload=None):
        calls.append((method, endpoint, timeout, payload))
        return json.dumps(issue_json())

    monkeypatch.setattr(module, "_request", request)
    remote = module.GitHubOperationAdapter().read_issue("owner/repo", 1, 10)
    assert "PRIVATE" not in remote.model_dump_json()
    assert calls == [("GET", "repos/owner/repo/issues/1", 10, None)]


@pytest.mark.parametrize(
    "change",
    [
        {"number": 2},
        {"pull_request": {}},
        {"html_url": "https://github.com/other/repo/issues/1"},
        {"labels": [{"name": "x"}] * 300},
    ],
)
def test_issue_scope_and_payload_are_checked(monkeypatch, change):
    monkeypatch.setattr(module, "_request", lambda *args: json.dumps({**issue_json(), **change}))
    with pytest.raises((ValueError, ValidationError)):
        module.GitHubOperationAdapter().read_issue("owner/repo", 1, 10)


@pytest.mark.parametrize("change", [{"labels": [None]}, {"body": False}])
def test_malformed_metadata_is_a_sanitized_contract_error(monkeypatch, change):
    monkeypatch.setattr(module, "_request", lambda *args: json.dumps({**issue_json(), **change}))
    with pytest.raises(ValueError) as caught:
        module.GitHubOperationAdapter().read_issue("owner/repo", 1, 10)
    assert "PRIVATE" not in str(caught.value)


@pytest.mark.parametrize(
    "repo,number", [("owner/repo/../../else", 1), ("owner/repo", 0), ("owner/repo", True)]
)
def test_bad_scope_never_reaches_api(monkeypatch, repo, number):
    def fail(*args):
        pytest.fail("Invalid request reached network boundary")

    monkeypatch.setattr(module, "_request", fail)
    with pytest.raises((ValueError, ValidationError)):
        module.GitHubOperationAdapter().read_issue(repo, number, 10)


def test_additive_endpoint_and_final_guard_are_fixed(tmp_path, monkeypatch):
    plan = plan_for(tmp_path)
    calls = []
    guarded = []

    def request(method, endpoint, timeout, payload=None):
        if method == "POST":
            assert guarded == [True]
        calls.append((method, endpoint, payload))
        return json.dumps({"name": plan.label, "archived_at": None})

    monkeypatch.setattr(module, "_request", request)
    module.GitHubOperationAdapter().add_label(plan, 10, lambda: guarded.append(True))
    assert calls == [
        ("GET", "repos/owner/repo/labels/nexo%3Aneeds-refinement", None),
        ("POST", "repos/owner/repo/issues/1/labels", json.dumps({"labels": [plan.label]})),
    ]


@pytest.mark.parametrize(
    "response", [{"name": "wrong"}, {"name": "nexo:needs-refinement", "archived_at": "2026-01-01"}]
)
def test_missing_or_archived_label_does_not_write(tmp_path, monkeypatch, response):
    calls = []
    monkeypatch.setattr(
        module, "_request", lambda *args: calls.append(args) or json.dumps(response)
    )
    with pytest.raises(ValueError, match="absent or archived"):
        module.GitHubOperationAdapter().add_label(plan_for(tmp_path), 10, lambda: None)
    assert len(calls) == 1 and calls[0][0] == "GET"


def test_guard_failure_prevents_post(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(
        module,
        "_request",
        lambda *args: calls.append(args) or json.dumps({"name": "nexo:needs-refinement"}),
    )

    def expired():
        raise ValueError("Authorization expired")

    with pytest.raises(ValueError, match="expired"):
        module.GitHubOperationAdapter().add_label(plan_for(tmp_path), 10, expired)
    assert len(calls) == 1


@pytest.mark.parametrize("mode", ["normal", "oversize", "error", "timeout"])
def test_subprocess_host_payload_timeout_and_output_limits(monkeypatch, mode):
    calls = []

    class FakeProcess:
        def __init__(self, command, **kwargs):
            self.stdout = io.BytesIO(b"{}" if mode != "oversize" else b"x" * (256 * 1024 + 1))
            self.stdin = io.BytesIO()
            self.returncode = 1 if mode == "error" else 0
            calls.append((command, kwargs, self))

        def wait(self, timeout=None):
            if mode == "timeout" and timeout is not None:
                raise subprocess.TimeoutExpired("gh", timeout)
            return self.returncode

        def kill(self):
            self.returncode = -1

    monkeypatch.setattr(module.shutil, "which", lambda name: "C:/tools/gh.exe")
    monkeypatch.setattr(module.subprocess, "Popen", FakeProcess)
    if mode == "normal":
        assert (
            module._request("POST", "repos/owner/repo/issues/1/labels", 10, '{"labels":["x"]}')
            == "{}"
        )
    else:
        with pytest.raises(ValueError):
            module._request("POST", "repos/owner/repo/issues/1/labels", 10, '{"labels":["x"]}')
    command, kwargs, process = calls[0]
    assert command[:4] == ["C:/tools/gh.exe", "api", "--hostname", "github.com"]
    assert command[-2:] == ["--input", "-"]
    assert kwargs["stderr"] == subprocess.DEVNULL
    assert kwargs.get("shell", False) is False
