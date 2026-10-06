import argparse
import hashlib
import json
import sqlite3
from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.memory.store import MemoryStore
from ai_harness_compiler.models.memory import RecordDraft


@pytest.fixture
def store(tmp_path):
    (tmp_path / "evidence.txt").write_text("regression observed and passed", encoding="utf-8")
    return MemoryStore(tmp_path)


@pytest.fixture
def draft(store):
    return RecordDraft.model_validate(
        {
            "id": "LES-0001",
            "kind": "LES",
            "project_id": "ai-harness-compiler",
            "title": "Postponed annotations fix argparse import errors",
            "summary": "Use postponed evaluation for typing-only generic annotations.",
            "context": "Python 3.12 and 3.13 runtime imports",
            "author": "test-operator",
            "resolution": "Enable future annotations in CLI adapter",
            "lesson": "Separate static type syntax from runtime support.",
            "applicability": ["argparse type annotations"],
            "limitations": ["Does not solve unrelated annotation errors"],
            "evidence": [
                {
                    "source": "evidence.txt",
                    "note": "Regression result",
                    "outcome": "passed",
                    "sha256": hashlib.sha256(
                        (store.root / "evidence.txt").read_bytes()
                    ).hexdigest(),
                }
            ],
        }
    )


def test_append_only_revisions_and_compare_and_swap(store, draft):
    first = store.add(draft)
    first_path = store.records / "LES/LES-0001/0001.json"
    original = first_path.read_bytes()
    with pytest.raises(ValueError, match="already exists"):
        store.add(draft)
    draft.summary = "Refined explanation"
    second = store.revise(draft, expected=1)
    assert second.revision == 2 and second.status == "draft"
    assert first_path.read_bytes() == original
    assert MemoryStore(store.root).latest()[first.id] == second
    with pytest.raises(ValueError, match="conflict"):
        store.revise(draft, expected=1)


def test_verified_lesson_reuse_and_changed_evidence_exclusion(store, draft):
    store.add(draft)
    assert store.search("argparse") == []
    assert store.search("argparse", include_drafts=True)[0]["reusable"] is False
    accepted = store.review(draft.id, 1, "verified", "reviewer", "Reviewed regression evidence")
    assert store.search("argparse")[0]["record"]["revision"] == accepted.revision
    (store.root / "evidence.txt").write_text("changed evidence", encoding="utf-8")
    assert store.reusable() == []
    assert store.search("argparse") == []


def test_verification_requires_positive_evidence_and_solution(store, draft):
    draft.evidence[0].outcome = "failed"
    store.add(draft)
    with pytest.raises(ValidationError, match="Verification"):
        store.review(draft.id, 1, "verified", "reviewer", "Not enough evidence")
    assert store.latest()[draft.id].revision == 1
    assert not (store.records / ".writer.lock").exists()


def test_editing_verified_knowledge_returns_to_draft(store, draft):
    store.add(draft)
    store.review(draft.id, 1, "verified", "reviewer", "Regression checked")
    edited = store.revise(draft, 2)
    assert edited.status == "draft" and edited.reviewed_by is None
    assert store.reusable() == []


def test_project_isolation_and_unresolved_links(store, draft):
    draft.related = ["INC-9999"]
    with pytest.raises(ValueError, match="Relationships"):
        store.add(draft)
    draft.related = []
    store.add(draft)
    other = MemoryStore(store.root, "another-project")
    assert other.latest() == {} and other.search("argparse", include_drafts=True) == []
    with pytest.raises(ValueError, match="different project"):
        other.add(draft)


def test_search_rebuilds_poisoned_cache_and_handles_concurrent_readers(store, draft):
    store.add(draft)
    store.review(draft.id, 1, "verified", "reviewer", "Evidence checked")
    assert store.search("argparse")
    with sqlite3.connect(store.database) as connection:
        connection.execute("UPDATE memory_fts SET body='poisoned cache'")
    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(lambda _: store.search("argparse"), range(6)))
    assert all(result[0]["record"]["id"] == draft.id for result in results)
    assert len(store.context("argparse", budget=1)) == 0
    store.search('argparse" OR 1=1; DROP TABLE memory_fts;')
    assert store.search("argparse")


def test_writer_lock_and_revision_tampering_are_detected(store, draft):
    with store.writer(), pytest.raises(ValueError, match="locked"):
        store.add(draft)
    store.add(draft)
    path = store.records / "LES/LES-0001/0001.json"
    payload = json.loads(path.read_text())
    payload["revision"] = 7
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="filename"):
        store.latest()


