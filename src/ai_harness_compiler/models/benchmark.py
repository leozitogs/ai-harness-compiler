"""Offline compiler measurements are separate from target product evaluations."""

from statistics import median
from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.evidence import Digest


class BenchmarkFixture(Contract):
    id: Identifier
    manifest: Text
    domain: Text
    capability_ids: list[Identifier] = Field(min_length=1)
    acceptance_criteria_count: int = Field(gt=0)


class BenchmarkSuite(Contract):
    schema_version: Literal["BenchmarkSuite/v1"] = "BenchmarkSuite/v1"
    fixtures: list[BenchmarkFixture] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_ids(self) -> Self:
        if len({item.id for item in self.fixtures}) != len(self.fixtures):
            raise ValueError("Benchmark fixture IDs must be unique")
        for item in self.fixtures:
            if len(item.capability_ids) != len(set(item.capability_ids)):
                raise ValueError("Expected capability IDs must be unique")
        return self


class BenchmarkSample(Contract):
    duration_ms: float = Field(ge=0, allow_inf_nan=False)
    artifact_bytes: int = Field(gt=0)
    file_count: int = Field(gt=0)
    bundle_sha256: Digest


class BenchmarkCase(Contract):
    fixture_id: Identifier
    domain: Text
    input_sha256: Digest
    samples: list[BenchmarkSample] = Field(min_length=2)
    median_ms: float = Field(ge=0, allow_inf_nan=False)
    reproducible: Literal[True] = True
    integrity_status: Literal["passed"] = "passed"

    @model_validator(mode="after")
    def validate_measurements(self) -> Self:
        if len({item.bundle_sha256 for item in self.samples}) != 1:
            raise ValueError("Reproducible samples must have identical bundle hashes")
        if len({(item.artifact_bytes, item.file_count) for item in self.samples}) != 1:
            raise ValueError("Identical bundles must have identical sizes and file counts")
        if self.median_ms != median(item.duration_ms for item in self.samples):
            raise ValueError("Reported median must equal the median of measured samples")
        return self


class BenchmarkReport(Contract):
    schema_version: Literal["CompilerBenchmark/v1"] = "CompilerBenchmark/v1"
    compiler_version: Text
    compiler_source_sha256: Digest
    python_version: Text
    python_implementation: Text
    platform_system: Text
    platform_release: Text
    pydantic_version: Text
    suite_sha256: Digest
    runs_per_fixture: int = Field(ge=2)
    clock: Literal["perf_counter_ns"] = "perf_counter_ns"
    timing_scope: Literal["intake-plan-compile-integrity"] = "intake-plan-compile-integrity"
    warmup_runs: Literal[0] = 0
    execution: Literal["sequential-same-process"] = "sequential-same-process"
    cases: list[BenchmarkCase] = Field(min_length=1)
    product_evaluation_status: Literal["not-run"] = "not-run"
    slo_status: Literal["not-defined"] = "not-defined"

    @model_validator(mode="after")
    def validate_cases(self) -> Self:
        if len({item.fixture_id for item in self.cases}) != len(self.cases):
            raise ValueError("Benchmark case IDs must be unique")
        if any(len(item.samples) != self.runs_per_fixture for item in self.cases):
            raise ValueError("Sample count must match runs_per_fixture for every case")
        return self
