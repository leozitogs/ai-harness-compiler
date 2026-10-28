"""Opt-in, single-use development campaign with one shared monotonic deadline."""

import hashlib
import json
from pathlib import Path
from time import monotonic
from typing import Any, Literal

from pydantic import TypeAdapter

from ai_harness_compiler.adapters.process_supervisor import invoke_json_worker
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.base import Identifier
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_campaign import (
    SemanticCampaignAuthorizationV1,
    SemanticCampaignCallV1,
    SemanticCampaignReportV1,
    SemanticCampaignRequestV1,
    flow_authorization,
)
from ai_harness_compiler.models.semantic_flow_v4 import SemanticFlowRequestV4, SemanticFlowResultV4
from ai_harness_compiler.models.supervised_transport import TransportLimitsV1
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
from ai_harness_compiler.supervised_semantic_flow import (
    _validate_request,
    prepare_supervised_flow,
    worker_command,
)


def _bounded_path(repository: Path, relative: str) -> Path:
    root = repository.resolve()
    path = root / relative
    if not path.resolve().is_relative_to(root) or path.is_symlink():
        raise ValueError("Campaign path escapes repository")
    return path


def _validate_corpus(repository: Path, request: SemanticCampaignRequestV1) -> None:
    path = _bounded_path(repository, request.corpus_source)
    manifest = _read(path)
    if (
        canonical_project_digest(manifest) != request.corpus_sha256
        or manifest.get("status") != "expectations-approved"
        or manifest.get("split") != "development"
        or manifest.get("target_analysis") != "SemanticAnalysis/v4"
    ):
        raise ValueError("Campaign requires the exact approved development manifest")
    entries = manifest.get("cases", [])
    if len(entries) != len(request.flows):
        raise ValueError("Campaign must bind the entire ordered corpus")
    rubric_path = manifest.get("rubric_source", "")
    if not rubric_path.startswith("evals/") or ".." in rubric_path.split("/"):
        raise ValueError("Rubric must remain an explicit eval source")
    raw_rubric = _bounded_path(repository, rubric_path).read_bytes()
    if hashlib.sha256(raw_rubric).hexdigest() != manifest.get("rubric_sha256"):
        raise ValueError("Corpus rubric hash differs")
    for entry, flow in zip(entries, request.flows, strict=True):
        name = entry["path"]
        if Path(name).name != name or "\\" in name or not name.endswith(".json"):
            raise ValueError("Corpus case must be a local JSON filename")
        case_path = _bounded_path(
            repository, (Path(request.corpus_source).parent / name).as_posix()
        )
        raw = case_path.read_bytes()
        if (
            entry["id"] != flow.case.id
            or entry["case_sha256"] != flow.case.snapshot_sha256
            or entry["project_sha256"] != canonical_project_digest(flow.case.project.model_dump())
            or entry["file_sha256"] != hashlib.sha256(raw).hexdigest()
            or json.loads(raw) != flow.case.model_dump(mode="json")
            or json.loads(raw_rubric) != flow.rubric.model_dump(mode="json")
        ):
            raise ValueError("Campaign case order, snapshot or rubric differs from approved corpus")


def prepare_campaign(
    repository: Path,
    *,
    campaign_id: str,
    corpus_source: str,
    flows: list[SemanticFlowRequestV4],
    limits: TransportLimitsV1,
) -> SemanticCampaignRequestV1:
    """Metadata and public source checks only; does not create claims or call a provider."""
    if not flows:
        raise ValueError("Campaign needs at least one case")
    transport = prepare_supervised_flow(repository, flows[0], limits)
    request = SemanticCampaignRequestV1(
        campaign_id=campaign_id,
        corpus_source=corpus_source,
        corpus_sha256=canonical_project_digest(_read(_bounded_path(repository, corpus_source))),
        flows=flows,
        limits=limits,
        max_calls=2 * len(flows),
        worker_command_sha256=transport.worker_command_sha256,
        python_runtime=transport.python_runtime,
        sources=transport.sources,
    )
    _validate_corpus(repository, request)
    return request


