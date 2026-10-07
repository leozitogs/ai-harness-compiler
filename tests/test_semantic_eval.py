"""Contract and protocol tests; fixture human declarations are not actual semantic reviews."""

import copy
import hashlib
import json
import shutil
import socket
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from pydantic import ValidationError

from ai_harness_compiler.cli import main
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_eval import (
    CRITERIA,
    SemanticReview,
    UnderstandingEvalReport,
    UnderstandingEvalSuite,
)
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec
from ai_harness_compiler.semantic_eval import FrozenCorpus, assess_artifact, save_report
from ai_harness_compiler.understanding import prepare_understanding

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "evals/understanding/v1"


@pytest.fixture
def corpus():
    return FrozenCorpus(CORPUS)


def valid_spec(case):
    request = prepare_understanding(case.project)
    rules = []
    for index, expected in enumerate(case.required_rules):
        ref = next(ref for ref in request.references if ref.pointer == expected.source_pointer)
        rules.append(
            {
                "id": f"rule-{index + 1}",
                "description": expected.quote,
                "condition": "Fixture condition; no semantic claim",
                "outcome": "Fixture outcome; no semantic claim",
                "origin": "extracted",
                "source_refs": [ref.id],
            }
        )
    return ProjectUnderstandingSpec.model_validate(
        {
            "request": request.model_dump(),
            "proposal": {"business_rules": rules},
        }
    )


def write_spec(tmp_path, spec):
    path = tmp_path / "artifact.json"
    path.write_text(spec.model_dump_json(), encoding="utf-8")
    return path


def review_for(corpus, case, spec):
    return SemanticReview(
        reviewer="human-protocol-fixture",
        note="Fixture declarations test protocol, not semantics",
        case_sha256=canonical_project_digest(case.model_dump()),
        rubric_sha256=canonical_project_digest(corpus.rubric.model_dump()),
        proposal_sha256=canonical_project_digest(spec.proposal.model_dump()),
        checks=[
            {"criterion": key, "outcome": "pass", "note": "Fixture judgment only"}
            for key in CRITERIA
        ],
        coverage=[
            {"requirement_id": req.id, "business_rule_id": rule.id}
            for req, rule in zip(case.required_rules, spec.proposal.business_rules, strict=True)
        ],
        support=[
            {
                "item_id": item.id,
                "source_refs": item.source_refs,
                "outcome": "pass",
                "note": "Protocol fixture, not actual support assessment",
            }
            for item in (
                spec.proposal.statements
                + spec.proposal.business_rules
                + spec.proposal.domain_candidates
                + spec.proposal.conflicts
                + spec.proposal.questions
            )
        ],
    )


def freeze(directory):
    data = json.loads((directory / "freeze.json").read_text(encoding="utf-8"))
    data["artifacts"] = {
        name: hashlib.sha256((directory / name).read_bytes()).hexdigest()
        for name in data["artifacts"]
    }
    (directory / "freeze.json").write_text(json.dumps(data), encoding="utf-8")


def reviewed_corpus(tmp_path):
    directory = tmp_path / "corpus"
    shutil.copytree(CORPUS, directory)
    path = directory / "rubric.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["approval"] = {"reviewer": "fixture", "note": "Protocol-only rubric declaration"}
    path.write_text(json.dumps(data), encoding="utf-8")
    freeze(directory)
    return FrozenCorpus(directory)


def test_frozen_corpus_has_disjoint_splits_and_generalist_cases(corpus):
    dev = corpus.suites["development"]
    held = corpus.suites["holdout"]
    assert len(dev.cases) == len(held.cases) == 8
    assert {case.id for case in dev.cases}.isdisjoint(case.id for case in held.cases)
    assert len({case.category for case in dev.cases}) == 8
    a, b = [case for case in dev.cases if case.category in {"rules-a", "rules-b"}]
    assert a.project.domain == b.project.domain
    assert a.required_rules != b.required_rules
    assert next(case for case in dev.cases if case.category == "new-domain").project.domain is None
    assert corpus.rubric.approval is None


def test_empty_business_rules_from_real_pilot_fail(corpus):
    artifact = ROOT / "docs/evidence/sprint-2-5-ac-pilot/cold-understanding.json"
    report = assess_artifact(corpus, "development", "dev-compatible-rules", artifact)
    assert report.status == "fail"
    assert report.checks[0].criterion == "rule-coverage"
    assert report.checks[0].outcome == "fail"
    assert report.model_qualification == "not-established"
    assert all(check.outcome == "not-run" for check in report.checks[1:])


def test_valid_artifact_without_human_judgment_is_not_run(corpus, tmp_path, monkeypatch):
    monkeypatch.setattr(socket, "socket", lambda *_a, **_k: pytest.fail("No network allowed"))
    case = corpus.case("development", "dev-rules-a")
    report = assess_artifact(corpus, "development", case.id, write_spec(tmp_path, valid_spec(case)))
    assert report.status == "not-run"
    assert report.review is None
    assert report.execution_evidence == "offline-artifact-model-execution-not-established"


