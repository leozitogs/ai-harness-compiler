"""Deterministic Scrum advice grounded in a validated observation."""

import hashlib
from pathlib import Path

from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.scrum import LOCAL_KINDS, SprintSnapshot, instant
from ai_harness_compiler.models.scrum_planning import ScrumActionProposal, ScrumPlanningReport
from ai_harness_compiler.scrum_observer import PlanProjection, decode_document


def derive_proposals(snapshot: SprintSnapshot) -> list[ScrumActionProposal]:
    sources = {s.kind: s for s in snapshot.observation.sources if s.kind in LOCAL_KINDS}
    evidence = [s.id for s in snapshot.observation.sources]
    try:
        plan = PlanProjection.model_validate(decode_document(sources["plan"].content or ""))
        project = ProjectInput.model_validate(decode_document(sources["project"].content or ""))
        goal = plan.goal
    except ValueError:
        project = None
        goal = "Recover valid project and sprint sources before choosing scope."
    proposals = []
    # Invalid/stale observations contain no trusted story projection. Never recover
    # selected stories directly from an otherwise readable, untrusted plan.
    for index, story in enumerate(snapshot.stories, 1):
        item = next((b for b in project.backlog if b.id == story.id), None) if project else None
        proposals.append(
            ScrumActionProposal(
                id=f"refine-{index}",
                kind="refinement",
                goal=goal,
                story_ids=[story.id],
                dependencies=story.dependencies,
                acceptance_criteria=item.acceptance_criteria if item else [],
                evidence_ids=list(dict.fromkeys([sources["project"].id, *story.evidence_ids])),
                diagnostic_ids=[d.id for d in snapshot.impediments if d.story_id == story.id],
                recommendation=(
                    "Review source criteria, unresolved dependencies "
                    "and acceptance evidence with the PO."
                ),
                alternatives=[
                    "Refine before selecting scope.",
                    "Defer explicitly and retain the original criteria.",
                ],
                decision_recipient="human-product-owner",
            )
        )
    proposals.append(
        ScrumActionProposal(
            id="planning-capacity",
            kind="planning",
            goal=goal,
            story_ids=[s.id for s in snapshot.stories],
            evidence_ids=evidence,
            diagnostic_ids=[d.id for d in snapshot.impediments],
            recommendation=(
                "Ask Developers for available capacity and dependency feasibility "
                "before proposing a Sprint Backlog; no forecast is established."
            ),
            alternatives=[
                "Confirm capacity and discuss feasible scope with the PO.",
                "Keep planning pending while missing information is collected.",
            ],
            decision_recipient="developers",
        )
    )
    proposals.append(
        ScrumActionProposal(
            id="review-evidence",
            kind="review",
            goal=goal,
            story_ids=[s.id for s in snapshot.stories],
            evidence_ids=evidence,
            diagnostic_ids=[d.id for d in snapshot.impediments],
            recommendation=(
                f"Review declared outcome ({snapshot.declared_goal_outcome}) and carryover; "
                "CI and merged PRs do not establish criterion acceptance."
            ),
            alternatives=[
                "Inspect evidence and record a separate human decision.",
                "Request missing evidence and retain unresolved work as carryover.",
            ],
            decision_recipient="human-product-owner",
        )
    )
    return proposals


def propose(snapshot: SprintSnapshot) -> ScrumPlanningReport:
    snapshot = SprintSnapshot.model_validate(snapshot.model_dump())
    return ScrumPlanningReport(snapshot=snapshot, proposals=derive_proposals(snapshot))


def assert_current(snapshot: SprintSnapshot, root: Path, now: str) -> None:
    """Reject stale or changed local sources before running/reviewing Nexo.

    Remote content remains captured evidence, not a claim of current GitHub state.
    Collection age is checked; no hidden remote refresh occurs.
    """
    snapshot = SprintSnapshot.model_validate(snapshot.model_dump())
    root = root.resolve()
    locations = {
        "project": "project-definition/project.yaml",
        "plan": f"planning/{snapshot.observation.sprint_id}.json",
        "work-items": f"planning/{snapshot.observation.sprint_id}.work-items.json",
        "policy": "docs/delivery/scrum.md",
        "memory-index": "knowledge/INDEX.md",
    }
    for source in snapshot.observation.sources:
        age = (instant(now) - instant(source.observed_at)).total_seconds()
        if age < 0 or age > snapshot.observation.max_age_seconds:
            raise ValueError("Scrum evidence expired or lies in the future; recollect sources")
        if source.kind not in LOCAL_KINDS:
            continue
        if source.locator != locations[source.kind]:
            raise ValueError("Scrum source is outside the fixed collection allowlist")
        if source.status != "observed":
            raise ValueError("Scrum local context is unavailable; recollect sources")
        path = (root / source.locator).resolve()
        if not path.is_relative_to(root):
            raise ValueError("Scrum source escapes repository")
        with path.open("rb") as stream:
            content = stream.read(256 * 1024 + 1)
        expected = source.revision if source.kind == "project" else source.content_sha256
        if len(content) > 256 * 1024 or hashlib.sha256(content).hexdigest() != expected:
            raise ValueError("Scrum source changed; recollect before review")
        if source.kind == "project":
            from ai_harness_compiler.intake import parse_project_manifest

            captured = ProjectInput.model_validate(decode_document(source.content or ""))
            if parse_project_manifest(content) != captured:
                raise ValueError("Scrum normalized project differs from current source")
