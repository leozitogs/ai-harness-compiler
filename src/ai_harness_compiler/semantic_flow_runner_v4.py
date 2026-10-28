"""Private single-use I/O boundary for injected generators, with no transport defaults.

Call limits count boundary invocations, NOT hidden transport requests. This is not
a production wall-clock supervisor; real adapters need a separately approved protocol.
"""

import hashlib
import json
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_assessment_v4 import (
    SemanticAssessmentV4,
    SemanticHumanReviewV4,
    assess_v4,
)
from ai_harness_compiler.models.semantic_flow_v4 import (
    SemanticFlowAuthorizationV4,
    SemanticFlowCallV4,
    SemanticFlowRequestV4,
    SemanticFlowResultV4,
)
from ai_harness_compiler.models.semantic_preflight import preflight_case
from ai_harness_compiler.semantic_generation_programs import analyze_program, program_prompt
from ai_harness_compiler.semantic_generation_v4 import (
    audit_prompt_v5,
    audit_schema_v5,
    audit_v5,
    generation_schema_v4,
)
from ai_harness_compiler.semantic_verification import JSONGenerator

MAX_ARTIFACT_BYTES = 16 * 1024 * 1024


def _write(path: Path, data: Any) -> None:
    encoded = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8") + b"\n"
    if len(encoded) > MAX_ARTIFACT_BYTES:
        raise ValueError("Flow artifact exceeds byte limit")
    with path.open("xb") as stream:
        stream.write(encoded)
        stream.flush()
        os.fsync(stream.fileno())


def _read(path: Path) -> Any:
    if path.is_symlink():
        raise ValueError("Flow artifact must not redirect to another file")
    with path.open("rb") as stream:
        raw = stream.read(MAX_ARTIFACT_BYTES + 1)
    if len(raw) > MAX_ARTIFACT_BYTES:
        raise ValueError("Flow artifact exceeds byte limit")
    return json.loads(raw)


def _directory(repository: Path, run_id: str) -> Path:
    root = repository.resolve()
    directory = root / ".factory" / "semantic-v4-runs" / run_id
    if not directory.resolve().is_relative_to(root):
        raise ValueError("Private output must remain inside repository")
    return directory


def run_semantic_flow_v4(
    repository: Path,
    request: SemanticFlowRequestV4,
    authorization: SemanticFlowAuthorizationV4,
    generator_factory: Callable[[], JSONGenerator],
) -> SemanticFlowResultV4:
    request = SemanticFlowRequestV4.model_validate(request.model_dump())
    authorization = SemanticFlowAuthorizationV4.model_validate(authorization.model_dump())
    preflight = preflight_case(request.case, "SemanticAnalysis/v4")
    if (
        authorization.request_sha256 != request.sha256
        or not request.case.expectations_approval
        or not request.rubric.approval
        or preflight.status != "compatible"
    ):
        raise ValueError(
            "Exact execution authorization and approved compatible expectations required"
        )
    directory = _directory(repository, request.run_id)
    claims = repository.resolve() / ".factory" / "semantic-v4-claims"
    if not claims.resolve().is_relative_to(repository.resolve()):
        raise ValueError("Claim directory must remain inside repository")
    claims.mkdir(parents=True, exist_ok=True)
    # Claim stays consumed even when output creation or the factory fails. Never resume.
    _write(claims / f"{request.sha256}.json", authorization.model_dump())
    directory.mkdir(parents=True, exist_ok=False)
    _write(directory / "request.json", request.model_dump())
    _write(directory / "authorization.json", authorization.model_dump())
    _write(directory / "preflight.json", preflight.model_dump())
    calls: list[SemanticFlowCallV4] = []
    analysis = None
    audit = None
    failure: Literal["factory-failed", "analysis-failed", "audit-failed"] | None = "factory-failed"

    class ChargedGenerator:
        def __init__(self, delegate: JSONGenerator, stage: Literal["analysis", "audit"]):
            self.delegate = delegate
            self.stage = stage

        def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
            if len(calls) >= 2 or self.stage != ["analysis", "audit"][len(calls)]:
                raise ValueError("No retries or additional generator calls")
            call = SemanticFlowCallV4(
                stage=self.stage,
                prompt_sha256=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                schema_sha256=canonical_project_digest(schema),
            )
            # Durable debit BEFORE calling injected code. No raw prompt is persisted.
            _write(directory / f"{self.stage}-call.json", call.model_dump())
            calls.append(call)
            raw = self.delegate.generate_json(prompt, schema)
            if len(raw.encode("utf-8")) > MAX_ARTIFACT_BYTES:
                raise ValueError("Generator response exceeds byte limit")
            _write(directory / f"{self.stage}-response.json", json.loads(raw))
            return raw

    try:
        generator = generator_factory()
        failure = "analysis-failed"
        analysis = analyze_program(
            extract_grounding(request.case.project),
            ChargedGenerator(generator, "analysis"),
            request.generation_program_sha256,
        )
        _write(directory / "analysis.json", analysis.model_dump())
        failure = "audit-failed"
        audit = audit_v5(analysis, ChargedGenerator(generator, "audit"), request.requested_model)
        _write(directory / "audit.json", audit.model_dump())
        failure = None
    except OSError:
        # An incomplete durable journal cannot be reported as a normal terminal run.
        # The claim remains consumed; recovery is manual, never automatic resume.
        raise
    except Exception:
        # Do not persist exception text: SDK errors can expose credentials/private content.
        pass
    result = SemanticFlowResultV4(
        request=request,
        authorization=authorization,
        preflight=preflight,
        calls=calls,
        status="failed" if failure else "completed",
        failure_code=failure,
        analysis=analysis,
        audit=audit,
        assessment=assess_v4(request.case, request.rubric, analysis) if analysis else None,
    )
    _write(directory / "result.json", result.model_dump())
    return result