def test_all_fixture_judgments_cannot_pass_unapproved_rubric(corpus, tmp_path):
    case = corpus.case("development", "dev-rules-a")
    spec = valid_spec(case)
    review_path = tmp_path / "review.json"
    review_path.write_text(review_for(corpus, case, spec).model_dump_json(), encoding="utf-8")
    report = assess_artifact(
        corpus, "development", case.id, write_spec(tmp_path, spec), review_path
    )
    assert all(check.outcome == "pass" for check in report.checks)
    assert report.status == "not-run"


def test_declared_review_protocol_pass_does_not_qualify_model(tmp_path):
    corpus = reviewed_corpus(tmp_path)
    case = corpus.case("development", "dev-rules-a")
    spec = valid_spec(case)
    review_path = tmp_path / "review.json"
    review_path.write_text(review_for(corpus, case, spec).model_dump_json(), encoding="utf-8")
    report = assess_artifact(
        corpus, "development", case.id, write_spec(tmp_path, spec), review_path
    )
    assert report.status == "pass"
    assert report.model_qualification == "not-established"
    corpus.validate_report(report)
    Draft202012Validator(UnderstandingEvalReport.model_json_schema()).validate(report.model_dump())


@pytest.mark.parametrize(
    "kind", ["status", "checks", "input", "proposal", "qualification", "error"]
)
def test_report_rejects_contradictory_fields(corpus, tmp_path, kind):
    report = assess_artifact(
        corpus,
        "development",
        "dev-rules-a",
        write_spec(tmp_path, valid_spec(corpus.case("development", "dev-rules-a"))),
    )
    data = report.model_dump()
    if kind == "status":
        data["status"] = "pass"
    elif kind == "checks":
        data["checks"][0]["outcome"] = "pass"
    elif kind == "input":
        data["input_sha256"] = "a" * 64
    elif kind == "proposal":
        data["proposal_sha256"] = "a" * 64
    elif kind == "qualification":
        data["model_qualification"] = "qualified"
    else:
        data["error_code"] = "made-up-error"
    with pytest.raises(ValidationError):
        UnderstandingEvalReport.model_validate(data)


@pytest.mark.parametrize(
    "kind",
    [
        "digest",
        "mapping",
        "coverage",
        "source",
        "checks",
        "support-missing",
        "support-source",
        "support-fail",
        "support-unknown",
        "support-duplicate",
    ],
)
def test_invalid_review_becomes_error_not_success(corpus, tmp_path, kind):
    case = corpus.case("development", "dev-rules-a")
    spec = valid_spec(case)
    data = review_for(corpus, case, spec).model_dump()
    if kind == "digest":
        data["proposal_sha256"] = "a" * 64
    elif kind == "mapping":
        data["coverage"][0]["business_rule_id"] = "missing-rule"
    elif kind == "coverage":
        data["coverage"] = []
    elif kind == "checks":
        data["checks"].pop()
    elif kind == "source":
        spec.proposal.business_rules[0].source_refs = [spec.request.references[0].id]
        spec.proposal.business_rules[0].origin = "hypothesis"
        data["proposal_sha256"] = canonical_project_digest(spec.proposal.model_dump())
    elif kind == "support-missing":
        data["support"] = []
    elif kind == "support-source":
        data["support"][0]["source_refs"] = [spec.request.references[0].id]
    elif kind == "support-fail":
        data["support"][0]["outcome"] = "fail"
    elif kind == "support-unknown":
        data["support"][0]["item_id"] = "foreign-item"
    else:
        data["support"].append(copy.deepcopy(data["support"][0]))
    path = tmp_path / "review.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    report = assess_artifact(corpus, "development", case.id, write_spec(tmp_path, spec), path)
    assert report.status == "error"
    assert report.error_code == "EVAL_REVIEW_INVALID"


def test_human_pass_cannot_override_expected_no_conflict(tmp_path):
    corpus = reviewed_corpus(tmp_path)
    case = corpus.case("development", "dev-rules-a")
    spec = valid_spec(case)
    data = spec.model_dump()
    data["proposal"]["conflicts"] = [
        {
            "id": "invented",
            "description": "Fixture invented conflict",
            "source_refs": [ref.id for ref in spec.request.references[:2]],
        }
    ]
    spec = ProjectUnderstandingSpec.model_validate(data)
    path = tmp_path / "review.json"
    path.write_text(review_for(corpus, case, spec).model_dump_json(), encoding="utf-8")
    report = assess_artifact(corpus, "development", case.id, write_spec(tmp_path, spec), path)
    assert report.status == "fail"
    assert report.checks[2].outcome == "fail"


