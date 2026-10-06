"""Run fresh offline builds; record measured samples without asserting an SLO."""

import hashlib
import platform
from pathlib import Path
from statistics import median
from time import perf_counter_ns

import pydantic

from ai_harness_compiler import __version__
from ai_harness_compiler.compiler import compile_harness, json_text, verify_bundle
from ai_harness_compiler.intake import DEFAULT_MAX_MANIFEST_BYTES, load_project
from ai_harness_compiler.models.benchmark import (
    BenchmarkCase,
    BenchmarkReport,
    BenchmarkSample,
    BenchmarkSuite,
)
from ai_harness_compiler.pipeline import plan


def bounded_bytes(path: Path) -> bytes:
    with path.open("rb") as stream:
        content = stream.read(DEFAULT_MAX_MANIFEST_BYTES + 1)
    if len(content) > DEFAULT_MAX_MANIFEST_BYTES:
        raise ValueError("BENCHMARK_SIZE: Suite/fixture exceeds 1 MiB.")
    return content


def run_benchmark(suite_path: Path, workspace: Path, *, runs: int = 3) -> BenchmarkReport:
    if isinstance(runs, bool) or not isinstance(runs, int) or runs < 2:
        raise ValueError("BENCHMARK_RUNS: At least two runs are required for reproducibility.")
    suite_bytes = bounded_bytes(suite_path)
    suite = BenchmarkSuite.model_validate_json(suite_bytes)
    base = suite_path.resolve().parent
    paths = []
    for fixture in suite.fixtures:
        path = (base / fixture.manifest).resolve()
        if Path(fixture.manifest).is_absolute() or not path.is_relative_to(base):
            raise ValueError("BENCHMARK_PATH: Fixture must stay inside suite directory.")
        paths.append(path)
    # Own this session only; never reuse another benchmark/project output directory.
    workspace.mkdir(parents=True, exist_ok=False)
    cases = []
    for fixture, path in zip(suite.fixtures, paths, strict=True):
        samples = []
        input_digest = hashlib.sha256(bounded_bytes(path)).hexdigest()
        for run in range(runs):
            started = perf_counter_ns()
            project = load_project(path)
            if hashlib.sha256(bounded_bytes(path)).hexdigest() != input_digest:
                raise ValueError("BENCHMARK_INPUT_CHANGED: Fixture changed during measurement.")
            spec = plan(project)
            if project.domain != fixture.domain or {item.id for item in project.backlog} != set(
                fixture.capability_ids
            ):
                raise ValueError(
                    "BENCHMARK_CRITERIA: Fixture does not match declared domain/capabilities."
                )
            if len(spec.evals) != fixture.acceptance_criteria_count:
                raise ValueError(
                    "BENCHMARK_CRITERIA: Acceptance coverage count differs from suite."
                )
            output = compile_harness(spec, workspace / fixture.id / f"run-{run + 1}")
            digests = verify_bundle(output)
            byte_count = sum((output / name).stat().st_size for name in digests)
            elapsed = (perf_counter_ns() - started) / 1_000_000
            samples.append(
                BenchmarkSample(
                    duration_ms=elapsed,
                    artifact_bytes=byte_count,
                    file_count=len(digests),
                    bundle_sha256=hashlib.sha256(json_text(digests).encode("utf-8")).hexdigest(),
                )
            )
        if len({sample.bundle_sha256 for sample in samples}) != 1:
            raise ValueError("BENCHMARK_REPRODUCIBILITY: Same fixture produced different bytes.")
        cases.append(
            BenchmarkCase(
                fixture_id=fixture.id,
                domain=fixture.domain,
                input_sha256=input_digest,
                samples=samples,
                median_ms=float(median(sample.duration_ms for sample in samples)),
            )
        )
    return BenchmarkReport(
        compiler_version=__version__,
        compiler_source_sha256=hashlib.sha256(
            json_text(
                {
                    path.relative_to(Path(__file__).parent).as_posix(): hashlib.sha256(
                        path.read_bytes()
                    ).hexdigest()
                    for path in sorted(Path(__file__).parent.rglob("*.py"))
                }
            ).encode("utf-8")
        ).hexdigest(),
        python_version=platform.python_version(),
        python_implementation=platform.python_implementation(),
        platform_system=platform.system(),
        platform_release=platform.release(),
        pydantic_version=pydantic.__version__,
        suite_sha256=hashlib.sha256(suite_bytes).hexdigest(),
        runs_per_fixture=runs,
        cases=cases,
    )
