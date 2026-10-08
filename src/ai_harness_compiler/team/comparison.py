"""Optional LangGraph fan-out with no tools, retries, selection or approval."""

import operator
import time
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Annotated, TypedDict

from langgraph.graph import END, START, StateGraph
from langgraph.types import Send
from langsmith import tracing_context

from ai_harness_compiler.models.compact_analysis import CompactAnalysisSpec
from ai_harness_compiler.models.comparison import (
    ComparisonCandidateResult,
    ComparisonReport,
    Provider,
    criterion_inventory,
)
from ai_harness_compiler.models.grounding import GroundingExtraction


@dataclass(frozen=True)
class ComparisonCandidateConfig:
    provider: Provider
    requested_model: str
    program_sha256: str | None = None


class ComparisonState(TypedDict, total=False):
    candidate_id: str
    results: Annotated[list[ComparisonCandidateResult], operator.add]


def run_comparison(
    extraction: GroundingExtraction,
    providers: Mapping[str, Callable[[GroundingExtraction], CompactAnalysisSpec]],
    metadata: Mapping[str, ComparisonCandidateConfig],
    max_concurrency: int = 2,
) -> ComparisonReport:
    """Run exactly two calls; adapters must enforce their own call timeouts.

    This first experiment has no durable checkpoints or automatic resume. Provider
    functions receive independent validated copies, and must not execute tools.
    """
    extraction = GroundingExtraction.model_validate(extraction.model_dump())
    ids = list(metadata)
    if len(ids) != 2 or set(providers) != set(ids):
        raise ValueError("Exactly two matching provider/config identifiers are required")
    if type(max_concurrency) is not int or not 1 <= max_concurrency <= 2:
        raise ValueError("Comparison concurrency must be one or two")
    # Validate identifiers, config metadata and provider diversity before any call.
    probes = [
        ComparisonCandidateResult(
            id=id_,
            provider=metadata[id_].provider,
            requested_model=metadata[id_].requested_model,
            program_sha256=metadata[id_].program_sha256,
            status="error",
            elapsed_seconds=0.0,
            error_code="provider-error",
        )
        for id_ in ids
    ]
    if {p.provider for p in probes} != {"ollama", "codex-cli"}:
        raise ValueError("One candidate from each provider is required")
    # Freeze caller-owned mappings before concurrent execution.
    calls = dict(providers)
    configs = dict(metadata)

    def dispatch(state: ComparisonState) -> list[Send]:
        return [Send("candidate", {"candidate_id": id_}) for id_ in ids]

    def candidate(state: ComparisonState) -> ComparisonState:
        id_ = state["candidate_id"]
        config = configs[id_]
        start = time.monotonic()
        analysis = None
        status, error = "completed", None
        try:
            analysis = calls[id_](GroundingExtraction.model_validate(extraction.model_dump()))
            analysis = CompactAnalysisSpec.model_validate(analysis.model_dump())
            if analysis.extraction != extraction:
                raise ValueError("Provider changed original extraction")
        except TimeoutError:
            analysis = None
            status, error = "timeout", "provider-timeout"
        except ValueError:
            analysis = None
            status, error = "error", "invalid-proposal"
        except Exception:
            analysis = None
            status, error = "error", "provider-error"
        result = ComparisonCandidateResult.model_validate(
            {
                "id": id_,
                "provider": config.provider,
                "requested_model": config.requested_model,
                "program_sha256": config.program_sha256,
                "status": status,
                "elapsed_seconds": time.monotonic() - start,
                "compact_analysis": analysis,
                "error_code": error,
            }
        )
        return {"results": [result]}

    builder = StateGraph(ComparisonState)
    builder.add_node("candidate", candidate)
    builder.add_node("consolidate", lambda state: {})
    builder.add_conditional_edges(START, dispatch, ["candidate"])
    builder.add_edge("candidate", "consolidate")
    builder.add_edge("consolidate", END)
    graph = builder.compile()
    started = time.monotonic()
    with tracing_context(enabled=False):
        state = graph.invoke(
            {"results": []},
            {"max_concurrency": max_concurrency, "recursion_limit": 4},
        )
    wall = time.monotonic() - started
    results = sorted(state["results"], key=lambda result: ids.index(result.id))
    agreement, disagreement, unavailable = criterion_inventory(extraction, results)
    return ComparisonReport(
        extraction=extraction,
        input_sha256=extraction.request.original_sha256,
        candidates=results,
        criterion_agreements=agreement,
        criterion_disagreements=disagreement,
        unavailable_criteria=unavailable,
        wall_time_seconds=wall,
        total_call_seconds=sum(r.elapsed_seconds for r in results),
    )
