"""Validate an explicit local change and emit a new readiness report, without execution."""

import argparse
import json
from pathlib import Path
from typing import Any

from ai_harness_compiler.functional_changes import assess_functional_change
from ai_harness_compiler.models.functional_change import (
    FunctionalChangeReviewV1,
    FunctionalChangeV1,
)

MAX_INPUT_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 2 * 1024 * 1024


def _path(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or path.is_symlink() or not path.resolve().is_relative_to(root):
        raise ValueError("Functional change path must remain inside repository")
    return path


def _read(path: Path) -> Any:
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError("Functional change input exceeds byte limit")
    return json.loads(raw)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("--input", required=True)
    parser.add_argument("--review")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    root = args.repository.resolve()
    source, target = _path(root, args.input), _path(root, args.output)
    change = FunctionalChangeV1.model_validate(_read(source))
    review = (
        FunctionalChangeReviewV1.model_validate(_read(_path(root, args.review)))
        if args.review
        else None
    )
    report = assess_functional_change(change, review)
    encoded = (
        json.dumps(report.model_dump(mode="json"), ensure_ascii=False, indent=2).encode("utf-8")
        + b"\n"
    )
    if len(encoded) > MAX_REPORT_BYTES:
        raise ValueError("Functional change report exceeds byte limit")
    # Parent must already exist. Exclusive output never replaces input or old evidence.
    with target.open("xb") as stream:
        stream.write(encoded)
    print(f"Functional readiness: {report.status}; {len(report.blockers)} blockers; tests not-run.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        raise SystemExit(
            "FUNCTIONAL_CHANGE_FAILED: input, review, bounds or output invalid"
        ) from None
