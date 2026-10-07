"""Sequential session I/O with isolated generation and explicit unexecuted jobs."""

import subprocess
import sys
from pathlib import Path
from time import monotonic
from typing import Protocol

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.model_session import (
    ModelSessionReport,
    SessionJob,
    SessionPlan,
    SessionSettings,
    WorkerRequest,
    WorkerResult,
)
from ai_harness_compiler.models.semantic_eval import UnderstandingEvalReport, case_checks
from ai_harness_compiler.semantic_eval import FrozenCorpus
from ai_harness_compiler.understanding import prepare_understanding

MAX_SESSION_BYTES = 64 * 1024 * 1024


def session_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        content = stream.read(MAX_SESSION_BYTES + 1)
    if len(content) > MAX_SESSION_BYTES:
        raise ValueError("SESSION_SIZE: Session artifact exceeds byte budget")
    return content


def write_artifact(path: Path, data: dict[str, object]) -> None:
    content = json_text(data)
    if len(content.encode()) > MAX_SESSION_BYTES:
        raise ValueError("SESSION_SIZE: Session artifact exceeds byte budget")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


class JobExecutor(Protocol):
    def execute(self, request: WorkerRequest, timeout: float) -> WorkerResult: ...


class IsolatedOllamaExecutor:
    def execute(self, request: WorkerRequest, timeout: float) -> WorkerResult:
        process = subprocess.Popen(
            [sys.executable, "-m", "ai_harness_compiler.model_worker"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
        )
        try:
            output, _ = process.communicate(request.model_dump_json().encode(), timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                if process.stdout:
                    process.stdout.close()
            return WorkerResult(status="error", error_code="worker-timeout")
        if process.returncode != 0 or len(output) > 2 * 1024 * 1024:
            return WorkerResult(status="error", error_code="worker-result-error")
        try:
            return WorkerResult.model_validate_json(output)
        except ValueError:
            return WorkerResult(status="error", error_code="worker-result-error")


def make_plan(
    corpus: FrozenCorpus,
    settings: SessionSettings,
    prompt_sha256: str,
    case_ids: list[str] | None = None,
    split: str = "development",
    declared_candidate_sha256: str | None = None,
) -> SessionPlan:
    settings = SessionSettings.model_validate(settings.model_dump())
    if split not in corpus.suites:
        raise ValueError("SESSION_SPLIT: Unknown split")
    ids = case_ids if case_ids is not None else [case.id for case in corpus.suites[split].cases]
    return SessionPlan.model_validate(
        {
            "settings": settings.model_dump(),
            "split": split,
            "cases": [corpus.case(split, case_id).model_dump() for case_id in ids],
            "rubric": corpus.rubric.model_dump(),
            "corpus_sha256": corpus.sha256,
            "prompt_sha256": prompt_sha256,
            "declared_candidate_sha256": declared_candidate_sha256,
        }
    )


def run_session(plan: SessionPlan, output: Path, executor: JobExecutor) -> ModelSessionReport:
    plan = SessionPlan.model_validate(plan.model_dump())
    output.mkdir(parents=True, exist_ok=False)
    write_artifact(output / "plan.json", plan.model_dump())
    start = monotonic()
    jobs: list[SessionJob] = []
    attempts = 0
    reason = None
    locked_digest = plan.settings.expected_model_sha256
    locked_identity = None
    for case in plan.cases:
        for repetition in range(1, plan.settings.repeats + 1):
            remaining = plan.settings.session_seconds - (monotonic() - start)
            if reason is None and remaining <= 0:
                reason = "time-limit"
            if reason is None and attempts >= plan.settings.max_attempts:
                reason = "attempt-limit"
            index = len(jobs) + 1
            if reason:
                job = SessionJob(
                    index=index,
                    case_id=case.id,
                    repetition=repetition,
                    state="not-run",
                    elapsed_seconds=0,
                    error_code="session-" + reason,
                )
            else:
                timeout = min(float(plan.settings.call_timeout_seconds), remaining)
                before = monotonic()
                attempts += 1
                try:
                    request = WorkerRequest(
                        settings=SessionSettings.model_validate(plan.settings.model_dump()),
                        request=prepare_understanding(case.project),
                        prompt_sha256=plan.prompt_sha256,
                    )
                    result = WorkerResult.model_validate(
                        executor.execute(request, timeout).model_dump()
                    )
                except (OSError, ValueError, subprocess.SubprocessError):
                    result = WorkerResult(status="error", error_code="worker-result-error")
                elapsed = monotonic() - before
                if result.status == "completed":
                    assert result.identity and result.understanding
                    identity = result.identity
                    identity_digest = canonical_project_digest(
                        result.identity.model_dump(exclude={"observed_at"})
                    )
                    if (
                        locked_digest
                        and result.identity.model_sha256 != locked_digest
                        or locked_identity
                        and identity_digest != locked_identity
                        or result.identity.requested_model != plan.settings.model
                        or result.settings != plan.settings
                        or result.identity.prompt_sha256 != plan.prompt_sha256
                        or result.understanding.request.original_input != case.project
                    ):
                        result = WorkerResult(status="error", error_code="model-changed")
                    else:
                        locked_digest = identity.model_sha256
                        locked_identity = identity_digest
                if result.status == "error":
                    if result.error_code in {"worker-timeout", "model-changed"}:
                        reason = result.error_code
                    job = SessionJob(
                        index=index,
                        case_id=case.id,
                        repetition=repetition,
                        state="error",
                        elapsed_seconds=elapsed,
                        effective_timeout_seconds=timeout,
                        error_code=result.error_code,
                    )
                else:
                    assert result.understanding
                    checks = case_checks(case, result.understanding, None)
                    evaluation = UnderstandingEvalReport.model_validate(
                        {
                            "case": case.model_dump(),
                            "rubric": plan.rubric.model_dump(),
                            "corpus_sha256": plan.corpus_sha256,
                            "split": plan.split,
                            "declared_candidate_sha256": plan.declared_candidate_sha256,
                            "understanding": result.understanding.model_dump(),
                            "checks": [check.model_dump() for check in checks],
                            "status": "fail"
                            if any(check.outcome == "fail" for check in checks)
                            else "not-run",
                            "input_sha256": canonical_project_digest(case.project.model_dump()),
                            "proposal_sha256": canonical_project_digest(
                                result.understanding.proposal.model_dump()
                            ),
                        }
                    )
                    job = SessionJob(
                        index=index,
                        case_id=case.id,
                        repetition=repetition,
                        state="completed",
                        elapsed_seconds=elapsed,
                        effective_timeout_seconds=timeout,
                        generation=result,
                        evaluation=evaluation,
                    )
            jobs.append(job)
            write_artifact(output / f"job-{index:03}.json", job.model_dump())
    report = ModelSessionReport.model_validate(
        {
            "plan": plan.model_dump(),
            "jobs": [job.model_dump() for job in jobs],
            "attempts_used": attempts,
            "elapsed_seconds": monotonic() - start,
            "stop_reason": reason,
            "run_status": "stopped"
            if reason in {"worker-timeout", "model-changed"}
            else "limited"
            if reason
            else "completed",
            "evaluation_status": "error"
            if any(job.state == "error" for job in jobs)
            else "fail"
            if any(job.evaluation and job.evaluation.status == "fail" for job in jobs)
            else "not-run",
        }
    )
    write_artifact(output / "session.json", report.model_dump())
    return report


def validate_session(corpus: FrozenCorpus, path: Path) -> ModelSessionReport:
    root = path.parent.resolve()
    if not path.resolve().is_relative_to(root):
        raise ValueError("SESSION_PATH: Session artifact escapes its directory")
    report = ModelSessionReport.model_validate_json(session_bytes(path))
    if report.plan.corpus_sha256 != corpus.sha256 or report.plan.rubric != corpus.rubric:
        raise ValueError("SESSION_CORPUS: Session differs from frozen corpus")
    for case in report.plan.cases:
        if case != corpus.case(report.plan.split, case.id):
            raise ValueError("SESSION_CASE: Session case differs from frozen corpus")
    plan_file = (root / "plan.json").resolve()
    if (
        not plan_file.is_relative_to(root)
        or SessionPlan.model_validate_json(session_bytes(plan_file)) != report.plan
    ):
        raise ValueError("SESSION_PLAN: Journal plan differs from session")
    for job in report.jobs:
        file = (root / f"job-{job.index:03}.json").resolve()
        if (
            not file.is_relative_to(root)
            or SessionJob.model_validate_json(session_bytes(file)) != job
        ):
            raise ValueError("SESSION_JOB: Journal job differs from session")
    return report
