"""Private, single-use reserved evaluation boundary. No calls without exact authorization."""

import hashlib
import json
import os
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from time import monotonic
from typing import Any

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.reserved_run import (
    ReservedRunAuthorization,
    ReservedRunJob,
    ReservedRunReport,
    ReservedRunRequest,
    relative_file,
    reserved_job_keys,
    validate_run_authorization,
)
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_eval import UnderstandingRubric, semantic_snapshot_digest
from ai_harness_compiler.models.semantic_verification_v4 import SemanticVerifierReportV4
from ai_harness_compiler.semantic_composition import (
    analyze_composition,
    audit_composition,
    component_audit_program_digest,
    composition_program_digest,
)
from ai_harness_compiler.semantic_verification import JSONGenerator

MAX_BYTES = 2 * 1024 * 1024
CANDIDATE_SOURCES = {
    "src/ai_harness_compiler/semantic_composition.py",
    "src/ai_harness_compiler/grounding.py",
    "src/ai_harness_compiler/semantic_verification.py",
    "src/ai_harness_compiler/models/semantic_analysis_v3.py",
    "src/ai_harness_compiler/models/semantic_verification_v4.py",
    "src/ai_harness_compiler/adapters/codex_cli.py",
}
RUNNER_SOURCES = {
    "src/ai_harness_compiler/models/reserved_evaluation.py",
    "src/ai_harness_compiler/models/reserved_run.py",
    "src/ai_harness_compiler/models/semantic_assessment.py",
    "src/ai_harness_compiler/models/semantic_assessment_v3.py",
    "src/ai_harness_compiler/reserved_runs.py",
    "src/ai_harness_compiler/reserved_cli.py",
    "src/ai_harness_compiler/cli.py",
}


def bounded_read(path: Path) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("RESERVED_ARTIFACT_SIZE")
    return raw


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def safe_path(root: Path, relative: str) -> Path:
    relative_file(relative)
    path = root / relative
    # Reject junctions/symlinks as well as lexical traversal, including output parents.
    cursor = path
    while cursor != root:
        if cursor.is_symlink() or cursor.is_junction():
            raise ValueError("RESERVED_LINKED_PATH")
        cursor = cursor.parent
    if not path.resolve().is_relative_to(root):
        raise ValueError("RESERVED_PATH_ESCAPE")
    return path


def write_new(path: Path, payload: dict[str, Any]) -> str:
    raw = json_text(payload).encode("utf-8")
    if len(raw) > MAX_BYTES:
        raise ValueError("RESERVED_ARTIFACT_SIZE")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return sha256(raw)


def verify_frozen_sources(root: Path, request: ReservedRunRequest) -> None:
    if {s.path for s in request.candidate_code.files} != CANDIDATE_SOURCES or {
        s.path for s in request.runner_sources
    } != RUNNER_SOURCES:
        raise ValueError("RESERVED_SOURCE_INVENTORY")
    package = Path(__file__).resolve().parent
    for source in request.candidate_code.files + request.runner_sources:
        repository_source = safe_path(root, source.path)
        running_source = package / source.path.removeprefix("src/ai_harness_compiler/")
        if sha256(bounded_read(repository_source)) != source.sha256 or (
            sha256(bounded_read(running_source)) != source.sha256
        ):
            raise ValueError("RESERVED_SOURCE_CHANGED")
    from ai_harness_compiler.adapters.codex_cli import (
        MAX_INPUT_BYTES,
        MAX_STREAM_BYTES,
        OVERRIDES,
        POLICY_VERSION,
    )

    if request.profile.adapter_version != POLICY_VERSION or request.profile.overrides != list(
        OVERRIDES
    ):
        raise ValueError("RESERVED_ADAPTER_PROFILE_CHANGED")
    if (
        request.max_prompt_bytes != MAX_INPUT_BYTES
        or request.max_response_bytes != MAX_STREAM_BYTES
    ):
        raise ValueError("RESERVED_ADAPTER_LIMIT_CHANGED")
    if request.protocol.candidate is None or (
        request.protocol.candidate.composition_version != "semantic-composition/v3.4"
        or request.protocol.candidate.audit_version != "component-audit/v4.1"
    ):
        raise ValueError("RESERVED_RECIPE_UNSUPPORTED")


