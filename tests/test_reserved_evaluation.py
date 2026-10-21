"""Synthetic metadata fixtures; no reserved inputs or human approvals are consumed."""

import copy
import hashlib
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.reserved_evaluation import (
    SCENARIOS,
    ReservedEvaluationProtocol,
    ReservedPreparationReport,
    prepare_reserved_evaluation,
)


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def binding(name, scenario="novel-intent"):
    return {
        "case_id": name,
        "project_id": name,
        "family_id": name,
        "scenario": scenario,
        "artifact_path": f"unread/{name}.json",
        **{
            field: digest(name + field)
            for field in ("artifact_sha256", "case_sha256", "input_sha256", "semantic_sha256")
        },
    }


def protocol_data():
    return {
        "id": "synthetic-reserved",
        "rubric_sha256": digest("synthetic-rubric"),
        "candidate_designer": "synthetic-designer",
        "curator": "synthetic-independent-curator",
        "curator_exposure": "blind-declared",
        "candidate": {
            "source_commit": "a" * 40,
            "composition_version": "synthetic-composition/v1",
            "audit_version": "synthetic-audit/v1",
            "profile_sha256": digest("synthetic-profile"),
            "code_sha256": digest("synthetic-code"),
        },
        "development": [binding("synthetic-development")],
        "reserved": [binding(f"synthetic-{i}", s) for i, s in enumerate(sorted(SCENARIOS))]
        + [binding("synthetic-7", "contrasting-rules")],
        "budget": {
            "max_calls": 16,
            "repetitions": 1,
            "max_call_seconds": 180,
            "max_session_seconds": 2880,
        },
    }


def reviewed_protocol():
    protocol = ReservedEvaluationProtocol.model_validate(protocol_data())
    protocol.corpus_candidate_sha256 = protocol.candidate.sha256
    data = protocol.model_dump()
    data["review"] = {
        "reviewer": "synthetic-human",
        "note": "Test fixture only, not actual PO approval",
        "corpus_sha256": protocol.corpus_sha256,
    }
    return ReservedEvaluationProtocol.model_validate(data)


def test_reviewable_metadata_never_claims_payload_validation_or_execution():
    report = prepare_reserved_evaluation(reviewed_protocol())
    assert report.state == "reviewable"
    assert report.pending_gates == []
    assert report.payload_validation == "not-performed"
    assert report.identity_authentication == "not-established"
    assert report.execution_authorized is False
    assert report.model_calls == 0


def test_draft_reports_missing_gates():
    protocol = ReservedEvaluationProtocol(
        id="draft", rubric_sha256=digest("rubric"), candidate_designer="designer"
    )
    report = prepare_reserved_evaluation(protocol)
    assert report.state == "blocked"
    assert set(report.pending_gates) == {
        "independent-curation-not-declared",
        "candidate-not-frozen",
        "development-metadata-missing",
        "reserved-case-count-insufficient",
        "scenario-coverage-incomplete",
        "human-expectations-review-missing",
        "execution-budget-not-proposed",
    }


@pytest.mark.parametrize(
    "field",
    [
        "case_id",
        "project_id",
        "family_id",
        "artifact_path",
        "artifact_sha256",
        "case_sha256",
        "input_sha256",
        "semantic_sha256",
    ],
)
def test_split_overlap_is_blocked_even_with_renamed_ids(field):
    data = reviewed_protocol().model_dump()
    data["reserved"][0][field] = data["development"][0][field]
    report = prepare_reserved_evaluation(ReservedEvaluationProtocol.model_validate(data))
    assert "development-reserved-overlap:" + field in report.pending_gates
    assert "human-expectations-review-stale" in report.pending_gates


@pytest.mark.parametrize(
    "field", ["case_id", "artifact_path", "artifact_sha256", "case_sha256", "semantic_sha256"]
)
def test_within_split_duplicates_are_invalid(field):
    data = protocol_data()
    data["reserved"][1][field] = data["reserved"][0][field]
    with pytest.raises(ValidationError):
        ReservedEvaluationProtocol.model_validate(data)