@pytest.mark.parametrize(
    "case_id,criterion",
    [
        ("dev-branding-conflict", "conflict-validity"),
        ("dev-ambiguous", "uncertainty"),
    ],
)
def test_missing_expected_conflict_or_question_fails(corpus, tmp_path, case_id, criterion):
    case = corpus.case("development", case_id)
    report = assess_artifact(corpus, "development", case.id, write_spec(tmp_path, valid_spec(case)))
    assert report.status == "fail"
    assert next(check for check in report.checks if check.criterion == criterion).outcome == "fail"


@pytest.mark.parametrize("kind", ["missing", "invalid", "wrong-snapshot", "oversized"])
def test_bad_artifact_produces_error(corpus, tmp_path, kind):
    path = tmp_path / "artifact.json"
    if kind == "invalid":
        path.write_text("{private broken JSON", encoding="utf-8")
    elif kind == "wrong-snapshot":
        write_spec(tmp_path, valid_spec(corpus.case("development", "dev-rules-b")))
    elif kind == "oversized":
        path.write_bytes(b" " * (2 * 1024 * 1024 + 1))
    report = assess_artifact(corpus, "development", "dev-rules-a", path)
    assert report.status == "error"
    assert report.understanding is None and report.review is None
    assert "private" not in report.model_dump_json()


@pytest.mark.parametrize(
    "kind",
    [
        "hash",
        "split",
        "leakage",
        "renamed-leakage",
        "quote",
        "duplicate",
        "version",
    ],
)
def test_changed_or_contradictory_corpus_rejected(tmp_path, kind):
    directory = tmp_path / "corpus"
    shutil.copytree(CORPUS, directory)
    path = directory / "holdout.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if kind == "hash":
        path.write_bytes(path.read_bytes() + b" ")
    else:
        if kind == "split":
            data["split"] = "development"
        elif kind == "version":
            data["version"] = "v2"
        elif kind in {"leakage", "renamed-leakage"}:
            data["cases"][0] = json.loads(
                (directory / "development.json").read_text(encoding="utf-8")
            )["cases"][0]
            if kind == "renamed-leakage":
                data["cases"][0]["id"] = "held-renamed"
                data["cases"][0]["project"]["id"] = "renamed-project"
                data["cases"][0]["project"]["name"] = "Different name, same content"
        elif kind == "quote":
            data["cases"][0]["required_rules"][0]["quote"] = "invented expectation"
        else:
            data["cases"][1] = copy.deepcopy(data["cases"][0])
        path.write_text(json.dumps(data), encoding="utf-8")
        freeze(directory)
    with pytest.raises(ValueError):
        FrozenCorpus(directory)


def test_report_binding_rejects_another_freeze(corpus, tmp_path):
    report = assess_artifact(corpus, "development", "dev-rules-a", tmp_path / "absent")
    report.corpus_sha256 = "a" * 64
    with pytest.raises(ValueError, match="EVAL_BINDING"):
        corpus.validate_report(report)


def test_cli_persists_failure_and_validates_report(corpus, tmp_path, capsys):
    output = tmp_path / "eval.json"
    args = [
        "eval-understanding",
        "docs/evidence/sprint-2-5-ac-pilot/cold-understanding.json",
        "--corpus",
        str(CORPUS),
        "--case",
        "dev-compatible-rules",
        "--output",
        str(output),
    ]
    assert main(args) == 1
    assert "fail" in capsys.readouterr().out
    assert main(["validate-eval-report", str(output), "--corpus", str(CORPUS)]) == 0
    previous = output.read_bytes()
    assert main(args) == 1
    assert output.read_bytes() == previous


def test_holdout_requires_explicit_opt_in_and_candidate_digest(corpus, tmp_path):
    case = corpus.case("holdout", "held-rules-a")
    source = write_spec(tmp_path, valid_spec(case))
    output = tmp_path / "eval.json"
    args = [
        "eval-understanding",
        str(source),
        "--corpus",
        str(CORPUS),
        "--case",
        case.id,
        "--split",
        "holdout",
        "--output",
        str(output),
    ]
    assert main(args) == 1 and not output.exists()
    assert main(args + ["--allow-holdout"]) == 1 and not output.exists()
    assert main(args + ["--allow-holdout", "--candidate-sha256", "a" * 64]) == 1
    report = UnderstandingEvalReport.model_validate_json(output.read_bytes())
    assert report.status == "not-run"
    assert report.declared_candidate_sha256 == "a" * 64


def test_schema_export_for_suite_and_report(corpus):
    validator = Draft202012Validator(UnderstandingEvalSuite.model_json_schema())
    for suite in corpus.suites.values():
        validator.validate(suite.model_dump())


def test_save_report_never_overwrites(corpus, tmp_path):
    report = assess_artifact(corpus, "development", "dev-rules-a", tmp_path / "absent")
    path = tmp_path / "report.json"
    path.write_text("keep", encoding="utf-8")
    with pytest.raises(FileExistsError):
        save_report(report, path)
    assert path.read_text(encoding="utf-8") == "keep"