@pytest.mark.parametrize(
    "field,value",
    [("id", "../escape"), ("kind", "ADR"), ("applicability", []), ("limitations", [])],
)
def test_incomplete_and_unsafe_lessons_are_rejected(draft, field, value):
    payload = draft.model_dump()
    payload[field] = value
    with pytest.raises(ValidationError):
        RecordDraft.model_validate(payload)


def test_cli_persists_records_index_and_draft_search(store, draft, capsys):
    source = store.root / "draft.json"
    source.write_text(json.dumps(draft.model_dump()))
    prefix = ["memory", "--repository", str(store.root)]
    assert main(prefix + ["add", str(source)]) == 0
    assert main(prefix + ["index"]) == 0
    assert main(prefix + ["index", "--check"]) == 0
    assert main(prefix + ["check"]) == 0
    assert main(prefix + ["search", "argparse", "--include-drafts"]) == 0
    capsys.readouterr()
    assert main(prefix + ["show", "LES-9999"]) == 1
    assert "Unknown record" in capsys.readouterr().err


def test_capture_failure_records_only_draft_and_excludes_raw_model_content(store, capsys):
    report = store.root / "team-report.json"
    report.write_text(
        json.dumps(
            {
                "reports": [
                    {
                        "agent_id": "quality",
                        "status": "failed",
                        "summary": "PRIVATE_RAW_MODEL_OUTPUT",
                    }
                ]
            }
        )
    )
    prefix = ["memory", "--repository", str(store.root)]
    assert main(prefix + ["capture-team", str(report), "--id", "INC-0001"]) == 0
    record = store.latest()["INC-0001"]
    assert record.status == "draft" and record.resolution is None
    assert "PRIVATE_RAW_MODEL_OUTPUT" not in record.model_dump_json()
    capsys.readouterr()


def test_argparse_runtime_failure_has_a_verified_reproduction_and_fix():
    with pytest.raises(TypeError, match="not subscriptable"):
        eval("argparse._SubParsersAction[argparse.ArgumentParser]", {"argparse": argparse})
    source = (
        "from __future__ import annotations\nimport argparse\n"
        "def configure(x: argparse._SubParsersAction[argparse.ArgumentParser]): pass\n"
    )
    namespace = {}
    exec(compile(source, "regression.py", "exec", dont_inherit=True), namespace)
    assert callable(namespace["configure"])


def test_agent_tool_retrieves_a_verified_lesson(store, draft, project):
    pytest.importorskip("sklearn")
    from ai_harness_compiler.pipeline import plan
    from ai_harness_compiler.team.context import RepositoryContext
    from ai_harness_compiler.team.tools import TeamTools

    project.id = "ai-harness-compiler"
    store.add(draft)
    store.review(draft.id, 1, "verified", "reviewer", "Regression reviewed")
    context = RepositoryContext(store.root)
    tools = TeamTools(plan(project), [node.id for node in project.backlog], context)
    result = tools.call("retrieve_memory", "argparse")
    assert result.data["matches"][0]["record"]["id"] == "LES-0001"
    assert result.data["automatic_weight_training"] is False


def test_evidence_freshness_changes_checkpoint_context_digest(store, draft):
    pytest.importorskip("sklearn")
    from ai_harness_compiler.team.context import RepositoryContext

    store.add(draft)
    store.review(draft.id, 1, "verified", "reviewer", "Regression reviewed")
    before = RepositoryContext(store.root).digests()
    (store.root / "evidence.txt").write_text("changed", encoding="utf-8")
    after = RepositoryContext(store.root).digests()
    assert before != after


def test_cyclic_supersession_is_rejected_before_writing_a_revision(store, draft):
    store.add(draft)
    replacement = RecordDraft.model_validate(
        {**draft.model_dump(), "id": "LES-0002", "supersedes": draft.id}
    )
    store.add(replacement)
    draft.supersedes = replacement.id
    with pytest.raises(ValueError, match="supersession"):
        store.revise(draft, expected=1)
    assert store.latest()[draft.id].revision == 1
    assert not (store.records / "LES/LES-0001/0002.json").exists()


def test_cyclic_supersession_in_manually_edited_records_is_rejected(store, draft):
    store.add(draft)
    store.add(
        RecordDraft.model_validate({**draft.model_dump(), "id": "LES-0002", "supersedes": draft.id})
    )
    path = store.records / "LES/LES-0001/0001.json"
    payload = json.loads(path.read_text())
    payload["supersedes"] = "LES-0002"
    path.write_text(json.dumps(payload))
    with pytest.raises(ValueError, match="supersession"):
        store.latest()
