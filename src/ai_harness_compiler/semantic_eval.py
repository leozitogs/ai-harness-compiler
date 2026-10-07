"""Bounded offline evaluator; never invokes a model or authors human judgments."""

import hashlib
from pathlib import Path

from pydantic import ValidationError

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_eval import (
    FrozenUnderstandingCorpus,
    SemanticReview,
    UnderstandingEvalCase,
    UnderstandingEvalReport,
    UnderstandingEvalSuite,
    UnderstandingRubric,
    case_checks,
    semantic_snapshot_digest,
)
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec

MAX_BYTES = 2 * 1024 * 1024


def bounded_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("EVAL_SIZE: Artifact exceeds byte budget")
    return data


class FrozenCorpus:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        files = {}
        for name in ("freeze.json", "rubric.json", "development.json", "holdout.json"):
            path = (self.root / name).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError("EVAL_PATH: Corpus artifact escapes its directory")
            files[name] = bounded_bytes(path)
        manifest = FrozenUnderstandingCorpus.model_validate_json(files["freeze.json"])
        for name, digest in manifest.artifacts.items():
            if hashlib.sha256(files[name]).hexdigest() != digest:
                raise ValueError("EVAL_FREEZE: Corpus changed since freeze")
        self.sha256 = hashlib.sha256(files["freeze.json"]).hexdigest()
        self.rubric = UnderstandingRubric.model_validate_json(files["rubric.json"])
        if self.rubric.version != manifest.version:
            raise ValueError("EVAL_VERSION: Rubric differs from corpus version")
        self.suites = {
            split: UnderstandingEvalSuite.model_validate_json(files[split + ".json"])
            for split in ("development", "holdout")
        }
        for split, suite in self.suites.items():
            if suite.split != split:
                raise ValueError("EVAL_SPLIT: Suite split contradicts its file")
            if suite.version != manifest.version:
                raise ValueError("EVAL_VERSION: Suite differs from corpus version")
        dev, held = self.suites.values()
        for dev_values, held_values in (
            ({case.id for case in dev.cases}, {case.id for case in held.cases}),
            ({case.project.id for case in dev.cases}, {case.project.id for case in held.cases}),
            (
                {semantic_snapshot_digest(case.project) for case in dev.cases},
                {semantic_snapshot_digest(case.project) for case in held.cases},
            ),
        ):
            if dev_values & held_values:
                raise ValueError("EVAL_LEAKAGE: Development and holdout snapshots overlap")

    def case(self, split: str, case_id: str) -> UnderstandingEvalCase:
        if split not in self.suites:
            raise ValueError("EVAL_SPLIT: Unknown split")
        for case in self.suites[split].cases:
            if case.id == case_id:
                return UnderstandingEvalCase.model_validate(case.model_dump())
        raise ValueError("EVAL_CASE: Unknown case in selected split")

    def validate_report(self, report: UnderstandingEvalReport) -> None:
        report = UnderstandingEvalReport.model_validate(report.model_dump())
        if (
            report.corpus_sha256 != self.sha256
            or report.rubric != self.rubric
            or report.case != self.case(report.split, report.case.id)
        ):
            raise ValueError("EVAL_BINDING: Report differs from its frozen corpus")


def assess_artifact(
    corpus: FrozenCorpus,
    split: str,
    case_id: str,
    artifact: Path,
    review_file: Path | None = None,
    declared_candidate_sha256: str | None = None,
) -> UnderstandingEvalReport:
    case = corpus.case(split, case_id)
    common = {
        "case": case.model_dump(),
        "rubric": corpus.rubric.model_dump(),
        "corpus_sha256": corpus.sha256,
        "split": split,
        "declared_candidate_sha256": declared_candidate_sha256,
        "input_sha256": canonical_project_digest(case.project.model_dump()),
    }
    UnderstandingEvalReport.model_validate(
        common | {"status": "error", "error_code": "EVAL_PENDING"}
    )
    try:
        spec = ProjectUnderstandingSpec.model_validate_json(bounded_bytes(artifact))
    except (OSError, ValueError, ValidationError, RecursionError):
        return UnderstandingEvalReport.model_validate(
            common | {"status": "error", "error_code": "EVAL_ARTIFACT_INVALID"}
        )
    if spec.request.original_input != case.project:
        return UnderstandingEvalReport.model_validate(
            common | {"status": "error", "error_code": "EVAL_SNAPSHOT_MISMATCH"}
        )
    try:
        review = (
            SemanticReview.model_validate_json(bounded_bytes(review_file)) if review_file else None
        )
        checks = case_checks(case, spec, review)
        outcomes = {check.outcome for check in checks}
        status = (
            "fail"
            if "fail" in outcomes
            else "pass"
            if outcomes == {"pass"} and corpus.rubric.approval
            else "not-run"
        )
        return UnderstandingEvalReport.model_validate(
            common
            | {
                "understanding": spec.model_dump(),
                "review": review.model_dump() if review else None,
                "checks": [check.model_dump() for check in checks],
                "status": status,
                "proposal_sha256": canonical_project_digest(spec.proposal.model_dump()),
            }
        )
    except (OSError, ValueError, ValidationError, RecursionError):
        return UnderstandingEvalReport.model_validate(
            common | {"status": "error", "error_code": "EVAL_REVIEW_INVALID"}
        )


def save_report(report: UnderstandingEvalReport, output: Path) -> None:
    report = UnderstandingEvalReport.model_validate(report.model_dump())
    with output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json_text(report.model_dump()))
