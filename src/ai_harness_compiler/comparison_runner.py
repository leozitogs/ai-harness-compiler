"""Exclusive development-only journals for one bounded two-provider comparison."""

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.base import Contract, Text
from ai_harness_compiler.models.compact_analysis import CompactAnalysisSpec
from ai_harness_compiler.models.comparison import ComparisonReport
from ai_harness_compiler.models.evidence import Digest
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.model_session import SessionSettings, WorkerRequest, WorkerResult
from ai_harness_compiler.models.semantic_eval import UnderstandingEvalCase
from ai_harness_compiler.semantic_eval import FrozenCorpus, bounded_bytes


class ComparisonPlan(Contract):
    schema_version: Literal["DevelopmentComparisonPlan/v1"] = "DevelopmentComparisonPlan/v1"
    split: Literal["development"] = "development"
    case: UnderstandingEvalCase
    corpus_sha256: Digest
    local_request: WorkerRequest
    codex_model: Text
    codex_timeout_seconds: int = Field(ge=1, le=300)
    codex_program_sha256: Digest
    max_calls: Literal[2] = 2
    retries: Literal[0] = 0

    @model_validator(mode="after")
    def consistent_scope(self) -> Self:
        request = WorkerRequest.model_validate(self.local_request.model_dump())
        settings = request.settings
        extraction = extract_grounding(self.case.project)
        if request.request != extraction.request or request.repair_feedback is not None:
            raise ValueError("Comparison worker must bind the canonical development case")
        if (
            settings.analysis_mode != "compact"
            or settings.max_attempts != 1
            or settings.repeats != 1
            or settings.expected_model_sha256 is None
            or settings.call_timeout_seconds != self.codex_timeout_seconds
            or settings.session_seconds != self.codex_timeout_seconds
        ):
            raise ValueError("Comparison requires one bounded compact call per provider")
        return self


def _write(path: Path, value: Contract) -> None:
    content = json_text(value.model_dump())
    if len(content.encode("utf-8")) > 2 * 1024 * 1024:
        raise ValueError("Comparison artifact exceeds byte budget")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)


def _bind_worker(plan: ComparisonPlan, result: WorkerResult) -> None:
    result = WorkerResult.model_validate(result.model_dump())
    if result.status != "completed":
        return
    if not result.identity or not result.settings or not result.compact_analysis:
        raise ValueError("Completed local evidence must contain compact analysis and identity")
    if (
        result.settings != plan.local_request.settings
        or result.identity.model_sha256 != plan.local_request.settings.expected_model_sha256
        or result.identity.prompt_sha256 != plan.local_request.prompt_sha256
        or result.compact_analysis.extraction != extract_grounding(plan.case.project)
    ):
        raise ValueError("Local worker differs from frozen comparison plan")


