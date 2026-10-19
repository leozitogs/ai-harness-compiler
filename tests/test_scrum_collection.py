"""Read boundaries and CLI remain offline unless GitHub is explicitly selected."""

import io
import json
import subprocess

import pytest
from test_scrum_observer import REPO, fixture_observation

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.scrum import SprintSnapshot, StoryPRLink
from ai_harness_compiler.scrum_collection import GitHubCLIReader, collect
from ai_harness_compiler.scrum_observer import observe


def repository(tmp_path):
    observation = fixture_observation()
    for source in observation.sources[:5]:
        path = tmp_path / source.locator
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(source.content, encoding="utf-8")
    return tmp_path


class FakeReader:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def read(self, kind, repository, number, timeout_seconds):
        self.calls.append((kind, repository, number, timeout_seconds))
        if self.fail:
            raise ValueError("private provider detail must not be persisted")
        return next(
            s.content
            for s in fixture_observation().sources
            if s.kind == kind and s.number == number
        )


def test_collect_defaults_to_local_without_any_external_read(tmp_path):
    observation = collect(repository(tmp_path), "demo", REPO, "sprint-2-5")
    assert all(s.reason == "not-requested" for s in observation.sources if s.kind == "issue")
    assert observe(observation).declared_state == "closed_with_carryover"


def test_fake_adapter_preserves_observations_and_read_budget(tmp_path):
    reader = FakeReader()
    observation = collect(
        repository(tmp_path),
        "demo",
        REPO,
        "sprint-2-5",
        reader=reader,
        links=[StoryPRLink(story_id="alpha", number=40)],
        max_remote_reads=1,
    )
    assert len(reader.calls) == 1
    assert observation.sources[-1].reason == "limit-exceeded"
    report = observe(observation)
    assert report.stories[0].issue_state == "OPEN"
    assert report.stories[1].issue_state == "unknown"
    assert not report.stories[0].pull_requests


def test_shared_pr_is_fetched_once_but_linked_to_two_stories(tmp_path):
    reader = FakeReader()
    observation = collect(
        repository(tmp_path),
        "demo",
        REPO,
        "sprint-2-5",
        reader=reader,
        links=[StoryPRLink(story_id=s, number=40) for s in ["alpha", "beta"]],
    )
    assert len(reader.calls) == 3
    assert all(len(s.pull_requests) == 1 for s in observe(observation).stories)


def test_collection_failure_is_unknown_without_private_error_details(tmp_path):
    observation = collect(
        repository(tmp_path), "demo", REPO, "sprint-2-5", reader=FakeReader(fail=True)
    )
    assert all(s.issue_state == "unknown" for s in observe(observation).stories)
    assert "private provider detail" not in observation.model_dump_json()


@pytest.mark.parametrize(
    "mutation", ["wrong-project", "wrong-sprint", "wrong-repo", "duplicate-json"]
)
def test_invalid_scope_or_ambiguous_plan_does_not_trigger_network(tmp_path, mutation):
    root = repository(tmp_path)
    p = root / "planning/sprint-2-5.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    project_id = "other" if mutation == "wrong-project" else "demo"
    if mutation == "wrong-sprint":
        data["id"] = "sprint-3"
    if mutation == "wrong-repo":
        data["tracking"]["issues"]["alpha"]["url"] = "https://github.com/other/repo/issues/1"
    raw = json.dumps(data)
    if mutation == "duplicate-json":
        raw = '{"id":"sprint-4",' + raw[1:]
    p.write_text(raw, encoding="utf-8")
    reader = FakeReader()
    report = observe(collect(root, project_id, REPO, "sprint-2-5", reader=reader))
    assert reader.calls == []
    assert report.declared_state == "unknown"
    assert any(i.code == "planning-invalid" for i in report.impediments)


def test_oversize_source_is_not_silently_truncated(tmp_path):
    root = repository(tmp_path)
    (root / "docs/delivery/scrum.md").write_bytes(b"x" * (256 * 1024 + 1))
    observation = collect(root, "demo", REPO, "sprint-2-5")
    source = next(s for s in observation.sources if s.kind == "policy")
    assert source.reason == "limit-exceeded" and source.content is None


def test_session_deadline_stops_remote_reads_without_sleep(tmp_path, monkeypatch):
    import ai_harness_compiler.scrum_collection as module

    times = iter([0.0, 121.0, 122.0])
    monkeypatch.setattr(module, "monotonic", lambda: next(times))
    reader = FakeReader()
    observation = collect(repository(tmp_path), "demo", REPO, "sprint-2-5", reader=reader)
    assert not reader.calls
    assert all(s.reason == "limit-exceeded" for s in observation.sources if s.kind == "issue")


