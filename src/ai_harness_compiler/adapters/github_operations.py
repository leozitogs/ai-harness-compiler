"""Explicit GitHub adapter: one additive label endpoint, never issue replacement."""

import hashlib
import json
import shutil
import subprocess
import threading
from collections.abc import Callable
from urllib.parse import quote

from ai_harness_compiler.models.scrum import RepositoryName
from ai_harness_compiler.models.scrum_operations import RemoteIssueState, ScrumOperationPlan
from ai_harness_compiler.scrum_collection import timestamp
from ai_harness_compiler.scrum_observer import decode_document


def _request(method: str, endpoint: str, timeout_seconds: float, payload: str | None = None) -> str:
    if not 0 < timeout_seconds <= 10:
        raise ValueError("Operation API timeout must be within ten seconds")
    executable = shutil.which("gh")
    if executable is None:
        raise ValueError("GitHub CLI unavailable")
    command = [
        executable,
        "api",
        "--hostname",
        "github.com",
        "--method",
        method,
        "--header",
        "Accept: application/vnd.github+json",
        "--header",
        "X-GitHub-Api-Version: 2026-03-10",
        endpoint,
    ]
    if payload is not None:
        command.extend(["--input", "-"])
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE if payload else subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    chunks: list[bytes] = []
    errors: list[str] = []

    def consume() -> None:
        used = 0
        try:
            assert process.stdout is not None
            while chunk := process.stdout.read(8192):
                used += len(chunk)
                if used > 256 * 1024:
                    errors.append("limit")
                    process.kill()
                    break
                chunks.append(chunk)
        except OSError:
            errors.append("read")

    worker = threading.Thread(target=consume, daemon=True)
    worker.start()
    try:
        if payload is not None:
            assert process.stdin is not None
            process.stdin.write(payload.encode("utf-8"))
            process.stdin.close()
        process.wait(timeout=timeout_seconds)
    except (subprocess.TimeoutExpired, OSError) as exc:
        process.kill()
        process.wait()
        raise ValueError("GitHub operation request failed or timed out") from exc
    finally:
        worker.join(timeout=2)
        if process.stdout is not None and not worker.is_alive():
            process.stdout.close()
    if worker.is_alive() or errors or process.returncode != 0:
        raise ValueError("GitHub operation request failed or exceeded output limit")
    return b"".join(chunks).decode("utf-8")


class GitHubOperationAdapter:
    def read_issue(self, repository: str, number: int, timeout_seconds: float) -> RemoteIssueState:
        # Reuse typed scope validation before constructing an endpoint.
        from pydantic import TypeAdapter

        TypeAdapter(RepositoryName).validate_python(repository, strict=True)
        if type(number) is not int or number < 1:
            raise ValueError("Invalid issue number")
        raw = decode_document(
            _request("GET", f"repos/{repository}/issues/{number}", timeout_seconds)
        )
        if (
            not isinstance(raw, dict)
            or "pull_request" in raw
            or raw.get("html_url") != f"https://github.com/{repository}/issues/{number}"
            or raw.get("number") != number
        ):
            raise ValueError("GitHub target is not the requested issue")
        title, body = raw.get("title"), raw.get("body")
        if body is None:
            body = ""
        if not isinstance(title, str) or not isinstance(body, str):
            raise ValueError("Invalid remote issue text")
        try:
            return RemoteIssueState.model_validate(
                {
                    "repository": repository,
                    "number": number,
                    "node_id": raw["node_id"],
                    "observed_at": timestamp(),
                    "updated_at": raw["updated_at"],
                    "state": raw["state"],
                    "title_sha256": hashlib.sha256(title.encode()).hexdigest(),
                    "body_sha256": hashlib.sha256(body.encode()).hexdigest(),
                    "labels": sorted(label["name"] for label in raw["labels"]),
                    "assignee_ids": sorted(user["id"] for user in raw["assignees"]),
                    "milestone_id": raw["milestone"]["id"] if raw.get("milestone") else None,
                }
            )
        except (KeyError, TypeError) as exc:
            raise ValueError("Malformed remote issue metadata") from exc

    def add_label(
        self,
        plan: ScrumOperationPlan,
        timeout_seconds: float,
        before_write: Callable[[], None],
    ) -> None:
        plan = ScrumOperationPlan.model_validate(plan.model_dump())
        repository, number = plan.expected.repository, plan.expected.number
        # Check existence explicitly; the API offers no atomic conditional write.
        label = decode_document(
            _request(
                "GET",
                f"repos/{repository}/labels/{quote(plan.label, safe='')}",
                timeout_seconds,
            )
        )
        if (
            not isinstance(label, dict)
            or label.get("name") != plan.label
            or label.get("archived_at")
        ):
            raise ValueError("Required operation label is absent or archived")
        before_write()
        _request(
            "POST",
            f"repos/{repository}/issues/{number}/labels",
            timeout_seconds,
            json.dumps({"labels": [plan.label]}),
        )
