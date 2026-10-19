"""Provider-independent team contracts and explicit human decisions."""

from typing import Literal, Self

from pydantic import ConfigDict, Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.project import ProjectInput
from ai_harness_compiler.models.qa import QAReviewReport
from ai_harness_compiler.models.scrum import SprintSnapshot

Role = Literal["analyst", "architect", "engineer", "quality", "security", "delivery"]
ToolName = Literal[
    "retrieve_context",
    "retrieve_memory",
    "requirements_audit",
    "architecture_review",
    "implementation_plan",
    "quality_review",
    "security_review",
    "delivery_plan",
]


class Persona(Contract):
    id: Role
    name: Text
    position: Text
    style: Text
    objective: Text
    tools: list[ToolName]
    required_tool: ToolName
    reports_to: Literal["human-product-owner"] = "human-product-owner"


class AgentDecision(Contract):
    action: Literal["tool", "finish"]
    tool: ToolName | None = None
    query: str = Field(default="", max_length=1000)
    summary: str = Field(default="", max_length=6000)

    @model_validator(mode="after")
    def validate_action(self) -> Self:
        if self.action == "tool" and self.tool is None:
            raise ValueError("Tool actions require a registered tool")
        if self.action == "finish" and (self.tool is not None or not self.summary.strip()):
            raise ValueError("Finish requires a summary and no tool")
        return self


class Finding(Contract):
    capability_id: Identifier | None = None
    severity: Literal["info", "warning", "blocker"]
    message: Text
    source: Text


class ToolResult(Contract):
    tool: ToolName
    summary: Text
    findings: list[Finding] = Field(default_factory=list)
    data: dict[str, object] = Field(default_factory=dict)


class AgentReport(Contract):
    agent_id: Role
    status: Literal["completed", "failed"]
    engine: Literal["local", "ollama", "codex-cli"]
    summary: Text
    observations: list[ToolResult]
    model_summary_is_advisory: bool = False


class TeamConfig(Contract):
    model_config = ConfigDict(hide_input_in_errors=True)
    schema_version: Literal["TeamRun/v1"] = "TeamRun/v1"
    project: ProjectInput
    selected: list[Identifier] = Field(min_length=1)
    request: Text = Field(max_length=4000)
    mode: Literal["prepare", "ask"] = "prepare"
    engine: Literal["local", "ollama", "codex-cli"] = "local"
    model: str | None = None
    max_steps: int = Field(default=5, ge=3, le=10)
    repository_root: Text
    scrum_snapshot: SprintSnapshot | None = None
    qa_report: QAReviewReport | None = None

    @model_validator(mode="after")
    def model_required(self) -> Self:
        if self.qa_report is not None:
            qa = QAReviewReport.model_validate(self.qa_report.model_dump())
            if (
                self.scrum_snapshot is None
                or qa.request.snapshot.model_dump() != self.scrum_snapshot.model_dump()
            ):
                raise ValueError("QA evidence must match the configured Scrum snapshot")
        if self.scrum_snapshot is not None:
            from ai_harness_compiler.scrum_observer import decode_document

            snapshot = SprintSnapshot.model_validate(self.scrum_snapshot.model_dump())
            source = next(s for s in snapshot.observation.sources if s.kind == "project")
            captured = ProjectInput.model_validate(decode_document(source.content or ""))
            if captured != self.project or snapshot.observation.project_id != self.project.id:
                raise ValueError("Scrum context differs from the configured project")
            if self.selected != [story.id for story in snapshot.stories]:
                raise ValueError("Scrum selection must match the observed stories in order")
            if self.mode != "ask":
                raise ValueError("Scrum context requires a dedicated Nexo ask session")
        if self.engine == "ollama" and not self.model:
            raise ValueError("Ollama mode requires an explicit installed model")
        if self.engine == "codex-cli" and not self.model:
            raise ValueError("Codex mode requires an explicit model in the run snapshot")
        return self


class POReview(Contract):
    decision: Literal["approve", "reject"]
    comment: Text
    actor: Literal["human-product-owner"] = "human-product-owner"