@pytest.mark.parametrize("field", ["code_sha256", "profile_sha256"])
def test_candidate_change_invalidates_corpus_binding(field):
    data = reviewed_protocol().model_dump()
    data["candidate"][field] = digest("changed")
    report = prepare_reserved_evaluation(ReservedEvaluationProtocol.model_validate(data))
    assert "corpus-candidate-binding-missing-or-stale" in report.pending_gates


@pytest.mark.parametrize(
    ("change", "gate"),
    [
        ({"curator": "synthetic-designer"}, "curator-is-candidate-designer"),
        ({"curator_exposure": "development-visible"}, "independent-curation-not-declared"),
        ({"review": None}, "human-expectations-review-missing"),
        ({"budget": None}, "execution-budget-not-proposed"),
    ],
)
def test_required_preparation_gates(change, gate):
    data = reviewed_protocol().model_dump()
    data.update(change)
    assert (
        gate
        in prepare_reserved_evaluation(
            ReservedEvaluationProtocol.model_validate(data)
        ).pending_gates
    )


def test_designer_cannot_declare_human_approval():
    data = reviewed_protocol().model_dump()
    data["review"]["reviewer"] = data["candidate_designer"]
    report = prepare_reserved_evaluation(ReservedEvaluationProtocol.model_validate(data))
    assert "candidate-designer-cannot-approve-corpus" in report.pending_gates


def test_budget_matches_both_calls_per_case_and_repetition():
    data = reviewed_protocol().model_dump()
    data["budget"].update(repetitions=2, max_calls=16)
    report = prepare_reserved_evaluation(ReservedEvaluationProtocol.model_validate(data))
    assert "execution-budget-does-not-match-generation-and-audit" in report.pending_gates
    data["budget"]["max_calls"] = 32
    assert (
        prepare_reserved_evaluation(ReservedEvaluationProtocol.model_validate(data)).state
        == "reviewable"
    )
    for field in ("retries", "repairs", "concurrency"):
        invalid = copy.deepcopy(data)
        invalid["budget"][field] = 2
        with pytest.raises(ValidationError):
            ReservedEvaluationProtocol.model_validate(invalid)
    data["budget"]["max_session_seconds"] = 1
    with pytest.raises(ValidationError):
        ReservedEvaluationProtocol.model_validate(data)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("state", "blocked"),
        ("pending_gates", ["fabricated"]),
        ("protocol_sha256", "0" * 64),
        ("execution_authorized", True),
        ("model_calls", 1),
    ],
)
def test_forged_report_is_rejected(field, value):
    data = prepare_reserved_evaluation(reviewed_protocol()).model_dump()
    data[field] = value
    with pytest.raises(ValidationError):
        ReservedPreparationReport.model_validate(data)


def test_cli_reads_only_metadata_and_never_overwrites(tmp_path, monkeypatch):
    protocol = reviewed_protocol()
    source = tmp_path / "protocol.json"
    target = tmp_path / "report.json"
    source.write_text(protocol.model_dump_json(), encoding="utf-8")
    original_read_bytes = Path.read_bytes

    def guarded_read(path):
        assert path == source, "CLI attempted to read a reserved payload"
        return original_read_bytes(path)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "read_bytes", guarded_read)
        assert main(["prepare-reserved-evaluation", str(source), "--output", str(target)]) == 0
    report = ReservedPreparationReport.model_validate_json(target.read_bytes())
    assert not report.execution_authorized
    before = target.read_bytes()
    assert main(["prepare-reserved-evaluation", str(source), "--output", str(target)]) == 1
    assert target.read_bytes() == before


def test_cli_blocked_still_writes_diagnostic(tmp_path):
    data = reviewed_protocol().model_dump()
    data["review"] = None
    source, target = tmp_path / "protocol.json", tmp_path / "report.json"
    source.write_text(ReservedEvaluationProtocol.model_validate(data).model_dump_json())
    assert main(["prepare-reserved-evaluation", str(source), "--output", str(target)]) == 1
    report = ReservedPreparationReport.model_validate_json(target.read_bytes())
    assert report.state == "blocked"


def test_cli_rejects_oversized_metadata(tmp_path):
    source, target = tmp_path / "oversized.json", tmp_path / "report.json"
    source.write_bytes(b" " * (2 * 1024 * 1024 + 1))
    assert main(["prepare-reserved-evaluation", str(source), "--output", str(target)]) == 1
    assert not target.exists()