def test_plan_cannot_redirect_work_items_to_private_file(tmp_path):
    root = repository(tmp_path / "repo")
    secret = tmp_path / "secret.txt"
    secret.write_text("PRIVATE-CONTENT-NOT-FOR-COLLECTION", encoding="utf-8")
    path = root / "planning/sprint-2-5.json"
    plan = json.loads(path.read_text(encoding="utf-8"))
    plan["work_items_file"] = str(secret)
    path.write_text(json.dumps(plan), encoding="utf-8")
    observation = collect(root, "demo", REPO, "sprint-2-5")
    assert "PRIVATE-CONTENT-NOT-FOR-COLLECTION" not in observation.model_dump_json()
    assert (
        next(s for s in observation.sources if s.kind == "work-items").locator
        == "planning/sprint-2-5.work-items.json"
    )


@pytest.mark.parametrize(
    "sprint", ["../secret", "sprint-2/../secret", "sprint-0", "sprint-2-5-5-1"]
)
def test_path_like_sprint_rejected_before_file_reads(tmp_path, sprint):
    with pytest.raises(ValueError):
        collect(tmp_path, "demo", REPO, sprint)


def test_cli_observe_and_no_overwrite(tmp_path):
    root = repository(tmp_path)
    output = tmp_path / "snapshot.json"
    args = [
        "scrum",
        "observe",
        str(root),
        "--project-id",
        "demo",
        "--repo",
        REPO,
        "--sprint",
        "sprint-2-5",
        "--output",
        str(output),
    ]
    assert main(args) == 0
    assert SprintSnapshot.model_validate_json(output.read_bytes()).completion_authority == "none"
    original = output.read_bytes()
    assert main(args) == 1
    assert output.read_bytes() == original


def test_cli_reconcile_ages_sources_without_network(tmp_path, monkeypatch):
    import ai_harness_compiler.scrum_cli as module

    original = observe(fixture_observation())
    source = tmp_path / "old.json"
    source.write_text(original.model_dump_json(), encoding="utf-8")
    output = tmp_path / "new.json"
    monkeypatch.setattr(module, "timestamp", lambda: "2026-10-21T12:00:00+00:00")
    assert main(["scrum", "reconcile", str(source), "--output", str(output)]) == 0
    refreshed = SprintSnapshot.model_validate_json(output.read_bytes())
    assert refreshed.declared_state == "unknown"
    assert any(i.code == "source-stale" for i in refreshed.impediments)
    assert refreshed.observation_sha256 != original.observation_sha256


@pytest.mark.parametrize("mode", ["success", "oversize", "error", "timeout"])
def test_gh_boundary_uses_only_fixed_reads_and_bounded_output(monkeypatch, mode):
    import ai_harness_compiler.scrum_collection as module

    seen = []

    class Process:
        def __init__(self, args, **kwargs):
            seen.append((args, kwargs))
            self.returncode = 0
            self.stdout = io.BytesIO(b"x" * (256 * 1024 + 1) if mode == "oversize" else b"{}")
            self.killed = False

        def kill(self):
            self.killed = True
            self.returncode = -9

        def wait(self, timeout=None):
            if mode == "timeout" and not self.killed:
                raise subprocess.TimeoutExpired("gh", timeout)
            if mode == "error":
                self.returncode = 1
            return self.returncode

    monkeypatch.setattr(module.shutil, "which", lambda command: "gh-test")
    monkeypatch.setattr(module.subprocess, "Popen", Process)
    reader = GitHubCLIReader()
    if mode == "success":
        assert reader.read("issue", REPO, 1, 5) == "{}"
    else:
        with pytest.raises(ValueError):
            reader.read("issue", REPO, 1, 5)
    args, kwargs = seen[0]
    assert args == [
        "gh-test",
        "issue",
        "view",
        "https://github.com/owner/repo/issues/1",
        "--json",
        "number,url,state,updatedAt",
    ]
    assert kwargs["stdin"] == subprocess.DEVNULL and kwargs["stderr"] == subprocess.DEVNULL


def test_snapshot_revalidates_mutated_nested_evidence():
    observation = fixture_observation()
    observation.sources[0].__dict__["content"] = "tampered nested instance"
    with pytest.raises(ValueError):
        observe(observation)
