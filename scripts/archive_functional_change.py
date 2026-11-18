"""Append and inspect immutable functional changes and their scoped reviews."""

import argparse
import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile

from inspect_functional_change import MAX_INPUT_BYTES, _path, _read

from ai_harness_compiler.functional_changes import assess_functional_change
from ai_harness_compiler.models.functional_change import (
    FunctionalChangeReviewV1,
    FunctionalChangeV1,
)

FORMAT = "FunctionalChangeArchiveEntry/v1"


def _publish(path: Path, payload: object) -> None:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_INPUT_BYTES:
        raise ValueError("Archive entry exceeds the read limit")
    # Close before linking on Windows. Linking publishes atomically and fails if occupied.
    pending = NamedTemporaryFile(dir=path.parent, prefix=".pending-", delete=False)
    temporary_path = Path(pending.name)
    try:
        with pending:
            pending.write(encoded)
            pending.flush()
            os.fsync(pending.fileno())
        os.link(temporary_path, path)
    finally:
        temporary_path.unlink()


def _identity(change: FunctionalChangeV1) -> tuple[str, str]:
    return change.source.original_input.id, change.id


def _changes(directory: Path) -> list[FunctionalChangeV1]:
    changes: list[FunctionalChangeV1] = []
    for path in sorted(directory.glob("revision-*.json")):
        if (
            path.name != f"revision-{len(changes) + 1:012}.json"
            or path.is_symlink()
            or not path.is_file()
        ):
            raise ValueError("Archive revisions must be consecutive regular entries")
        entry = _read(path)
        if (
            not isinstance(entry, dict)
            or set(entry) != {"format", "parent_sha256", "change_sha256", "change"}
            or entry["format"] != FORMAT
        ):
            raise ValueError("Unexpected archive entry format")
        change = FunctionalChangeV1.model_validate(entry["change"])
        previous = changes[-1] if changes else None
        if (
            entry["parent_sha256"] != (previous.sha256 if previous else None)
            or entry["change_sha256"] != change.sha256
            or change.revision != len(changes) + 1
            or (previous is not None and _identity(change) != _identity(previous))
        ):
            raise ValueError("Broken archive revision chain")
        changes.append(change)
    return changes


def _review_path(directory: Path, revision: int) -> Path:
    return directory / f"review-{revision:012}.json"


def _require_exact_review(change: FunctionalChangeV1, review: FunctionalChangeReviewV1) -> None:
    report = assess_functional_change(change, review)
    if any(item.code == "stale-review" for item in report.blockers):
        raise ValueError("Review does not match this revision")
    if review.decision == "approved" and report.status != "approved":
        raise ValueError("Blocked revisions cannot be approved")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--archive", required=True)
    commands = parser.add_subparsers(dest="command", required=True)
    append = commands.add_parser("append")
    append.add_argument("--input", required=True)
    append.add_argument("--expected-head", required=True)
    review = commands.add_parser("review")
    review.add_argument("--input", required=True)
    show = commands.add_parser("show")
    show.add_argument("--revision", type=int)
    commands.add_parser("history")
    args = parser.parse_args()

    root = args.repository.resolve()
    directory = _path(root, args.archive).resolve()
    if directory == root or not directory.is_dir():
        raise ValueError("Archive requires an existing dedicated directory")
    changes = _changes(directory)
    head = changes[-1] if changes else None
    if args.command == "append":
        change = FunctionalChangeV1.model_validate(_read(_path(root, args.input)))
        parent = head.sha256 if head else None
        if (
            args.expected_head != (parent or "empty")
            or change.revision != len(changes) + 1
            or (head is not None and _identity(change) != _identity(head))
        ):
            raise ValueError("Unexpected head, revision or change identity")
        _publish(
            directory / f"revision-{change.revision:012}.json",
            dict(
                format=FORMAT,
                parent_sha256=parent,
                change_sha256=change.sha256,
                change=change.model_dump(mode="json"),
            ),
        )
        print(change.sha256)
        return

    if args.command == "history":
        print(json.dumps([dict(revision=c.revision, sha256=c.sha256) for c in changes]))
        return

    declaration = None
    if args.command == "review":
        declaration = FunctionalChangeReviewV1.model_validate(_read(_path(root, args.input)))
        revision = declaration.revision
    else:
        revision = len(changes) if args.revision is None else args.revision
    if not 1 <= revision <= len(changes):
        raise ValueError("Unknown archive revision")
    change = changes[revision - 1]
    path = _review_path(directory, revision)
    if args.command == "review":
        assert declaration is not None
        _require_exact_review(change, declaration)
        _publish(path, declaration.model_dump(mode="json"))
        print(declaration.decision)
        return

    if path.is_symlink() or (path.exists() and not path.is_file()):
        raise ValueError("Review must be a regular entry")
    if path.exists():
        declaration = FunctionalChangeReviewV1.model_validate(_read(path))
        _require_exact_review(change, declaration)
    print(json.dumps(assess_functional_change(change, declaration).model_dump(mode="json")))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, RecursionError):
        raise SystemExit(
            "FUNCTIONAL_ARCHIVE_FAILED: invalid input, revision conflict or storage error"
        ) from None
