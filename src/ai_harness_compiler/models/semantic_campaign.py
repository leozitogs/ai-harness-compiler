"""A global development budget is separate from case approval and semantic success."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest, canonical_project_digest
from ai_harness_compiler.models.semantic_eval import HumanDeclaration, semantic_snapshot_digest
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowRequestV4,
    SemanticFlowResultV4,
)
from ai_harness_compiler.models.semantic_preflight import preflight_case
from ai_harness_compiler.models.supervised_transport import (
    SupervisedFlowRequestV1,
    TransportLimitsV1,
    TransportReceiptV1,
    TransportSourceV1,
)


class SemanticCampaignRequestV1(Contract):
    schema_version: Literal["SemanticCampaignRequest/v1"] = "SemanticCampaignRequest/v1"
    campaign_id: Identifier
    corpus_source: Text
    corpus_sha256: Digest
    flows: list[SemanticFlowRequestV4] = Field(min_length=1, max_length=8)
    limits: TransportLimitsV1
    max_calls: int = Field(ge=2, le=16)
    destination: Literal["codex-chatgpt-cli"] = "codex-chatgpt-cli"
    worker_command_sha256: Digest
    python_runtime: Text
    sources: list[TransportSourceV1] = Field(min_length=1, max_length=512)
    split: Literal["development"] = "development"

    @property
    def sha256(self) -> str:
        return canonical_project_digest(self.model_dump())

    def supervision(self, index: int) -> SupervisedFlowRequestV1:
        return SupervisedFlowRequestV1(
            flow=self.flows[index],
            limits=self.limits,
            destination=self.destination,
            worker_command_sha256=self.worker_command_sha256,
            python_runtime=self.python_runtime,
            sources=self.sources,
        )

    @model_validator(mode="after")
    def bounded_approved_sequence(self) -> Self:
        from ai_harness_compiler.grounding import extract_grounding
        from ai_harness_compiler.semantic_generation_programs import resolve_program

        path = self.corpus_source
        if (
            not path.startswith("evals/")
            or not path.endswith(".json")
            or "\\" in path
            or any(p in {"", ".", ".."} for p in path.split("/"))
        ):
            raise ValueError("Campaign corpus must be an explicit repository eval JSON file")
        if self.max_calls != 2 * len(self.flows):
            raise ValueError("Global call ceiling must bind exactly two stages per case")
        for key in (
            lambda f: f.run_id,
            lambda f: f.case.id,
            lambda f: semantic_snapshot_digest(f.case.project),
        ):
            values = [key(f) for f in self.flows]
            if len(set(values)) != len(values):
                raise ValueError("Campaign run, case and input identities must be unique")
        first = self.flows[0]
        version = resolve_program(
            extract_grounding(first.case.project), first.generation_program_sha256
        )
        for index, flow in enumerate(self.flows):
            self.supervision(index)  # Reuse source-inventory constraints without executing.
            if (
                not flow.case.expectations_approval
                or not flow.rubric.approval
                or flow.rubric != first.rubric
                or flow.requested_model != first.requested_model
                or resolve_program(
                    extract_grounding(flow.case.project), flow.generation_program_sha256
                )
                != version
                or preflight_case(flow.case, "SemanticAnalysis/v4").status != "compatible"
            ):
                raise ValueError("Campaign requires approved cases and one rubric/model/program")
        return self


class SemanticCampaignAuthorizationV1(HumanDeclaration):
    schema_version: Literal["SemanticCampaignAuthorization/v1"] = "SemanticCampaignAuthorization/v1"
    request_sha256: Digest
    authorized: Literal[True]


def flow_authorization(
    request: SemanticFlowRequestV4,
    authorization: SemanticCampaignAuthorizationV1,
) -> SemanticFlowAuthorizationV4:
    """Project exact campaign authorization onto its nested flow, without new consent."""
    fields = authorization.model_dump(exclude={"schema_version", "request_sha256", "authorized"})
    return SemanticFlowAuthorizationV4(**fields, request_sha256=request.sha256, authorized=True)


class SemanticCampaignCallV1(Contract):
    index: int = Field(ge=1, le=16)
    flow_index: int = Field(ge=0, le=7)
    stage: Literal["analysis", "audit"]
    payload_sha256: Digest
    started_offset_seconds: float = Field(ge=0, allow_inf_nan=False)
    finished_offset_seconds: float = Field(ge=0, allow_inf_nan=False)
    receipt: TransportReceiptV1 | None = None
    interruption: Literal["cancelled", "transport-exception"] | None = None

    @model_validator(mode="after")
    def observed_only(self) -> Self:
        if (self.receipt is None) == (self.interruption is None):
            raise ValueError("Call must preserve a receipt or an explicit unobserved interruption")
        if self.finished_offset_seconds < self.started_offset_seconds:
            raise ValueError("Call cannot finish before its debit")
        if self.receipt and (
            self.receipt.index != (1 if self.stage == "analysis" else 2)
            or self.receipt.payload_sha256 != self.payload_sha256
            or self.receipt.elapsed_seconds
            > self.finished_offset_seconds - self.started_offset_seconds
        ):
            raise ValueError("Call identity and duration must agree with its receipt")
        return self


class SemanticCampaignReportV1(Contract):
    schema_version: Literal["SemanticCampaignReport/v1"] = "SemanticCampaignReport/v1"
    request: SemanticCampaignRequestV1
    authorization: SemanticCampaignAuthorizationV1
    results: list[SemanticFlowResultV4] = Field(max_length=8)
    calls: list[SemanticCampaignCallV1] = Field(max_length=16)
    elapsed_seconds: float = Field(ge=0, allow_inf_nan=False)
    status: Literal["completed", "failed"]
    failure_code: Literal["case-failed", "budget-exhausted", "cancelled"] | None = None
    budget_closed: Literal[True] = True
    model_qualification: Literal["not-established"] = "not-established"
    compilation_eligibility: Literal["not-authorized"] = "not-authorized"

    @model_validator(mode="after")
    def exact_global_accounting(self) -> Self:
        req = self.request
        if self.authorization.request_sha256 != req.sha256:
            raise ValueError("Campaign authorization must bind the exact request")
        if len(self.results) > len(req.flows) or len(self.calls) > req.max_calls:
            raise ValueError("Campaign exceeds approved cases or global call ceiling")
        expected_calls: list[tuple[int, str]] = []
        for index, result in enumerate(self.results):
            if (
                result.request != req.flows[index]
                or result.authorization != flow_authorization(req.flows[index], self.authorization)
                or (index < len(self.results) - 1 and result.status != "completed")
            ):
                raise ValueError(
                    "Results must be the exact authorized prefix, without continuation"
                )
            expected_calls.extend((index, call.stage) for call in result.calls)
        if [(c.flow_index, c.stage) for c in self.calls] != expected_calls:
            raise ValueError("Every nested invocation needs exactly one global debit")
        end = 0.0
        for index, call in enumerate(self.calls, 1):
            if (
                call.index != index
                or call.started_offset_seconds < end
                or call.finished_offset_seconds > self.elapsed_seconds
            ):
                raise ValueError(
                    "Global invocations must be serial, ordered and within elapsed time"
                )
            end = call.finished_offset_seconds
            if call.receipt and (
                call.receipt.command_sha256 != req.worker_command_sha256
                or call.receipt.granted_seconds > req.limits.call_timeout_seconds
                or call.receipt.granted_seconds
                > max(
                    0.0,
                    req.limits.session_timeout_seconds
                    - call.started_offset_seconds
                    - req.limits.cleanup_timeout_seconds,
                )
            ):
                raise ValueError("Worker grant exceeds frozen command or remaining global time")
            if (
                call.receipt
                and call.receipt.worker_pid
                and (
                    call.started_offset_seconds + req.limits.cleanup_timeout_seconds
                    >= req.limits.session_timeout_seconds
                )
            ):
                raise ValueError("No worker may start without remaining global execution time")
            bad = call.interruption is not None or (
                call.receipt and call.receipt.status == "failed"
            )
            if bad:
                result = self.results[call.flow_index]
                if (
                    index != len(self.calls)
                    or result.status != "failed"
                    or (call.stage == "analysis" and result.analysis is not None)
                    or (call.stage == "audit" and result.audit is not None)
                ):
                    raise ValueError("Failed invocation cannot yield an artifact or continuation")
        complete = (
            len(self.results) == len(req.flows)
            and all(r.status == "completed" for r in self.results)
            and self.elapsed_seconds <= req.limits.session_timeout_seconds
        )
        if (self.status == "completed") != complete or complete != (self.failure_code is None):
            raise ValueError(
                "Campaign completion must preserve all technical and deadline failures"
            )
        interrupted = any(c.interruption == "cancelled" for c in self.calls)
        if self.failure_code == "case-failed" and (
            not self.results or self.results[-1].status != "failed"
        ):
            raise ValueError("Case failure requires a failed nested result")
        if self.failure_code == "cancelled" and not interrupted:
            raise ValueError("Cancellation requires an observed interrupted invocation")
        if self.failure_code == "budget-exhausted" and (
            self.elapsed_seconds + req.limits.cleanup_timeout_seconds
            < req.limits.session_timeout_seconds
            and not any(
                c.receipt and c.receipt.failure_code == "session-budget" for c in self.calls
            )
        ):
            raise ValueError("Budget failure requires observed insufficient remaining time")
        if interrupted and self.failure_code != "cancelled":
            raise ValueError("Cancellation must remain explicit")
        return self