def run_development_comparison(
    corpus: FrozenCorpus,
    case_id: str,
    ollama_model: str,
    codex_model: str,
    expected_model_sha256: str,
    output: Path,
    timeout_seconds: int = 180,
) -> ComparisonReport:
    # Optional provider/framework imports do not enter the domain contracts.
    from ai_harness_compiler.adapters.codex_cli import (
        CodexCLISettings,
        CodexCompactModel,
        program_digest,
    )
    from ai_harness_compiler.adapters.ollama import prompt_digest
    from ai_harness_compiler.model_sessions import IsolatedOllamaExecutor
    from ai_harness_compiler.team.comparison import ComparisonCandidateConfig, run_comparison

    case = corpus.case("development", case_id)
    extraction = extract_grounding(case.project)
    codex = CodexCompactModel(CodexCLISettings(codex_model, timeout_seconds))
    settings = SessionSettings(
        model=ollama_model,
        analysis_mode="compact",
        repeats=1,
        max_attempts=1,
        session_seconds=timeout_seconds,
        call_timeout_seconds=timeout_seconds,
        expected_model_sha256=expected_model_sha256,
    )
    plan = ComparisonPlan(
        case=case,
        corpus_sha256=corpus.sha256,
        local_request=WorkerRequest(
            settings=settings,
            request=extraction.request,
            prompt_sha256=prompt_digest("compact"),
        ),
        codex_model=codex_model,
        codex_timeout_seconds=timeout_seconds,
        codex_program_sha256=program_digest(),
    )
    output.mkdir(parents=True, exist_ok=False)
    _write(output / "plan.json", plan)
    executor = IsolatedOllamaExecutor()

    def local(value: GroundingExtraction) -> CompactAnalysisSpec:
        try:
            result = WorkerResult.model_validate(
                executor.execute(
                    WorkerRequest.model_validate(plan.local_request.model_dump()),
                    float(timeout_seconds),
                ).model_dump()
            )
            _bind_worker(plan, result)
        except TimeoutError:
            result = WorkerResult(status="error", error_code="worker-timeout")
        except Exception:
            result = WorkerResult(status="error", error_code="worker-result-error")
        _write(output / "local-worker.json", result)
        if result.status != "completed":
            if result.error_code == "worker-timeout":
                raise TimeoutError("Local worker exceeded its deadline")
            raise ValueError("Local worker did not return a valid bound proposal")
        assert result.compact_analysis
        return result.compact_analysis

    def cloud(value: GroundingExtraction) -> CompactAnalysisSpec:
        return CompactAnalysisSpec(
            extraction=value,
            interpretation=codex.generate_compact(value),
        )

    report = run_comparison(
        extraction,
        {"local": local, "cloud": cloud},
        {
            "local": ComparisonCandidateConfig(
                "ollama", ollama_model, plan.local_request.prompt_sha256
            ),
            "cloud": ComparisonCandidateConfig("codex-cli", codex_model, plan.codex_program_sha256),
        },
    )
    _write(output / "comparison.json", report)
    return report


def validate_development_comparison(corpus: FrozenCorpus, output: Path) -> ComparisonReport:
    root = output.resolve()
    names = {"plan.json", "local-worker.json", "comparison.json"}
    if {p.name for p in root.iterdir()} != names:
        raise ValueError("Comparison journal must contain exactly its three artifacts")
    paths = {}
    for name in names:
        path = (root / name).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("Comparison artifact escapes its journal directory")
        paths[name] = path
    plan = ComparisonPlan.model_validate_json(bounded_bytes(paths["plan.json"]))
    if plan.corpus_sha256 != corpus.sha256 or plan.case != corpus.case("development", plan.case.id):
        raise ValueError("Comparison plan differs from frozen development corpus")
    worker = WorkerResult.model_validate_json(bounded_bytes(paths["local-worker.json"]))
    _bind_worker(plan, worker)
    report = ComparisonReport.model_validate_json(bounded_bytes(paths["comparison.json"]))
    if report.extraction != extract_grounding(plan.case.project):
        raise ValueError("Comparison report differs from planned canonical extraction")
    local, cloud = report.candidates
    if (
        [local.id, cloud.id] != ["local", "cloud"]
        or [local.provider, cloud.provider] != ["ollama", "codex-cli"]
        or local.requested_model != plan.local_request.settings.model
        or local.program_sha256 != plan.local_request.prompt_sha256
        or cloud.requested_model != plan.codex_model
        or cloud.program_sha256 != plan.codex_program_sha256
        or local.reported_model is not None
        or cloud.reported_model is not None
    ):
        raise ValueError("Comparison candidate metadata differs from its recorded plan")
    if worker.status == "completed":
        if local.status != "completed" or local.compact_analysis != worker.compact_analysis:
            raise ValueError("Comparison local proposal differs from its worker evidence")
    elif worker.error_code == "worker-timeout":
        if local.status != "timeout" or local.error_code != "provider-timeout":
            raise ValueError("Comparison timeout contradicts its worker evidence")
    elif local.status != "error" or local.error_code != "invalid-proposal":
        raise ValueError("Comparison failure contradicts its worker evidence")
    return report
