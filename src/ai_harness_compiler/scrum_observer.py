"""Pure reconciliation of captured sources. No model, network, shell or writes."""

import json
from typing import Any, Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.scrum import (
    DeliveryEvidence,
    Impediment,
    ObservedPullRequest,
    ObservedStory,
    ScrumObservation,
    SprintID,
    SprintSnapshot,
    instant,
)


def decode_document(content: str) -> Any:
    def mapping(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate source JSON key")
            result[key] = value
        return result

    def constant(value: str) -> None:
        raise ValueError("Non-finite source JSON constant")

    try:
        return json.loads(content, object_pairs_hook=mapping, parse_constant=constant)
    except RecursionError as exc:
        raise ValueError("Source JSON nesting exceeds parser limit") from exc


class PlanProjection(Contract):
    """A typed projection; original metadata remains intact in captured content."""

    model_config = ConfigDict(extra="ignore", strict=True)
    id: SprintID
    status: Text
    goal: Text
    selected_capabilities: list[Identifier] = Field(min_length=1, max_length=64)
    declared_completed_capabilities: list[Identifier] = Field(default_factory=list, max_length=512)
    capability_status: dict[Identifier, Text] = Field(default_factory=dict)
    tracking: dict[str, Any] = Field(default_factory=dict)
    closure: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def unique_selection(self) -> Self:
        for items in (self.selected_capabilities, self.declared_completed_capabilities):
            if len(items) != len(set(items)):
                raise ValueError("Plan selection and completion declarations must be unique")
        return self


def issue_links(plan: PlanProjection, repository: str) -> dict[str, int]:
    result = {}
    mapping = plan.tracking.get("issues", {})
    if not isinstance(mapping, dict):
        raise ValueError("Plan issue tracking must be a mapping")
    for story, data in mapping.items():
        if not isinstance(data, dict):
            raise ValueError("Issue tracking entry must contain number and URL")
        number = data.get("number")
        if type(number) is not int or number < 1:
            raise ValueError("Issue tracking requires a positive integer number")
        if data.get("url") != f"https://github.com/{repository}/issues/{number}":
            raise ValueError("Plan issue tracking differs from expected repository")
        result[story] = number
    return result


def check_state(rows: object) -> Literal["all-success", "failure", "pending", "unknown"]:
    if not isinstance(rows, list) or not rows:
        return "unknown"
    states = []
    for row in rows:
        if not isinstance(row, dict):
            return "unknown"
        if row.get("__typename") == "CheckRun":
            states.append(row.get("conclusion") if row.get("status") == "COMPLETED" else "PENDING")
        elif row.get("__typename") == "StatusContext":
            states.append(row.get("state"))
        else:
            return "unknown"
    if any(
        s in {"FAILURE", "ERROR", "TIMED_OUT", "CANCELLED", "ACTION_REQUIRED", "STARTUP_FAILURE"}
        for s in states
    ):
        return "failure"
    if "PENDING" in states or "EXPECTED" in states:
        return "pending"
    return "all-success" if all(s == "SUCCESS" for s in states) else "unknown"


def derive(
    observation: ScrumObservation,
) -> tuple[
    str, Literal["achieved", "not-achieved", "unknown"], list[ObservedStory], list[Impediment]
]:
    sources = {s.kind: s for s in observation.sources if s.kind not in {"issue", "pull-request"}}
    usable: dict[str, DeliveryEvidence] = {}
    findings: list[Impediment] = []

    def finding(
        code: str,
        message: str,
        refs: list[str],
        story: str | None = None,
        severity: Literal["info", "warning", "blocker"] = "warning",
    ) -> None:
        findings.append(
            Impediment(
                id=f"observation-{len(findings) + 1}",
                code=code,
                severity=severity,
                story_id=story,
                message=message,
                evidence_ids=list(dict.fromkeys(refs)),
            )
        )

    for source in observation.sources:
        age = (instant(observation.observed_at) - instant(source.observed_at)).total_seconds()
        if source.status == "unavailable":
            finding(
                "source-unavailable",
                "Source unavailable; no current fact is inferred.",
                [source.id],
            )
        elif age > observation.max_age_seconds:
            finding(
                "source-stale",
                "Observation is older than the allowed freshness window.",
                [source.id],
            )
        else:
            usable[source.id] = source
    project_source, plan_source = sources["project"], sources["plan"]
    if project_source.id not in usable or plan_source.id not in usable:
        return "unknown", "unknown", [], findings
    try:
        project = ProjectInput.model_validate(decode_document(project_source.content or ""))
        plan = PlanProjection.model_validate(decode_document(plan_source.content or ""))
        if project.id != observation.project_id or plan.id != observation.sprint_id:
            raise ValueError("Project or sprint identity differs")
        by_id = {item.id: item for item in project.backlog}
        if any(
            len(by_id[id_].depends_on) > 128 for id_ in plan.selected_capabilities if id_ in by_id
        ):
            raise ValueError("Dependency inventory exceeds observation limit")
        if not set(plan.selected_capabilities + plan.declared_completed_capabilities).issubset(
            by_id
        ):
            raise ValueError("Plan refers to unknown capabilities")
        tracked_issues = issue_links(plan, observation.repository)
        if any(
            link.story_id not in plan.selected_capabilities
            for link in observation.pull_request_links
        ):
            raise ValueError("PR link belongs to an unselected story")
    except ValueError:
        finding(
            "planning-invalid",
            "Project, plan identity or tracked resources are invalid; planning facts unavailable.",
            [project_source.id, plan_source.id],
            severity="blocker",
        )
        return "unknown", "unknown", [], findings

    remote: dict[tuple[str, int], tuple[DeliveryEvidence, dict[str, Any]]] = {}
    for source in observation.sources:
        if source.kind not in {"issue", "pull-request"} or source.id not in usable:
            continue
        try:
            data = decode_document(source.content or "")
            if (
                not isinstance(data, dict)
                or type(data.get("number")) is not int
                or data.get("number") != source.number
                or data.get("url") != source.locator
            ):
                raise ValueError("Remote resource scope differs")
            if source.number is None:
                raise ValueError("Remote resource number absent")
            if source.kind == "issue":
                if data.get("state") not in {"OPEN", "CLOSED"}:
                    raise ValueError("Unknown issue state")
                if instant(data["updatedAt"]) > instant(source.observed_at):
                    raise ValueError("Issue update is later than the collection timestamp")
            else:
                ObservedPullRequest(
                    number=source.number,
                    state=data["state"],
                    head_sha=data["headRefOid"],
                    checks=check_state(data.get("statusCheckRollup")),
                    evidence_id=source.id,
                )
            remote[(source.kind, source.number)] = source, data
        except (ValueError, KeyError, TypeError):
            finding(
                "remote-invalid",
                "Captured remote resource has invalid identity or shape; ignored.",
                [source.id],
                severity="blocker",
            )

    work_source = sources["work-items"]
    if work_source.id in usable:
        try:
            work = decode_document(work_source.content or "")
            if (
                not isinstance(work, dict)
                or work.get("sprint_id") != plan.id
                or not isinstance(work.get("work_items"), list)
            ):
                raise ValueError("Work items belong to another sprint")
            for item in work["work_items"]:
                if (
                    not isinstance(item, dict)
                    or item.get("capability_id") not in plan.selected_capabilities
                ):
                    raise ValueError("Work item belongs to another selection")
                if item.get("status") == "done":
                    finding(
                        "task-done-unverified",
                        "Task claims Done; acceptance is not established by this observer.",
                        [work_source.id],
                        item["capability_id"],
                    )
        except (ValueError, TypeError):
            finding(
                "work-items-invalid",
                "Work item source cannot be reconciled with this sprint.",
                [work_source.id],
                severity="blocker",
            )

    stories = []
    for story_id in plan.selected_capabilities:
        declared = plan.capability_status.get(
            story_id, "done" if story_id in plan.declared_completed_capabilities else "unknown"
        )
        refs = [project_source.id, plan_source.id]
        issue_state: Literal["OPEN", "CLOSED", "unknown"] = "unknown"
        issue_number = tracked_issues.get(story_id)
        if issue_number and (pair := remote.get(("issue", issue_number))):
            source, issue_data = pair
            refs.append(source.id)
            issue_state = issue_data["state"]
        elif issue_number:
            finding(
                "issue-unobserved",
                "Tracked issue state has not been observed as fresh valid evidence.",
                [plan_source.id],
                story_id,
            )
        if declared == "done" or issue_state == "CLOSED":
            finding(
                "done-unverified",
                "Done or closed is declared; criteria acceptance and DoD are not established.",
                refs,
                story_id,
                "blocker",
            )
        if (declared == "done" and issue_state == "OPEN") or (
            declared not in {"done", "unknown"} and issue_state == "CLOSED"
        ):
            finding(
                "status-divergence",
                "Local completion declaration and observed issue lifecycle disagree.",
                refs,
                story_id,
            )
        if story_id in plan.declared_completed_capabilities and declared != "done":
            finding(
                "local-status-divergence",
                "Local completion inventory contradicts capability status.",
                [plan_source.id],
                story_id,
                "blocker",
            )
        unresolved = [
            d
            for d in by_id[story_id].depends_on
            if d not in plan.declared_completed_capabilities
            or (
                tracked_issues.get(d) is not None
                and (dep := remote.get(("issue", tracked_issues[d]))) is not None
                and dep[1]["state"] == "OPEN"
            )
        ]
        if unresolved:
            dependency_refs = [
                remote[("issue", tracked_issues[d])][0].id
                for d in unresolved
                if d in tracked_issues and ("issue", tracked_issues[d]) in remote
            ]
            finding(
                "dependency-unresolved",
                "Dependencies not declared complete or observed open: "
                + ", ".join(unresolved[:16]),
                [project_source.id, plan_source.id, *dependency_refs],
                story_id,
            )
        elif by_id[story_id].depends_on:
            finding(
                "dependency-acceptance-unverified",
                "Dependencies are declared complete; their acceptance is not certified.",
                [project_source.id, plan_source.id],
                story_id,
                "info",
            )
        pull_requests = []
        for link in observation.pull_request_links:
            if link.story_id != story_id:
                continue
            pair = remote.get(("pull-request", link.number))
            if pair is None:
                finding(
                    "pr-unobserved",
                    f"Explicitly linked PR {link.number} has no fresh valid observation.",
                    [plan_source.id],
                    story_id,
                )
                continue
            source, pr = pair
            refs.append(source.id)
            row = ObservedPullRequest(
                number=link.number,
                state=pr["state"],
                head_sha=pr["headRefOid"],
                checks=check_state(pr.get("statusCheckRollup")),
                evidence_id=source.id,
            )
            pull_requests.append(row)
            if row.state == "MERGED":
                finding(
                    "merged-without-acceptance",
                    "Merged PR is observed; acceptance criteria still require separate evidence.",
                    [source.id, plan_source.id],
                    story_id,
                )
            if row.checks == "all-success":
                finding(
                    "checks-not-acceptance",
                    "Checks succeeded; required policy and semantic acceptance remain unknown.",
                    [source.id],
                    story_id,
                    "info",
                )
            elif row.checks in {"failure", "pending"}:
                finding(
                    "checks-incomplete",
                    "PR checks contain failures or unfinished execution.",
                    [source.id],
                    story_id,
                )
        stories.append(
            ObservedStory(
                id=story_id,
                declared_status=declared,
                issue_state=issue_state,
                dependencies=by_id[story_id].depends_on,
                pull_requests=pull_requests,
                evidence_ids=list(dict.fromkeys(refs)),
            )
        )
    goal: Literal["achieved", "not-achieved", "unknown"] = "unknown"
    if type(plan.closure.get("goal_achieved")) is bool:
        goal = "achieved" if plan.closure["goal_achieved"] else "not-achieved"
    if plan.status.startswith("closed") and (
        goal == "not-achieved" or any(s.declared_status != "done" for s in stories)
    ):
        finding(
            "closed-with-carryover",
            "Sprint closed with unfinished/unverified work; no story is promoted to Done.",
            [plan_source.id],
        )
    return plan.status, goal, stories, findings


def observe(observation: ScrumObservation) -> SprintSnapshot:
    observation = ScrumObservation.model_validate(observation.model_dump())
    state, goal, stories, impediments = derive(observation)
    return SprintSnapshot(
        observation=observation,
        observation_sha256=observation.snapshot_sha256,
        declared_state=state,
        declared_goal_outcome=goal,
        stories=stories,
        impediments=impediments,
    )