def _directory(repository: Path, campaign_id: str) -> Path:
    TypeAdapter(Identifier).validate_python(campaign_id)
    return _bounded_path(repository, f".factory/semantic-v4-campaigns/{campaign_id}")


def run_campaign(
    repository: Path,
    request: SemanticCampaignRequestV1,
    authorization: SemanticCampaignAuthorizationV1,
) -> SemanticCampaignReportV1:
    started = monotonic()
    request = SemanticCampaignRequestV1.model_validate(request.model_dump())
    authorization = SemanticCampaignAuthorizationV1.model_validate(authorization.model_dump())
    if authorization.request_sha256 != request.sha256:
        raise ValueError("A new exact campaign authorization is required")
    _validate_corpus(repository, request)
    _validate_request(repository, request.supervision(0))
    directory = _directory(repository, request.campaign_id)
    claim = _bounded_path(repository, f".factory/semantic-v4-campaign-claims/{request.sha256}.json")
    claim.parent.mkdir(parents=True, exist_ok=True)
    _write(claim, authorization.model_dump())
    directory.mkdir(parents=True, exist_ok=False)
    _write(directory / "request.json", request.model_dump())
    _write(directory / "authorization.json", authorization.model_dump())
    deadline = started + request.limits.session_timeout_seconds
    calls: list[SemanticCampaignCallV1] = []
    results: list[SemanticFlowResultV4] = []
    failure: Literal["case-failed", "budget-exhausted", "cancelled"] | None = None

    def run_case(flow_index: int) -> SemanticFlowResultV4:
        nested = request.flows[flow_index]
        local_count = 0

        class Generator:
            def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
                nonlocal local_count
                if (
                    len(calls) >= request.max_calls
                    or local_count >= 2
                    or any(
                        c.interruption or (c.receipt and c.receipt.status == "failed")
                        for c in calls
                    )
                ):
                    raise ValueError(
                        "Campaign cannot retry, exceed budget or continue after failure"
                    )
                local_count += 1
                index = len(calls) + 1
                payload = dict(
                    model=nested.requested_model,
                    prompt=prompt,
                    response_schema=schema,
                    timeout_seconds=request.limits.call_timeout_seconds,
                )
                debit: dict[str, Any] = dict(
                    index=index,
                    flow_index=flow_index,
                    stage="analysis" if local_count == 1 else "audit",
                    payload_sha256=canonical_project_digest(payload),
                    started_offset_seconds=monotonic() - started,
                )
                # Persist global debit before any trusted worker is invoked.
                _write(directory / f"attempt-{index}.json", debit)
                receipt = None
                interruption: Literal["cancelled", "transport-exception"] | None = None
                response = None
                try:
                    # A later worker must not load code changed since campaign entry.
                    _validate_request(repository, request.supervision(flow_index))
                    command = worker_command()
                    if canonical_project_digest({"argv": command}) != request.worker_command_sha256:
                        raise ValueError("Campaign worker command changed before invocation")
                    outcome = invoke_json_worker(
                        command,
                        payload,
                        cwd=repository.resolve(),
                        limits=request.limits,
                        session_deadline=deadline,
                        index=local_count,
                    )
                    receipt, response = outcome.receipt, outcome.response
                    if (
                        receipt.command_sha256 != request.worker_command_sha256
                        or receipt.payload_sha256 != debit["payload_sha256"]
                        or (
                            receipt.status == "succeeded"
                            and (
                                response is None
                                or canonical_project_digest(json.loads(response))
                                != receipt.response_sha256
                            )
                        )
                    ):
                        raise ValueError("Transport evidence differs from the charged payload")
                except KeyboardInterrupt:
                    receipt, response, interruption = None, None, "cancelled"
                except Exception:
                    # No exception text or fabricated process observations.
                    receipt, response, interruption = None, None, "transport-exception"
                call = SemanticCampaignCallV1(
                    **debit,
                    receipt=receipt,
                    interruption=interruption,
                    finished_offset_seconds=monotonic() - started,
                )
                _write(directory / f"call-{index}.json", call.model_dump())
                calls.append(call)
                if interruption or not receipt or receipt.status != "succeeded" or response is None:
                    raise ValueError("CAMPAIGN_TRANSPORT_FAILED")
                return response

        return run_semantic_flow_v4(
            repository, nested, flow_authorization(nested, authorization), Generator
        )

    for index in range(len(request.flows)):
        if deadline - monotonic() <= request.limits.cleanup_timeout_seconds:
            failure = "budget-exhausted"
            break
        result = run_case(index)
        results.append(result)
        if result.status == "failed":
            failure = (
                "cancelled" if calls and calls[-1].interruption == "cancelled" else "case-failed"
            )
            break
    elapsed = monotonic() - started
    if failure is None and elapsed > request.limits.session_timeout_seconds:
        failure = "budget-exhausted"
    report = SemanticCampaignReportV1(
        request=request,
        authorization=authorization,
        results=results,
        calls=calls,
        elapsed_seconds=elapsed,
        status="failed" if failure else "completed",
        failure_code=failure,
    )
    _write(directory / "report.json", report.model_dump())
    return report