def validate_semantic_flow_v4(repository: Path, run_id: str) -> SemanticFlowResultV4:
    # Validate identifier before using it in a path, including offline replay.
    from pydantic import TypeAdapter

    from ai_harness_compiler.models.base import Identifier

    TypeAdapter(Identifier).validate_python(run_id)
    directory = _directory(repository, run_id)
    result = SemanticFlowResultV4.model_validate(_read(directory / "result.json"))
    if result.request.run_id != run_id:
        raise ValueError("Flow identity differs from directory")
    for name, model in [
        ("request", result.request),
        ("authorization", result.authorization),
        ("preflight", result.preflight),
        ("analysis", result.analysis),
        ("audit", result.audit),
    ]:
        if model and _read(directory / f"{name}.json") != model.model_dump(mode="json"):
            raise ValueError("Saved artifact differs from flow result")
    claim = (
        repository.resolve() / ".factory" / "semantic-v4-claims" / f"{result.request.sha256}.json"
    )
    if not claim.resolve().is_relative_to(repository.resolve()):
        raise ValueError("Claim must remain inside repository")
    if _read(claim) != result.authorization.model_dump(mode="json"):
        raise ValueError("Flow claim differs")
    extraction = extract_grounding(result.request.case.project)
    for call in result.calls:
        if _read(directory / f"{call.stage}-call.json") != call.model_dump():
            raise ValueError("Durable call debit differs")
        if call.stage == "analysis":
            prompt, schema = (
                program_prompt(extraction, result.request.generation_program_sha256),
                generation_schema_v4(extraction),
            )
        elif result.analysis:
            prompt, schema = audit_prompt_v5(result.analysis), audit_schema_v5(result.analysis)
        else:
            raise ValueError("Audit call requires saved analysis")
        if call.prompt_sha256 != hashlib.sha256(
            prompt.encode("utf-8")
        ).hexdigest() or call.schema_sha256 != canonical_project_digest(schema):
            raise ValueError("Call must bind the exact input prompt and response schema")
        artifact = result.analysis if call.stage == "analysis" else result.audit
        if artifact:
            response = _read(directory / f"{call.stage}-response.json")
            if type(artifact.proposal).model_validate(response) != artifact.proposal:
                raise ValueError("Response differs from validated proposal")
    return result


def save_semantic_review_v4(
    repository: Path, run_id: str, review: SemanticHumanReviewV4
) -> SemanticAssessmentV4:
    result = validate_semantic_flow_v4(repository, run_id)
    if result.analysis is None:
        raise ValueError("Human review requires a validated analysis")
    assessment = assess_v4(result.request.case, result.request.rubric, result.analysis, review)
    directory = _directory(repository, run_id)
    digest = canonical_project_digest(assessment.model_dump())
    _write(directory / f"human-assessment-{digest}.json", assessment.model_dump())
    return assessment
