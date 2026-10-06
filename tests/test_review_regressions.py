"""Independent review reproductions must fail before export/deserialization succeeds."""

import copy
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from ai_harness_compiler.compiler import compile_harness
from ai_harness_compiler.intake import load_project
from ai_harness_compiler.models import HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.benchmark import BenchmarkReport
from ai_harness_compiler.pipeline import plan

ROOT = Path(__file__).resolve().parents[1]


def supplied_ir():
    project = load_project(ROOT / "examples/evidence-pack").model_dump()
    project["evidence_pack"]["sources"][0]["verification_status"] = "rejected"
    return plan(ProjectInput.model_validate(project)).model_dump()


@pytest.mark.parametrize(
    "mutation",
    [
        "claim",
        "reactivation",
        "remove-source",
        "remove-claim",
        "extra-source",
        "extra-claim",
        "combined",
    ],
)
def test_supplied_snapshot_cannot_be_edited_independently(mutation, tmp_path):
    payload = supplied_ir()
    dna = payload["project_dna"]
    source = dna["sources"][-1]
    claim = dna["evidence"][-1]
    if mutation in {"claim", "combined"}:
        claim["claim"] = "Changed claim absent from input"
    if mutation in {"reactivation", "combined"}:
        source["verification_status"] = "unverified"
        payload["capability_graph"]["capabilities"][0]["evidence_ids"].append(claim["id"])
    if mutation == "remove-source":
        dna["sources"].pop()
        dna["evidence"].pop()
    if mutation == "remove-claim":
        dna["evidence"].pop()
    if mutation == "extra-source":
        new = copy.deepcopy(source)
        new["id"] = "detached-source"
        dna["sources"].append(new)
    if mutation == "extra-claim":
        new = copy.deepcopy(claim)
        new["id"] = "detached-claim"
        dna["evidence"].append(new)
    output = tmp_path / "invalid"
    with pytest.raises(ValidationError):
        compile_harness(HarnessSpec.model_validate(payload), output)
    with pytest.raises(ValidationError):
        ProjectDNA.model_validate(dna)
    assert not output.exists()


def test_valid_supplied_records_can_be_reordered_and_roundtripped():
    payload = supplied_ir()
    payload["project_dna"]["sources"].reverse()
    payload["project_dna"]["evidence"].reverse()
    spec = HarnessSpec.model_validate(payload)
    assert HarnessSpec.model_validate_json(spec.model_dump_json()) == spec


@pytest.mark.parametrize(
    "mutation",
    ["hash", "median", "runs", "one-sample", "duplicate-case", "bytes", "file-count", "combined"],
)
def test_contradictory_benchmark_is_rejected(mutation):
    payload = json.loads(
        (ROOT / "benchmarks/results/baseline-windows-python313.json").read_text(encoding="utf-8")
    )
    case = payload["cases"][0]
    if mutation in {"hash", "combined"}:
        case["samples"][1]["bundle_sha256"] = "0" * 64
    if mutation in {"median", "combined"}:
        case["median_ms"] = 0.0
    if mutation in {"runs", "combined"}:
        payload["runs_per_fixture"] = 99
    if mutation == "one-sample":
        case["samples"] = case["samples"][:1]
        case["median_ms"] = case["samples"][0]["duration_ms"]
    if mutation == "duplicate-case":
        payload["cases"].append(copy.deepcopy(case))
    if mutation == "bytes":
        case["samples"][1]["artifact_bytes"] += 1
    if mutation == "file-count":
        case["samples"][1]["file_count"] += 1
    with pytest.raises(ValidationError):
        BenchmarkReport.model_validate(payload)
    with pytest.raises(ValidationError):
        BenchmarkReport.model_validate_json(json.dumps(payload))


def test_published_baseline_is_still_a_consistent_report():
    report = BenchmarkReport.model_validate_json(
        (ROOT / "benchmarks/results/baseline-windows-python313.json").read_text(encoding="utf-8")
    )
    assert len(report.cases) == 3 and report.runs_per_fixture == 5