def validate_campaign(repository: Path, campaign_id: str) -> SemanticCampaignReportV1:
    directory = _directory(repository, campaign_id)
    report = SemanticCampaignReportV1.model_validate(_read(directory / "report.json"))
    request = report.request
    if request.campaign_id != campaign_id:
        raise ValueError("Campaign directory identity differs")
    _validate_corpus(repository, request)
    _validate_request(repository, request.supervision(0))
    for name, value in [("request", request), ("authorization", report.authorization)]:
        if _read(directory / f"{name}.json") != value.model_dump(mode="json"):
            raise ValueError("Campaign metadata differs")
    claim = _bounded_path(repository, f".factory/semantic-v4-campaign-claims/{request.sha256}.json")
    if _read(claim) != report.authorization.model_dump(mode="json"):
        raise ValueError("Campaign claim differs")
    for result in report.results:
        if validate_semantic_flow_v4(repository, result.request.run_id) != result:
            raise ValueError("Nested result differs from campaign report")
    for call in report.calls:
        flow = request.flows[call.flow_index]
        if call.stage == "analysis":
            extraction = extract_grounding(flow.case.project)
            prompt, schema = (
                program_prompt(extraction, flow.generation_program_sha256),
                generation_schema_v4(extraction),
            )
        else:
            analysis = report.results[call.flow_index].analysis
            if analysis is None:
                raise ValueError("Audit debit requires a validated analysis")
            prompt, schema = audit_prompt_v5(analysis), audit_schema_v5(analysis)
        payload = dict(
            model=flow.requested_model,
            prompt=prompt,
            response_schema=schema,
            timeout_seconds=request.limits.call_timeout_seconds,
        )
        debit = call.model_dump(exclude={"finished_offset_seconds", "receipt", "interruption"})
        if (
            call.payload_sha256 != canonical_project_digest(payload)
            or _read(directory / f"attempt-{call.index}.json") != debit
            or _read(directory / f"call-{call.index}.json") != call.model_dump(mode="json")
        ):
            raise ValueError("Campaign debit or receipt differs from exact stage payload")
        if call.receipt and call.receipt.status == "succeeded":
            response = _read(
                _bounded_path(
                    repository,
                    f".factory/semantic-v4-runs/{flow.run_id}/{call.stage}-response.json",
                )
            )
            if canonical_project_digest(response) != call.receipt.response_sha256:
                raise ValueError("Campaign response differs from transport receipt")
    for prefix in ("attempt", "call"):
        if {p.name for p in directory.glob(f"{prefix}-*.json")} != {
            f"{prefix}-{c.index}.json" for c in report.calls
        }:
            raise ValueError("Campaign contains unaccounted invocation evidence")
    return report