def load_verified_payloads(
    root: Path, request: ReservedRunRequest
) -> tuple[dict[str, AssessmentCase], UnderstandingRubric, dict[str, bytes], bytes]:
    """Called only after authorization and exclusive claim. Never follows asset references."""
    raw_rubric = bounded_read(safe_path(root, request.rubric_path))
    if sha256(raw_rubric) != request.protocol.rubric_sha256:
        raise ValueError("RESERVED_RUBRIC_CHANGED")
    rubric = UnderstandingRubric.model_validate_json(raw_rubric)
    if rubric.version != "v2" or rubric.approval is None:
        raise ValueError("RESERVED_RUBRIC_UNREVIEWED")
    cases, originals = {}, {}
    total = len(raw_rubric)
    for binding in request.protocol.reserved:
        raw = bounded_read(safe_path(root, binding.artifact_path))
        total += len(raw)
        if total > request.max_corpus_bytes:
            raise ValueError("RESERVED_CORPUS_SIZE")
        if sha256(raw) != binding.artifact_sha256:
            raise ValueError("RESERVED_CASE_BYTES_CHANGED")
        case = AssessmentCase.model_validate_json(raw)
        if (
            case.id != binding.case_id
            or case.project.id != binding.project_id
            or case.snapshot_sha256 != binding.case_sha256
            or canonical_project_digest(case.project.model_dump()) != binding.input_sha256
            or semantic_snapshot_digest(case.project) != binding.semantic_sha256
        ):
            raise ValueError("RESERVED_CASE_BINDING_CHANGED")
        cases[case.id], originals[case.id] = case, raw
    return cases, rubric, originals, raw_rubric


