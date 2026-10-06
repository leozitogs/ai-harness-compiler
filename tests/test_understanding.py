"""Snapshot-bound understanding contracts; fixtures are proposals, not model outputs."""

import copy
import json
import socket

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.understanding import (
    ProjectUnderstandingSpec,
    UnderstandingProposal,
    UnderstandingRequest,
)
from ai_harness_compiler.understanding import prepare_understanding


def payload(project):
    request = prepare_understanding(project)
    ref = request.references[0]
    return {
        "request": request.model_dump(),
        "proposal": {
            "statements": [
                {
                    "id": "purpose",
                    "subject": "purpose",
                    "text": ref.value,
                    "status": "declared",
                    "source_refs": [ref.id],
                }
            ],
            "business_rules": [
                {
                    "id": "rule",
                    "description": "A proposed workflow rule",
                    "condition": "When a draft is ready",
                    "outcome": "Request review",
                    "origin": "hypothesis",
                    "source_refs": [ref.id],
                }
            ],
            "domain_candidates": [
                {
                    "id": "candidate",
                    "domain": "unregistered-domain",
                    "rationale": "Candidate supplied for testing",
                    "source_refs": [ref.id],
                }
            ],
            "questions": [
                {"id": "question", "question": "Who confirms publication?", "source_refs": [ref.id]}
            ],
        },
    }


def add_review(value, decision="approved"):
    value["review"] = {
        "decision": decision,
        "reviewer": "fixture-reviewer",
        "note": "Contract test metadata only",
        "input_sha256": value["request"]["original_sha256"],
        "proposal_sha256": canonical_project_digest(
            UnderstandingProposal.model_validate(value["proposal"]).model_dump()
        ),
        "answers": [{"item_id": "question", "text": "Product owner"}],
    }


def test_preparation_is_offline_and_preserves_independent_snapshot(project, monkeypatch):
    def no_network(*args, **kwargs):
        raise AssertionError("Preparation must not invoke network")

    monkeypatch.setattr(socket, "socket", no_network)
    request = prepare_understanding(project)
    assert request.original_input == project
    assert request.original_sha256 == canonical_project_digest(project.model_dump())
    assert {ref.pointer for ref in request.references} >= {
        "/conception",
        "/branding",
        "/constraints",
        "/backlog/0/description",
    }
    assert all(ref.content_trust == "untrusted-data" for ref in request.references)
    original = copy.deepcopy(request.model_dump())
    project.branding.tone.append("changed")
    assert request.model_dump() == original
    assert UnderstandingRequest.model_validate_json(request.model_dump_json()) == request


def test_proposal_and_review_roundtrip_with_schema(project):
    value = payload(project)
    add_review(value)
    spec = ProjectUnderstandingSpec.model_validate(value)
    assert spec.proposal.domain_candidates[0].confidence is None
    assert spec.request.original_input.domain == project.domain
    assert ProjectUnderstandingSpec.model_validate_json(spec.model_dump_json()) == spec
    Draft202012Validator(ProjectUnderstandingSpec.model_json_schema()).validate(spec.model_dump())


@pytest.mark.parametrize(
    "mutation",
    [
        "digest",
        "reference-text",
        "project",
        "missing-pointer",
        "negative-index",
        "leading-zero",
        "bad-escape",
        "duplicate-reference",
    ],
)
def test_invalid_request_snapshot_is_rejected(project, mutation):
    value = prepare_understanding(project).model_dump()
    if mutation == "digest":
        value["original_sha256"] = "0" * 64
    if mutation == "reference-text":
        value["references"][0]["value"] = "Forged quotation"
    if mutation == "project":
        value["references"][0]["project_id"] = "other-project"
    if mutation == "missing-pointer":
        value["references"][0]["pointer"] = "/missing"
    if mutation == "negative-index":
        value["references"][0]["pointer"] = "/backlog/-1"
    if mutation == "leading-zero":
        value["references"][0]["pointer"] = "/backlog/00"
    if mutation == "bad-escape":
        value["references"][0]["pointer"] = "/conception~2"
    if mutation == "duplicate-reference":
        value["references"].append(copy.deepcopy(value["references"][0]))
    with pytest.raises(ValidationError):
        UnderstandingRequest.model_validate(value)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-ref",
        "duplicate-ref",
        "duplicate-item",
        "confidence",
        "declared-summary",
        "extracted-rule",
        "empty-proposal",
        "model-review",
    ],
)
def test_invalid_proposal_is_rejected(project, mutation):
    value = payload(project)
    if mutation == "missing-ref":
        value["proposal"]["business_rules"][0]["source_refs"] = ["missing"]
    if mutation == "duplicate-ref":
        value["proposal"]["business_rules"][0]["source_refs"] *= 2
    if mutation == "duplicate-item":
        value["proposal"]["business_rules"][0]["id"] = "purpose"
    if mutation == "confidence":
        value["proposal"]["domain_candidates"][0]["confidence"] = 0.99
    if mutation == "declared-summary":
        value["proposal"]["statements"][0]["text"] = "Invented summary"
    if mutation == "extracted-rule":
        value["proposal"]["business_rules"][0]["origin"] = "extracted"
    if mutation == "empty-proposal":
        value["proposal"] = {}
    if mutation == "model-review":
        value["proposal"]["review"] = {"decision": "approved"}
    with pytest.raises(ValidationError):
        ProjectUnderstandingSpec.model_validate(value)


