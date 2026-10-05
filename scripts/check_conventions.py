"""Enforce repository commit/PR-title and branch conventions without third-party tools."""

import argparse
import os
import re
import subprocess
from pathlib import Path

HEADER = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
    r"(\([a-z0-9][a-z0-9_-]*\))?!?: [^\s].*$"
)
BRANCH = re.compile(
    r"^(feat|fix|docs|refactor|perf|test|build|ci|chore)/"
    r"(ahc-[0-9]{3}|infra)-[a-z0-9]+(?:-[a-z0-9]+)*$"
)


def check_message(message: str) -> None:
    header = message.splitlines()[0] if message else ""
    if len(header) > 100 or not HEADER.fullmatch(header) or header.rstrip() != header:
        raise ValueError(
            "Expected Conventional Commit header (max 100 chars): feat(scope): summary"
        )


def check_branch(branch: str) -> None:
    if branch == "main" or re.fullmatch(r"dependabot/[A-Za-z0-9_./-]+", branch):
        return
    if len(branch) > 100 or not BRANCH.fullmatch(branch):
        raise ValueError(
            "Expected branch: feat/ahc-001-short-description or ci/infra-short-description"
        )


def check_ci() -> None:
    check_branch(os.environ["BRANCH_NAME"])
    if os.environ.get("EVENT_NAME") == "pull_request":
        check_message(os.environ["PR_TITLE"])
    head = os.environ["HEAD_SHA"]
    base = os.environ.get("BASE_SHA", "")
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("Invalid head SHA")
    if base and not re.fullmatch(r"[0-9a-f]{40}", base):
        raise ValueError("Invalid base SHA")
    revision = head if not base or set(base) == {"0"} else f"{base}..{head}"
    result = subprocess.run(
        ["git", "log", "--no-merges", "--format=%s", revision],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )
    for header in result.stdout.splitlines():
        check_message(header)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--message")
    parser.add_argument("--message-file", type=Path)
    parser.add_argument("--branch")
    parser.add_argument("--ci", action="store_true")
    args = parser.parse_args()
    if not any([args.message is not None, args.message_file, args.branch, args.ci]):
        parser.error("Provide --message, --message-file, --branch or --ci")
    try:
        if args.message is not None:
            check_message(args.message)
        if args.message_file:
            check_message(args.message_file.read_text(encoding="utf-8"))
        if args.branch:
            check_branch(args.branch)
        if args.ci:
            check_ci()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"Convention check failed: {exc}")
        return 1
    print("Repository conventions passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
