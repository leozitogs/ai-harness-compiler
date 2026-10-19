"""Explicit read-only Scrum collection and offline re-reconciliation."""

import argparse

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.scrum import ScrumObservation, SprintSnapshot, StoryPRLink
from ai_harness_compiler.scrum_collection import GitHubCLIReader, collect, timestamp
from ai_harness_compiler.scrum_observer import observe


def execute(args: argparse.Namespace) -> int:
    if args.output.exists():
        raise FileExistsError("SCRUM_EXISTS: Choose a new output file")
    if args.scrum_command == "observe":
        links = []
        for value in args.pull_request:
            story, separator, number = value.partition("=")
            if not separator or not number.isascii() or not number.isdecimal():
                raise ValueError("SCRUM_LINK: Use story-id=positive-pr-number")
            links.append(StoryPRLink(story_id=story, number=int(number)))
        observation = collect(
            args.root,
            args.project_id,
            args.repo,
            args.sprint,
            reader=GitHubCLIReader() if args.github else None,
            links=links,
            max_age_seconds=args.max_age_seconds,
            max_remote_reads=args.max_remote_reads,
        )
    else:
        with args.input.open("rb") as stream:
            raw = stream.read(8 * 1024 * 1024 + 1)
        if len(raw) > 8 * 1024 * 1024:
            raise ValueError("SCRUM_INPUT_LIMIT: Saved snapshot exceeds 8 MiB")
        original = SprintSnapshot.model_validate_json(raw)
        data = original.observation.model_dump()
        data["observed_at"] = timestamp()
        observation = ScrumObservation.model_validate(data)
    snapshot = observe(observation)
    report = snapshot.model_dump()
    if args.scrum_command == "propose":
        from ai_harness_compiler.scrum_planning import propose

        report = propose(snapshot).model_dump()
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json_text(report))
    print(
        f"Saved read-only Scrum snapshot: {args.output}; "
        f"{len(snapshot.impediments)} diagnostics; no completion authority."
    )
    return 0