@pytest.mark.parametrize(
    "mutation",
    [
        "stale-input",
        "stale-proposal",
        "unanswered",
        "unknown-answer",
        "duplicate-answer",
        "unresolved-conflict",
    ],
)
def test_contradictory_review_is_rejected(project, mutation):
    value = payload(project)
    if mutation == "unresolved-conflict":
        value["proposal"]["conflicts"] = [
            {
                "id": "conflict",
                "description": "Conflicting sources",
                "source_refs": ["input-1", "input-2"],
            }
        ]
    add_review(value)
    if mutation == "stale-input":
        value["review"]["input_sha256"] = "0" * 64
    if mutation == "stale-proposal":
        value["review"]["proposal_sha256"] = "0" * 64
    if mutation == "unanswered":
        value["review"]["answers"] = []
    if mutation == "unknown-answer":
        value["review"]["answers"][0]["item_id"] = "missing"
    if mutation == "duplicate-answer":
        value["review"]["answers"] *= 2
    with pytest.raises(ValidationError):
        ProjectUnderstandingSpec.model_validate(value)


def test_rejected_review_may_preserve_unresolved_questions(project):
    value = payload(project)
    add_review(value, "rejected")
    value["review"]["answers"] = []
    assert ProjectUnderstandingSpec.model_validate(value).review.decision == "rejected"


def test_cli_prepares_and_validates_without_claiming_model_execution(project, tmp_path, capsys):
    source = tmp_path / "project.yaml"
    source.write_text(json.dumps(project.model_dump(), ensure_ascii=False), encoding="utf-8")
    assert main(["prepare-understanding", str(source)]) == 0
    prepared = json.loads(capsys.readouterr().out)
    assert prepared["schema_version"] == "UnderstandingRequest/v1"
    assert "proposal" not in prepared
    path = tmp_path / "understanding.json"
    path.write_text(json.dumps(payload(project)), encoding="utf-8")
    assert main(["validate-understanding", str(path)]) == 0
    assert "not established" in capsys.readouterr().out
    invalid = payload(project)
    invalid["request"]["references"][0]["value"] = "forged"
    path.write_text(json.dumps(invalid), encoding="utf-8")
    assert main(["validate-understanding", str(path)]) == 1


def test_understanding_file_limit_precedes_parsing(tmp_path, capsys):
    source = tmp_path / "large.json"
    source.write_bytes(b" " * 17)
    assert main(["validate-understanding", str(source), "--max-understanding-bytes", "16"]) == 1
    assert "UNDERSTANDING_TOO_LARGE" in capsys.readouterr().err


def test_invalid_snapshot_diagnostic_does_not_echo_values(project, tmp_path, capsys):
    value = payload(project)
    value["request"]["references"][0]["value"] = "private-value-must-not-be-echoed"
    source = tmp_path / "invalid.json"
    source.write_text(json.dumps(value), encoding="utf-8")
    assert main(["validate-understanding", str(source)]) == 1
    assert "private-value-must-not-be-echoed" not in capsys.readouterr().err


def test_duplicate_pointer_alias_cannot_fake_independent_sources(project):
    value = prepare_understanding(project).model_dump()
    alias = copy.deepcopy(value["references"][0])
    alias["id"] = "alias"
    value["references"].append(alias)
    with pytest.raises(ValidationError, match="pointers must be unique"):
        UnderstandingRequest.model_validate(value)


def test_conflict_reference_budget_is_enforced():
    with pytest.raises(ValidationError):
        UnderstandingProposal.model_validate(
            {
                "conflicts": [
                    {
                        "id": "conflict",
                        "description": "Too many sources",
                        "source_refs": [f"source-{index}" for index in range(33)],
                    }
                ]
            }
        )
