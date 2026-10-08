"""New-directory repair journals; one isolated worker and one charged attempt per call."""

import subprocess
from pathlib import Path
from time import monotonic

from ai_harness_compiler.model_sessions import JobExecutor, session_bytes, write_artifact
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.model_session import WorkerRequest, WorkerResult
from ai_harness_compiler.models.repair import RepairAttempt, RepairPlan, RepairReport
from ai_harness_compiler.models.semantic_eval import UnderstandingEvalReport, case_checks
from ai_harness_compiler.semantic_eval import FrozenCorpus
from ai_harness_compiler.understanding import prepare_understanding


def run_repair(plan: RepairPlan, output: Path, executor: JobExecutor) -> RepairReport:
    plan = RepairPlan.model_validate(plan.model_dump())
    output.mkdir(parents=True, exist_ok=False)
    write_artifact(output / "plan.json", plan.model_dump())
    start = monotonic()
    attempts: list[RepairAttempt] = []
    settings = plan.session.settings
    feedback = None
    evaluation = None
    termination = "repair-limit"
    while True:
        offset = monotonic() - start
        remaining = settings.session_seconds - offset
        if remaining <= 0:
            termination = "time-limit"
            break
        if len(attempts) >= settings.max_attempts:
            termination = "attempt-limit"
            break
        request = WorkerRequest(
            settings=settings.model_copy(deep=True),
            request=prepare_understanding(plan.session.cases[0].project),
            prompt_sha256=plan.repair_prompt_sha256 if feedback else plan.session.prompt_sha256,
            repair_feedback=feedback,
        )
        offset = monotonic() - start
        remaining = settings.session_seconds - offset
        if remaining <= 0:
            termination = "time-limit"
            break
        timeout = min(float(settings.call_timeout_seconds), remaining)
        try:
            result = WorkerResult.model_validate(
                executor.execute(request.model_copy(deep=True), timeout).model_dump()
            )
            attempt = RepairAttempt(
                index=len(attempts) + 1,
                request=request,
                result=result,
                started_after_seconds=offset,
                elapsed_seconds=monotonic() - start - offset,
                effective_timeout_seconds=timeout,
            )
        except (OSError, ValueError, subprocess.SubprocessError):
            attempt = RepairAttempt(
                index=len(attempts) + 1,
                request=request,
                result=WorkerResult(status="error", error_code="worker-result-error"),
                started_after_seconds=offset,
                elapsed_seconds=monotonic() - start - offset,
                effective_timeout_seconds=timeout,
            )
        attempts.append(attempt)
        write_artifact(output / f"attempt-{attempt.index:03}.json", attempt.model_dump())
        result = attempt.result
        if result.status == "completed":
            assert result.understanding
            case = plan.session.cases[0]
            checks = case_checks(case, result.understanding, None)
            evaluation = UnderstandingEvalReport.model_validate(
                {
                    "case": case.model_dump(),
                    "rubric": plan.session.rubric.model_dump(),
                    "corpus_sha256": plan.session.corpus_sha256,
                    "split": "development",
                    "declared_candidate_sha256": plan.session.declared_candidate_sha256,
                    "understanding": result.understanding.model_dump(),
                    "checks": [check.model_dump() for check in checks],
                    "status": "fail"
                    if any(check.outcome == "fail" for check in checks)
                    else "not-run",
                    "input_sha256": result.understanding.request.original_sha256,
                    "proposal_sha256": canonical_project_digest(
                        result.understanding.proposal.model_dump()
                    ),
                }
            )
            termination = "completed"
            break
        if result.error_code in {"worker-timeout", "model-changed"}:
            termination = result.error_code
            break
        if not result.failure_diagnostic:
            termination = "not-repairable"
            break
        if len(attempts) >= plan.max_repairs + 1:
            termination = "repair-limit"
            break
        feedback = result.failure_diagnostic.model_copy(deep=True)
    report = RepairReport.model_validate(
        {
            "plan": plan.model_dump(),
            "attempts": [a.model_dump() for a in attempts],
            "elapsed_seconds": monotonic() - start,
            "termination": termination,
            "evaluation": evaluation.model_dump() if evaluation else None,
        }
    )
    write_artifact(output / "repair.json", report.model_dump())
    return report


def validate_repair(corpus: FrozenCorpus, directory: Path) -> RepairReport:
    root = directory.resolve()

    def read(name: str) -> bytes:
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Repair journal artifact escapes directory")
        return session_bytes(path)

    report = RepairReport.model_validate_json(read("repair.json"))
    expected = {"plan.json", "repair.json"} | {
        f"attempt-{a.index:03}.json" for a in report.attempts
    }
    if {path.name for path in root.iterdir()} != expected:
        raise ValueError("Repair journal has unexpected or missing artifacts")
    session = report.plan.session
    if (
        session.corpus_sha256 != corpus.sha256
        or session.rubric != corpus.rubric
        or session.cases[0] != corpus.case("development", session.cases[0].id)
    ):
        raise ValueError("Repair journal differs from frozen development corpus")
    if RepairPlan.model_validate_json(read("plan.json")) != report.plan:
        raise ValueError("Repair plan differs from journal")
    for attempt in report.attempts:
        if RepairAttempt.model_validate_json(read(f"attempt-{attempt.index:03}.json")) != attempt:
            raise ValueError("Repair attempt differs from journal")
    return report
