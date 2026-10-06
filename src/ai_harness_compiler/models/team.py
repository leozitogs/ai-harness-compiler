"""Provider-independent team contracts and explicit human decisions."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.project import ProjectInput

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
    engine: Literal["local", "ollama"]
    summary: Text
    observations: list[ToolResult]
    model_summary_is_advisory: bool = False


class TeamConfig(Contract):
    schema_version: Literal["TeamRun/v1"] = "TeamRun/v1"
    project: ProjectInput
    selected: list[Identifier] = Field(min_length=1)
    request: Text = Field(max_length=4000)
    mode: Literal["prepare", "ask"] = "prepare"
    engine: Literal["local", "ollama"] = "local"
    model: str | None = None
    max_steps: int = Field(default=5, ge=3, le=10)
    repository_root: Text

    @model_validator(mode="after")
    def model_required(self) -> Self:
        if self.engine == "ollama" and not self.model:
            raise ValueError("Ollama mode requires an explicit installed model")
        return self


class POReview(Contract):
    decision: Literal["approve", "reject"]
    comment: Text
    actor: Literal["human-product-owner"] = "human-product-owner"
