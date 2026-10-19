"""Explicit, bounded Git capture; source bytes are data, never instructions."""

import hashlib
import os
import signal
import subprocess
import sys
import threading
from pathlib import Path

from ai_harness_compiler.models.qa import QAReviewRequest, ReviewSource, safe_review_path
from ai_harness_compiler.models.scrum import SprintSnapshot, instant
from ai_harness_compiler.scrum_collection import timestamp
from ai_harness_compiler.scrum_planning import assert_current


def stop_tree(process: subprocess.Popen[bytes]) -> None:
    if sys.platform == "win32":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=5,
                check=False,
            )
        except (OSError, subprocess.TimeoutExpired):
            process.kill()
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def bounded_process(
    command: list[str], root: Path, timeout: float, limit: int
) -> tuple[int | None, str, str]:
    process = subprocess.Popen(
        command,
        cwd=root,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        start_new_session=sys.platform != "win32",
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )
    chunks: list[bytes] = []
    exceeded: list[bool] = []

    def consume() -> None:
        used = 0
        assert process.stdout is not None
        while chunk := process.stdout.read(4096):
            remaining = max(0, limit - used)
            chunks.append(chunk[:remaining])
            used += len(chunk)
            if used > limit:
                exceeded.append(True)
                stop_tree(process)
                break

    reader = threading.Thread(target=consume, daemon=True)
    reader.start()
    status = "completed"
    try:
        process.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_tree(process)
        process.wait()
        status = "timed-out"
    finally:
        reader.join(timeout=2)
        if process.stdout is not None and not reader.is_alive():
            process.stdout.close()
    if reader.is_alive() or exceeded:
        stop_tree(process)
        status = "output-limit"
    # UTF-8 replacement may expand bytes; enforce the limit on the final text too.
    output = b"".join(chunks).decode("utf-8", errors="replace")
    output = output.encode()[:limit].decode("utf-8", errors="ignore")
    return process.returncode, output, status


def git(root: Path, *args: str, limit: int = 65536) -> str:
    code, output, status = bounded_process(
        [
            "git",
            "--no-optional-locks",
            "-c",
            "core.fsmonitor=false",
            "--no-pager",
            "--no-replace-objects",
            *args,
        ],
        root,
        10,
        limit,
    )
    if code != 0 or status != "completed":
        raise ValueError("QA Git read failed or exceeded budget")
    return output


def capture(
    root: Path,
    snapshot: SprintSnapshot,
    base: str,
    head: str,
    author: str,
    paths: list[str],
    *,
    check_ids: list[str] | None = None,
) -> QAReviewRequest:
    from pydantic import TypeAdapter

    from ai_harness_compiler.models.qa import Commit

    TypeAdapter(Commit).validate_python(base, strict=True)
    TypeAdapter(Commit).validate_python(head, strict=True)
    root = root.resolve()
    if Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() != root:
        raise ValueError("QA root must be the repository root")
    if not paths:
        raise ValueError("Select explicit review source paths; no implicit repository ingestion")
    if len(paths) > 32 or len(set(paths)) != len(paths):
        raise ValueError("Select at most 32 unique source paths")
    for revision in (base, head):
        if git(root, "rev-parse", f"{revision}^{{commit}}").strip() != revision:
            raise ValueError("QA revision must resolve to the exact commit")
    sources = []
    for path in paths:
        safe_review_path(path)
        tree = git(root, "ls-tree", head, "--", path).split()
        if len(tree) < 4 or tree[0] not in {"100644", "100755"}:
            raise ValueError("QA sources must be regular tracked files")
        content = git(root, "show", f"{head}:{path}")
        sources.append(
            ReviewSource(
                path=path, content=content, sha256=hashlib.sha256(content.encode()).hexdigest()
            )
        )
    changed = git(root, "diff", "--no-ext-diff", "--name-only", base, head, "--").splitlines()
    diff = git(
        root, "diff", "--no-ext-diff", "--no-textconv", "--unified=3", base, head, "--", *paths
    )
    data: dict[str, object] = {
        "snapshot": snapshot.model_dump(),
        "base_commit": base,
        "head_commit": head,
        "author": author,
        "captured_at": timestamp(),
        "sources": [s.model_dump() for s in sources],
        "diff": diff,
        "diff_sha256": hashlib.sha256(diff.encode()).hexdigest(),
        "excluded_paths": [p for p in changed if p not in paths],
    }
    if check_ids is not None:
        data["check_ids"] = check_ids
    request = QAReviewRequest.model_validate(data)
    assert_current_request(request, root, timestamp())
    return request


def assert_current_request(request: QAReviewRequest, root: Path, now: str) -> None:
    request = QAReviewRequest.model_validate(request.model_dump())
    assert_current(request.snapshot, root, now)
    age = (instant(now) - instant(request.captured_at)).total_seconds()
    if not 0 <= age <= request.max_age_seconds:
        raise ValueError("QA request expired or lies in the future")
    root = root.resolve()
    if git(root, "rev-parse", "HEAD").strip() != request.head_commit:
        raise ValueError("QA head changed; capture a new review")
    if Path(git(root, "rev-parse", "--show-toplevel").strip()).resolve() != root:
        raise ValueError("QA root must be the repository root")
    if git(root, "rev-parse", f"{request.base_commit}^{{commit}}").strip() != request.base_commit:
        raise ValueError("QA base revision does not match an existing commit")
    if git(
        root, "status", "--porcelain", "--untracked-files=normal", "--ignore-submodules=all"
    ).strip():
        raise ValueError("QA requires a clean tracked revision and no untracked source files")
    if (
        git(
            root,
            "diff",
            "--no-ext-diff",
            "--no-textconv",
            "--unified=3",
            request.base_commit,
            request.head_commit,
            "--",
            *(s.path for s in request.sources),
        )
        != request.diff
    ):
        raise ValueError("QA captured diff differs from Git revisions")
    entries = git(
        root, "ls-tree", "-z", request.head_commit, "--", *(s.path for s in request.sources)
    ).split("\0")
    tree = {}
    for entry in entries:
        if entry:
            metadata_text, _, name = entry.partition("\t")
            tree[name] = metadata_text.split()
    for source in request.sources:
        path = (root / source.path).resolve()
        if not path.is_relative_to(root):
            raise ValueError("QA source escapes repository")
        with path.open("rb") as stream:
            content = stream.read(65537)
        if len(content) > 65536 or hashlib.sha256(content).hexdigest() != source.sha256:
            raise ValueError("QA source differs from the captured revision")
        # The working tree alone cannot authenticate an imported capture.
        metadata = tree.get(source.path, [])
        if len(metadata) != 3 or metadata[0] not in {"100644", "100755"}:
            raise ValueError("QA source is not a regular tracked file")
        blob = hashlib.sha1(f"blob {len(content)}\0".encode() + content).hexdigest()
        if metadata[1:] != ["blob", blob]:
            raise ValueError("QA capture differs from Git revision")
