"""Fixed check commands, trusted revision opt-in and total/per-command budgets."""

import hashlib
import sys
from collections.abc import Callable
from pathlib import Path
from time import monotonic

from ai_harness_compiler.models.qa import CheckID, QACheckResult, QAReviewRequest
from ai_harness_compiler.qa_collection import assert_current_request, bounded_process
from ai_harness_compiler.scrum_collection import timestamp

COMMANDS: dict[CheckID, tuple[str, ...]] = {
    "lint": ("-m", "ruff", "check", "."),
    "format": ("-m", "ruff", "format", "--check", "."),
    "typing": ("-m", "mypy", "src"),
    "tests": ("-m", "pytest", "-q", "-p", "no:cacheprovider"),
    "schemas": ("scripts/export_schemas.py", "--check"),
    "repo-policy": ("scripts/generate_repo_agents.py", "--check"),
    "sprint-plan": ("scripts/generate_sprint_plan.py", "--check"),
}


def run_checks(
    request: QAReviewRequest,
    root: Path,
    trusted_revision: str | None = None,
    on_result: Callable[[QACheckResult], None] | None = None,
) -> list[QACheckResult]:
    request = QAReviewRequest.model_validate(request.model_dump())
    assert_current_request(request, root, timestamp())
    if trusted_revision is not None and trusted_revision != request.head_commit:
        raise ValueError("Trusted check revision differs from reviewed head")
    deadline = monotonic() + request.total_check_seconds
    results = []
    for check_id in request.check_ids:
        started = timestamp()
        output, code, state = "", None, "not-run"
        remaining = deadline - monotonic()
        if trusted_revision is not None and remaining > 0:
            assert_current_request(request, root, timestamp())
            remaining = deadline - monotonic()
            if remaining > 0:
                try:
                    code, output, termination = bounded_process(
                        [
                            sys.executable,
                            *COMMANDS[check_id],
                            *(
                                ["--sprint", request.snapshot.observation.sprint_id]
                                if check_id == "sprint-plan"
                                else []
                            ),
                        ],
                        root,
                        min(request.check_timeout_seconds, remaining),
                        32768,
                    )
                    state = (
                        termination
                        if termination != "completed"
                        else "passed"
                        if code == 0
                        else "failed"
                    )
                except OSError:
                    state, code, output = "failed", -1, "Fixed check process unavailable."

        results.append(
            QACheckResult.model_validate(
                {
                    "id": check_id,
                    "request_sha256": request.request_sha256,
                    "head_commit": request.head_commit,
                    "status": state,
                    "exit_code": code,
                    "started_at": started,
                    "finished_at": timestamp(),
                    "output": output,
                    "output_sha256": hashlib.sha256(output.encode()).hexdigest(),
                }
            )
        )
        if on_result is not None:
            on_result(results[-1])
    assert_current_request(request, root, timestamp())
    return results
