"""Transport supervision is execution evidence, never semantic or human approval."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_eval import HumanDeclaration
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowRequestV4,
    SemanticFlowResultV4,
)


class TransportLimitsV1(Contract):
    call_timeout_seconds: int = Field(ge=1, le=300)
    cleanup_timeout_seconds: int = Field(ge=1, le=30)
    session_timeout_seconds: int = Field(ge=2, le=3600)
    max_worker_launches: Literal[2] = 2
    max_input_bytes: int = Field(default=1024 * 1024, ge=1024, le=2 * 1024 * 1024)
    max_output_bytes: int = Field(default=4 * 1024 * 1024, ge=1024, le=8 * 1024 * 1024)

    @model_validator(mode="after")
    def reserve_cleanup(self) -> Self:
        if self.session_timeout_seconds <= self.cleanup_timeout_seconds:
            raise ValueError("Session must reserve time for cleanup")
        return self


class TransportSourceV1(Contract):
    path: Text
    sha256: Digest


class SupervisedFlowRequestV1(Contract):
    schema_version: Literal["SupervisedFlowRequest/v1"] = "SupervisedFlowRequest/v1"
    flow: SemanticFlowRequestV4
    limits: TransportLimitsV1
    destination: Literal["codex-chatgpt-cli"] = "codex-chatgpt-cli"
    worker_command_sha256: Digest
    python_runtime: Text
    sources: list[TransportSourceV1] = Field(min_length=1, max_length=512)

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    @model_validator(mode="after")
    def source_inventory(self) -> Self:
        paths = [s.path for s in self.sources]
        if paths != sorted(set(paths)):
            raise ValueError("Source snapshot must be sorted and unique")
        if any(
            p not in {"pyproject.toml", "uv.lock"}
            and not (p.startswith("src/ai_harness_compiler/") and p.endswith(".py"))
            or ".." in p.split("/")
            or "\\" in p
            for p in paths
        ):
            raise ValueError("Source snapshot accepts repository implementation files only")
        return self


class SupervisedFlowAuthorizationV1(HumanDeclaration):
    schema_version: Literal["SupervisedFlowAuthorization/v1"] = "SupervisedFlowAuthorization/v1"
    request_sha256: Digest
    authorized: Literal[True]


class TransportReceiptV1(Contract):
    schema_version: Literal["TransportReceipt/v1"] = "TransportReceipt/v1"
    index: int = Field(ge=1, le=2)
    payload_sha256: Digest
    command_sha256: Digest
    granted_seconds: float = Field(ge=0, le=300)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    worker_pid: int | None = Field(default=None, ge=1)
    containment: Literal["none", "windows-job", "posix-session"]
    root_reaped: bool
    tree_termination_requested: bool
    exit_code: int | None = None
    response_sha256: Digest | None = None
    failure_code: (
        Literal[
            "session-budget",
            "input-limit",
            "spawn-failed",
            "containment-failed",
            "call-timeout",
            "output-limit",
            "worker-failed",
            "invalid-output",
            "cleanup-failed",
        ]
        | None
    ) = None
    status: Literal["succeeded", "failed"]

    @model_validator(mode="after")
    def observed_shape(self) -> Self:
        if (self.status == "succeeded") != (self.failure_code is None):
            raise ValueError("Transport status must preserve failure")
        if self.worker_pid is None and (
            self.root_reaped or self.tree_termination_requested or self.exit_code is not None
        ):
            raise ValueError("No process observations without a worker")
        if self.root_reaped != (self.exit_code is not None):
            raise ValueError("Root reaping requires observed exit code")
        if self.status == "succeeded" and (
            not self.worker_pid
            or not self.root_reaped
            or not self.tree_termination_requested
            or self.containment == "none"
            or self.exit_code != 0
            or not self.response_sha256
            or self.granted_seconds <= 0
        ):
            raise ValueError("Success requires response, containment and observed cleanup")
        return self


class SupervisedFlowReportV1(Contract):
    schema_version: Literal["SupervisedFlowReport/v1"] = "SupervisedFlowReport/v1"
    request: SupervisedFlowRequestV1
    authorization: SupervisedFlowAuthorizationV1
    flow_result: SemanticFlowResultV4
    receipts: list[TransportReceiptV1] = Field(max_length=2)
    session_elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    status: Literal["completed", "failed"]
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"
    model_qualification: Literal["not-established"] = "not-established"

    @model_validator(mode="after")
    def exact_bindings(self) -> Self:
        if (
            self.authorization.request_sha256 != self.request.sha256
            or self.flow_result.request != self.request.flow
            or len(self.receipts) != len(self.flow_result.calls)
            or [r.index for r in self.receipts] != list(range(1, len(self.receipts) + 1))
        ):
            raise ValueError("Supervised report must bind exact request and charged invocations")
        expected = (
            self.flow_result.status == "completed"
            and all(r.status == "succeeded" for r in self.receipts)
            and self.session_elapsed_seconds <= self.request.limits.session_timeout_seconds
        )
        if (self.status == "completed") != expected:
            raise ValueError("Completion must preserve transport/session failure")
        if any(r.granted_seconds > self.request.limits.call_timeout_seconds for r in self.receipts):
            raise ValueError("Granted call time cannot exceed the approved policy")
        if sum(r.elapsed_seconds for r in self.receipts) > self.session_elapsed_seconds:
            raise ValueError("Serial call durations cannot exceed total session duration")
        if any(r.status == "failed" for r in self.receipts[:-1]):
            raise ValueError("No continuation after first transport failure")
        for receipt in self.receipts:
            if receipt.status == "failed" and (
                self.flow_result.status != "failed"
                or (receipt.index == 1 and self.flow_result.analysis is not None)
                or (receipt.index == 2 and self.flow_result.audit is not None)
            ):
                raise ValueError("A failed transport cannot produce a validated stage artifact")
        if any(r.command_sha256 != self.request.worker_command_sha256 for r in self.receipts):
            raise ValueError("Receipts must bind the frozen worker command")
        human = self.authorization.model_dump(
            exclude={"schema_version", "request_sha256", "authorized"}
        )
        expected_authorization = SemanticFlowAuthorizationV4(
            **human, request_sha256=self.request.flow.sha256, authorized=True
        )
        if self.flow_result.authorization != expected_authorization:
            raise ValueError("Nested authorization must be the exact outer projection")
        return self