class RecordedGenerator:
    def __init__(
        self,
        generator: JSONGenerator,
        folder: Path,
        request: ReservedRunRequest,
        case_id: str,
        repetition: int,
        stage: str,
        deadline: float,
    ) -> None:
        self.generator, self.folder, self.request = generator, folder, request
        self.case_id, self.repetition, self.stage = case_id, repetition, stage
        self.deadline = deadline
        self.charged = False
        self.elapsed = 0.0
        self.response_sha256: str | None = None

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        if self.charged:
            raise ValueError("RESERVED_SECOND_CALL_FORBIDDEN")
        if len(prompt.encode()) > self.request.max_prompt_bytes:
            raise ValueError("RESERVED_PROMPT_SIZE")
        if self.deadline - monotonic() < (
            self.request.profile.timeout_seconds + self.request.cleanup_grace_seconds
        ):
            raise TimeoutError("RESERVED_SESSION_TIME_LIMIT")
        # Adapter performs a deterministic strict-schema projection; no model call here.
        from ai_harness_compiler.adapters.codex_cli import strict_schema

        receipt = {
            "request_sha256": self.request.sha256,
            "case_id": self.case_id,
            "repetition": self.repetition,
            "stage": self.stage,
            "prompt_sha256": sha256(prompt.encode()),
            "response_schema_sha256": canonical_project_digest(schema),
            "effective_schema_sha256": canonical_project_digest(strict_schema(schema)),
            "provider_calls_observed": None,
        }
        write_new(self.folder / "call-start.json", receipt | {"state": "charged"})
        self.charged = True
        started = monotonic()
        state = "error"
        try:
            response = self.generator.generate_json(prompt, schema)
            raw = response.encode("utf-8")
            if len(raw) > MAX_BYTES:
                raise ValueError("RESERVED_RESPONSE_SIZE")
            with (self.folder / "response.txt").open("xb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            self.response_sha256 = sha256(raw)
            if monotonic() - started > self.request.profile.timeout_seconds:
                raise TimeoutError("RESERVED_CALL_TIME_LIMIT")
            state = "returned"
            return response
        finally:
            self.elapsed = monotonic() - started
            write_new(
                self.folder / "call-finish.json",
                receipt
                | {
                    "state": state,
                    "elapsed_seconds": self.elapsed,
                    "response_sha256": self.response_sha256,
                },
            )


def codex_generator(request: ReservedRunRequest) -> JSONGenerator:
    from ai_harness_compiler.adapters.codex_cli import CodexCLISettings, CodexCompactModel

    return CodexCompactModel(
        CodexCLISettings(request.profile.requested_model, request.profile.timeout_seconds)
    )


def run_reserved(
    repository: Path,
    request: ReservedRunRequest,
    authorization: ReservedRunAuthorization,
    *,
    generator_factory: Callable[[ReservedRunRequest], JSONGenerator] = codex_generator,
) -> ReservedRunReport:
    request = ReservedRunRequest.model_validate(request.model_dump())
    authorization = ReservedRunAuthorization.model_validate(authorization.model_dump())
    validate_run_authorization(request, authorization)
    root = repository.resolve()
    verify_frozen_sources(root, request)
    output = safe_path(root, request.output_path)
    if output.exists():
        raise FileExistsError("RESERVED_OUTPUT_EXISTS")
    claims = safe_path(root, ".factory/reserved-run-claims")
    claims.mkdir(parents=True, exist_ok=True)
    # One use per exact request, regardless of output changes, crash or preflight failure.
    write_new(
        claims / f"{request.sha256}.json",
        {
            "request_sha256": request.sha256,
            "authorization": authorization.model_dump(),
            "state": "consumed-no-resume",
            "recorded_at": datetime.now(UTC).isoformat(),
        },
    )
    output.mkdir(parents=True, exist_ok=False)
    write_new(output / "request.json", request.model_dump())
    write_new(output / "authorization.json", authorization.model_dump())
    started = monotonic()
    started_at = datetime.now(UTC).isoformat()
    try:
        cases, _, originals, raw_rubric = load_verified_payloads(root, request)
    except (OSError, ValueError):
        write_new(
            output / "preflight-error.json",
            {
                "state": "error",
                "code": "RESERVED_PAYLOAD_PREFLIGHT_FAILED",
                "model_invocations_charged": 0,
                "request_sha256": request.sha256,
            },
        )
        raise ValueError("RESERVED_PAYLOAD_PREFLIGHT_FAILED") from None
    case_folder = output / "cases"
    case_folder.mkdir()
    with (output / "rubric.json").open("xb") as stream:
        stream.write(raw_rubric)
    for case_id, raw in originals.items():
        with (case_folder / f"{case_id}.json").open("xb") as stream:
            stream.write(raw)
    write_new(
        output / "verification.json",
        {
            "request_sha256": request.sha256,
            "case_count": len(cases),
            "payload_validation": "exact-bytes-and-contracts",
            "expectations_authority": "external-human-review-bound-to-original-corpus",
            "semantic_status": "not-established",
        },
    )
    assert request.protocol.budget
    budget = request.protocol.budget
    jobs: list[ReservedRunJob] = []
    analyses: dict[tuple[str, int], SemanticAnalysisV3] = {}
    reason = None
    for index, (case_id, repetition, stage) in enumerate(reserved_job_keys(request), 1):
        if reason is None and budget.max_session_seconds - (monotonic() - started) < (
            budget.max_call_seconds + request.cleanup_grace_seconds
        ):
            reason = "session-budget-insufficient"
        if reason:
            jobs.append(
                ReservedRunJob(
                    case_id=case_id,
                    repetition=repetition,
                    stage=stage,
                    state="not-run",
                    invocation_charged=False,
                    elapsed_seconds=0.0,
                    error_code=reason,
                )
            )
            continue
        folder = output / f"job-{index:03}"
        folder.mkdir()
        recorder: RecordedGenerator | None = None
        analysis = analyses.get((case_id, repetition))
        artifact: SemanticAnalysisV3 | SemanticVerifierReportV4
        try:
            recorder = RecordedGenerator(
                generator_factory(request),
                folder,
                request,
                case_id,
                repetition,
                stage,
                started + budget.max_session_seconds,
            )
            if stage == "analysis":
                extraction = extract_grounding(cases[case_id].project)
                program = composition_program_digest(extraction, "semantic-composition/v3.4")
                analysis = analyze_composition(
                    extraction, recorder, program_version="semantic-composition/v3.4"
                )
                analyses[case_id, repetition] = analysis
                artifact = analysis
            else:
                assert analysis
                program = component_audit_program_digest(analysis, "component-audit/v4.1")
                artifact = audit_composition(
                    analysis,
                    recorder,
                    request.profile.requested_model,
                    program_version="component-audit/v4.1",
                )
            if monotonic() - started > budget.max_session_seconds:
                raise TimeoutError("RESERVED_SESSION_TIME_LIMIT")
            artifact_sha256 = write_new(folder / "artifact.json", artifact.model_dump())
            write_new(folder / "program.json", {"program_sha256": program})
            assert analysis
            job = ReservedRunJob(
                case_id=case_id,
                repetition=repetition,
                stage=stage,
                state="completed",
                invocation_charged=recorder.charged,
                elapsed_seconds=recorder.elapsed,
                response_sha256=recorder.response_sha256,
                artifact_sha256=artifact_sha256,
                analysis_sha256=analysis.snapshot_sha256,
            )
        except Exception as exc:
            # Provider/serialization failures are persisted without private exception text.
            reason = (
                "call-time-limit-no-retry"
                if isinstance(exc, TimeoutError)
                else "provider-unavailable"
                if isinstance(exc, ModuleNotFoundError)
                else "invalid-stage-no-retry"
                if isinstance(exc, ValueError)
                else "stage-error-no-retry"
            )
            charged = bool(recorder and recorder.charged)
            job = ReservedRunJob(
                case_id=case_id,
                repetition=repetition,
                stage=stage,
                state="error" if charged else "not-run",
                invocation_charged=charged,
                elapsed_seconds=recorder.elapsed if recorder else 0.0,
                response_sha256=recorder.response_sha256 if recorder else None,
                analysis_sha256=analysis.snapshot_sha256
                if stage == "audit" and analysis and charged
                else None,
                error_code=reason,
            )
        jobs.append(job)
        write_new(folder / "job.json", job.model_dump())
    report = ReservedRunReport(
        request=request,
        authorization=authorization,
        request_sha256=request.sha256,
        started_at=started_at,
        finished_at=datetime.now(UTC).isoformat(),
        jobs=jobs,
        model_invocations_charged=sum(j.invocation_charged for j in jobs),
        elapsed_seconds=monotonic() - started,
        state="stopped" if reason else "completed",
        stop_reason=reason,
    )
    write_new(output / "session.json", report.model_dump())
    return report


def validate_reserved_run(repository: Path, output: Path) -> ReservedRunReport:
    """Offline evidence replay. Uses only the original authorization's private result directory."""
    root = repository.resolve()
    output = output.resolve()
    if not output.is_relative_to(root):
        raise ValueError("RESERVED_PATH_ESCAPE")
    report = ReservedRunReport.model_validate_json(bounded_read(output / "session.json"))
    request = report.request
    if safe_path(root, request.output_path) != output:
        raise ValueError("RESERVED_RUN_LOCATION_CHANGED")
    saved_request = ReservedRunRequest.model_validate_json(bounded_read(output / "request.json"))
    saved_auth = ReservedRunAuthorization.model_validate_json(
        bounded_read(output / "authorization.json")
    )
    if saved_request != request or saved_auth != report.authorization:
        raise ValueError("RESERVED_RUN_METADATA_CHANGED")
    # Exact hashes checked before parsing copied inputs; original files remain untouched.
    cases = {}
    for binding in request.protocol.reserved:
        raw = bounded_read(safe_path(root, f"{request.output_path}/cases/{binding.case_id}.json"))
        case = AssessmentCase.model_validate_json(raw)
        if (
            sha256(raw) != binding.artifact_sha256
            or case.snapshot_sha256 != binding.case_sha256
            or canonical_project_digest(case.project.model_dump()) != binding.input_sha256
            or case.id != binding.case_id
            or case.project.id != binding.project_id
            or semantic_snapshot_digest(case.project) != binding.semantic_sha256
        ):
            raise ValueError("RESERVED_COPIED_CASE_CHANGED")
        cases[case.id] = case
    raw_rubric = bounded_read(safe_path(root, f"{request.output_path}/rubric.json"))
    if sha256(raw_rubric) != request.protocol.rubric_sha256:
        raise ValueError("RESERVED_COPIED_RUBRIC_CHANGED")
    UnderstandingRubric.model_validate_json(raw_rubric)
    analyses: dict[tuple[str, int], SemanticAnalysisV3] = {}
    expected_starts = set()
    for index, job in enumerate(report.jobs, 1):
        relative = f"{request.output_path}/job-{index:03}"
        folder = safe_path(root, relative)
        job_file = folder / "job.json"
        if job_file.exists() and ReservedRunJob.model_validate_json(bounded_read(job_file)) != job:
            raise ValueError("RESERVED_JOB_CHANGED")
        if not job.invocation_charged:
            continue
        if not job_file.is_file():
            raise ValueError("RESERVED_JOB_MISSING")
        start_path = safe_path(root, relative + "/call-start.json")
        finish_path = safe_path(root, relative + "/call-finish.json")
        start, finish = json.loads(bounded_read(start_path)), json.loads(bounded_read(finish_path))
        expected_starts.add(start_path)
        identity = {
            "request_sha256": request.sha256,
            "case_id": job.case_id,
            "repetition": job.repetition,
            "stage": job.stage,
        }
        if any(start.get(k) != v for k, v in identity.items()) or start.get("state") != "charged":
            raise ValueError("RESERVED_RECEIPT_BINDING_CHANGED")
        if any(finish.get(k) != v for k, v in start.items() if k != "state") or (
            finish.get("elapsed_seconds") != job.elapsed_seconds
            or finish.get("response_sha256") != job.response_sha256
            or finish.get("state") not in {"returned", "error"}
        ):
            raise ValueError("RESERVED_RECEIPT_CHANGED")
        response_path = safe_path(root, relative + "/response.txt")
        if job.response_sha256 is not None and sha256(bounded_read(response_path)) != (
            job.response_sha256
        ):
            raise ValueError("RESERVED_RESPONSE_CHANGED")
        if job.state != "completed":
            continue
        if finish["state"] != "returned":
            raise ValueError("RESERVED_COMPLETED_WITHOUT_RESPONSE")
        artifact_path = safe_path(root, relative + "/artifact.json")
        raw = bounded_read(artifact_path)
        if sha256(raw) != job.artifact_sha256:
            raise ValueError("RESERVED_ARTIFACT_CHANGED")
        replay = ReplayGenerator(bounded_read(response_path).decode("utf-8"), start)
        if job.stage == "analysis":
            analysis = SemanticAnalysisV3.model_validate_json(raw)
            binding = next(c for c in request.protocol.reserved if c.case_id == job.case_id)
            if analysis.extraction.request.original_sha256 != binding.input_sha256:
                raise ValueError("RESERVED_ANALYSIS_INPUT_CHANGED")
            reconstructed = analyze_composition(
                extract_grounding(cases[job.case_id].project),
                replay,
                program_version="semantic-composition/v3.4",
            )
            if reconstructed != analysis:
                raise ValueError("RESERVED_RESPONSE_ARTIFACT_CONTRADICTION")
            analyses[job.case_id, job.repetition] = analysis
            program = composition_program_digest(analysis.extraction, "semantic-composition/v3.4")
        else:
            audit = SemanticVerifierReportV4.model_validate_json(raw)
            analysis = analyses[job.case_id, job.repetition]
            if (
                audit.analysis != analysis
                or audit.requested_model != request.profile.requested_model
            ):
                raise ValueError("RESERVED_AUDIT_CHANGED")
            reconstructed_audit = audit_composition(
                analysis,
                replay,
                request.profile.requested_model,
                program_version="component-audit/v4.1",
            )
            if reconstructed_audit != audit:
                raise ValueError("RESERVED_RESPONSE_ARTIFACT_CONTRADICTION")
            program = component_audit_program_digest(analysis, "component-audit/v4.1")
        if analysis.snapshot_sha256 != job.analysis_sha256 or json.loads(
            bounded_read(safe_path(root, relative + "/program.json"))
        ) != {"program_sha256": program}:
            raise ValueError("RESERVED_PROGRAM_OR_ANALYSIS_CHANGED")
    if set(output.glob("job-*/call-start.json")) != expected_starts:
        raise ValueError("RESERVED_UNACCOUNTED_INVOCATIONS")
    return report


class ReplayGenerator:
    """Reconstruct saved contracts without provider access, retries or semantic judgment."""

    def __init__(self, response: str, receipt: dict[str, Any]) -> None:
        self.response, self.receipt = response, receipt

    def generate_json(self, prompt: str, schema: dict[str, Any]) -> str:
        from ai_harness_compiler.adapters.codex_cli import strict_schema

        if (
            self.receipt.get("prompt_sha256") != sha256(prompt.encode())
            or self.receipt.get("response_schema_sha256") != canonical_project_digest(schema)
            or self.receipt.get("effective_schema_sha256")
            != canonical_project_digest(strict_schema(schema))
        ):
            raise ValueError("RESERVED_REQUEST_RECEIPT_CONTRADICTION")
        return self.response
