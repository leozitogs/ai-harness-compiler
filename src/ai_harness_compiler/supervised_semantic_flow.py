"""Explicitly authorized, source-frozen supervision of the additive v4 flow."""

import hashlib
import sys
from pathlib import Path
from time import monotonic
from typing import Any

from ai_harness_compiler.adapters.process_supervisor import invoke_json_worker
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowRequestV4,
)
from ai_harness_compiler.models.semantic_preflight import preflight_case
from ai_harness_compiler.models.supervised_transport import (
    SupervisedFlowAuthorizationV1,
    SupervisedFlowReportV1,
    SupervisedFlowRequestV1,
    TransportLimitsV1,
    TransportReceiptV1,
    TransportSourceV1,
)
from ai_harness_compiler.semantic_flow_runner_v4 import (
    _read,
    _write,
    run_semantic_flow_v4,
    validate_semantic_flow_v4,
)
from ai_harness_compiler.semantic_generation_programs import program_prompt
from ai_harness_compiler.semantic_generation_v4 import (
    audit_prompt_v5,
    audit_schema_v5,
    generation_schema_v4,
)


def worker_command() -> list[str]:
    return [sys.executable, "-I", "-m", "ai_harness_compiler.adapters.semantic_worker_v4"]


def prepare_supervised_flow(
    repository: Path, flow: SemanticFlowRequestV4, limits: TransportLimitsV1
) -> SupervisedFlowRequestV1:
    """Capture implementation metadata only; no assets, provider, approval or execution."""
    return SupervisedFlowRequestV1(
        flow=flow,
        limits=limits,
        sources=transport_sources(repository),
        worker_command_sha256=canonical_project_digest({"argv": worker_command()}),
        python_runtime=sys.version,
    )


def transport_sources(repository: Path) -> list[TransportSourceV1]:
    root = repository.resolve()
    paths = [
        *root.joinpath("src/ai_harness_compiler").rglob("*.py"),
        root / "pyproject.toml",
        root / "uv.lock",
    ]
    result = []
    for path in sorted(paths):
        if not path.resolve().is_relative_to(root) or path.is_symlink():
            raise ValueError("Transport source escapes repository")
        raw = path.read_bytes()
        if len(raw) > 2 * 1024 * 1024:
            raise ValueError("Transport source exceeds byte limit")
        result.append(
            TransportSourceV1(
                path=path.relative_to(root).as_posix(), sha256=hashlib.sha256(raw).hexdigest()
            )
        )
    return sorted(result, key=lambda s: s.path)


def _directory(repository: Path, run_id: str) -> Path:
    directory = repository.resolve() / ".factory" / "supervised-v4-runs" / run_id
    if not directory.resolve().is_relative_to(repository.resolve()):
        raise ValueError("Supervised output escapes repository")
    return directory


def _validate_request(repository: Path, request: SupervisedFlowRequestV1) -> None:
    if (
        request.sources != transport_sources(repository)
        or request.worker_command_sha256 != canonical_project_digest({"argv": worker_command()})
        or request.python_runtime != sys.version
    ):
        raise ValueError("Transport source, worker command or Python runtime changed")
    # Reject a different installed package even when the repository source freeze matches.
    package = Path(__file__).resolve().parent
    for source in request.sources:
        if source.path.startswith("src/ai_harness_compiler/"):
            running = package / source.path.removeprefix("src/ai_harness_compiler/")
            if hashlib.sha256(running.read_bytes()).hexdigest() != source.sha256:
                raise ValueError("Running implementation differs from frozen repository")


def _inner_authorization(
    request: SupervisedFlowRequestV1, authorization: SupervisedFlowAuthorizationV1
) -> SemanticFlowAuthorizationV4:
    # The exact outer authorization explicitly covers this nested flow, destination,
    # sources and limits. This projection is not a new or transferred human approval.
    fields = authorization.model_dump(exclude={"schema_version", "request_sha256", "authorized"})
    return SemanticFlowAuthorizationV4(
        **fields, request_sha256=request.flow.sha256, authorized=True
    )


def run_supervised_flow(
    repository: Path,
    request: SupervisedFlowRequestV1,
    authorization: SupervisedFlowAuthorizationV1,
) -> SupervisedFlowReportV1:
    started = monotonic()
    request = SupervisedFlowRequestV1.model_validate(request.model_dump())
    authorization = SupervisedFlowAuthorizationV1.model_validate(authorization.model_dump())
    _validate_request(repository, request)
    if (
        authorization.request_sha256 != request.sha256
        or not request.flow.case.expectations_approval
        or not request.flow.rubric.approval
        or preflight_case(request.flow.case, "SemanticAnalysis/v4").status != "compatible"
    ):
        raise ValueError("New exact supervision authorization and approved expectations required")
    directory = _directory(repository, request.flow.run_id)
    claim = repository.resolve() / ".factory" / "supervised-v4-claims" / f"{request.sha256}.json"
    if not claim.resolve().is_relative_to(repository.resolve()):
        raise ValueError("Supervised claim escapes repository")
    claim.parent.mkdir(parents=True, exist_ok=True)
    _write(claim, authorization.model_dump())
    directory.mkdir(parents=True, exist_ok=False)
    _write(directory / "request.json", request.model_dump())
    _write(directory / "authorization.json", authorization.model_dump())
    receipts: list[TransportReceiptV1] = []
    deadline = started + request.limits.session_timeout_seconds

    class SupervisedGenerator:
        def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
            index = len(receipts) + 1
            if index > request.limits.max_worker_launches or any(
                r.status == "failed" for r in receipts
            ):
                raise ValueError("Transport cannot retry or continue after failure")
            payload = dict(
                model=request.flow.requested_model,
                prompt=prompt,
                response_schema=schema,
                timeout_seconds=request.limits.call_timeout_seconds,
            )
            _write(
                directory / f"attempt-{index}.json",
                dict(index=index, payload_sha256=canonical_project_digest(payload)),
            )
            outcome = invoke_json_worker(
                worker_command(),
                payload,
                cwd=repository.resolve(),
                limits=request.limits,
                session_deadline=deadline,
                index=index,
            )
            _write(directory / f"receipt-{index}.json", outcome.receipt.model_dump())
            receipts.append(outcome.receipt)
            if outcome.response is None:
                raise ValueError("SUPERVISED_TRANSPORT_FAILED")
            return outcome.response

    flow_result = run_semantic_flow_v4(
        repository, request.flow, _inner_authorization(request, authorization), SupervisedGenerator
    )
    elapsed = monotonic() - started
    report = SupervisedFlowReportV1(
        request=request,
        authorization=authorization,
        flow_result=flow_result,
        receipts=receipts,
        session_elapsed_seconds=elapsed,
        status="completed"
        if flow_result.status == "completed" and elapsed <= request.limits.session_timeout_seconds
        else "failed",
    )
    _write(directory / "report.json", report.model_dump())
    return report


def validate_supervised_flow(repository: Path, run_id: str) -> SupervisedFlowReportV1:
    from pydantic import TypeAdapter

    from ai_harness_compiler.grounding import extract_grounding
    from ai_harness_compiler.models.base import Identifier

    TypeAdapter(Identifier).validate_python(run_id)
    directory = _directory(repository, run_id)
    report = SupervisedFlowReportV1.model_validate(_read(directory / "report.json"))
    if report.request.flow.run_id != run_id:
        raise ValueError("Supervised run identity differs")
    _validate_request(repository, report.request)
    if report.flow_result.authorization != _inner_authorization(
        report.request, report.authorization
    ):
        raise ValueError("Nested authorization is not the exact outer projection")
    if validate_semantic_flow_v4(repository, run_id) != report.flow_result:
        raise ValueError("Nested flow result differs")
    for name, model in [("request", report.request), ("authorization", report.authorization)]:
        if _read(directory / f"{name}.json") != model.model_dump(mode="json"):
            raise ValueError("Supervised metadata differs")
    claim = (
        repository.resolve() / ".factory" / "supervised-v4-claims" / f"{report.request.sha256}.json"
    )
    if not claim.resolve().is_relative_to(repository.resolve()) or _read(
        claim
    ) != report.authorization.model_dump(mode="json"):
        raise ValueError("Supervised claim differs")
    extraction = extract_grounding(report.request.flow.case.project)
    for receipt in report.receipts:
        if _read(directory / f"receipt-{receipt.index}.json") != receipt.model_dump(mode="json"):
            raise ValueError("Saved transport receipt differs")
        if receipt.index == 1:
            prompt, schema = (
                program_prompt(extraction, report.request.flow.generation_program_sha256),
                generation_schema_v4(extraction),
            )
        elif report.flow_result.analysis:
            prompt, schema = (
                audit_prompt_v5(report.flow_result.analysis),
                audit_schema_v5(report.flow_result.analysis),
            )
        else:
            raise ValueError("Audit transport requires validated analysis")
        payload = dict(
            model=report.request.flow.requested_model,
            prompt=prompt,
            response_schema=schema,
            timeout_seconds=report.request.limits.call_timeout_seconds,
        )
        expected = dict(index=receipt.index, payload_sha256=canonical_project_digest(payload))
        if (
            receipt.payload_sha256 != expected["payload_sha256"]
            or _read(directory / f"attempt-{receipt.index}.json") != expected
        ):
            raise ValueError("Transport payload must match charged flow call")
        if receipt.status == "succeeded":
            stage = "analysis" if receipt.index == 1 else "audit"
            response = _read(
                repository.resolve()
                / ".factory"
                / "semantic-v4-runs"
                / run_id
                / f"{stage}-response.json"
            )
            if canonical_project_digest(response) != receipt.response_sha256:
                raise ValueError("Transport response differs from saved response")
    return report
