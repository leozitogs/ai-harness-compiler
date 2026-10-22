"""Explicit offline preflight; no provider, assets or model invocation."""

import argparse
import json
from pathlib import Path

from ai_harness_compiler.compiler import json_text
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.models.semantic_case_v3 import AssessmentCaseV3
from ai_harness_compiler.models.semantic_preflight import AnalysisVersion, preflight_case

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--case", type=Path, required=True)
parser.add_argument(
    "--target", choices=["SemanticAnalysis/v3", "SemanticAnalysis/v4"], required=True
)
parser.add_argument(
    "--output", type=Path, required=True, help="New private report; contains expectations"
)
args = parser.parse_args()
try:
    with args.case.open("rb") as stream:
        raw = stream.read(2 * 1024 * 1024 + 1)
    if len(raw) > 2 * 1024 * 1024:
        raise ValueError("Case size limit")
    models = {"AssessmentCase/v2": AssessmentCase, "AssessmentCase/v3": AssessmentCaseV3}
    data = json.loads(raw)
    version = data.get("schema_version") if isinstance(data, dict) else None
    if not isinstance(version, str) or version not in models:
        raise ValueError("Explicit supported case version required")
    case = models[version].model_validate_json(raw)
    target: AnalysisVersion = args.target
    report = preflight_case(case, target)
    payload = json_text(report.model_dump()).encode("utf-8")
    if len(payload) > 4 * 1024 * 1024:
        raise ValueError("Report size limit")
    with args.output.open("xb") as stream:
        stream.write(payload)
except (OSError, ValueError):
    parser.error("Invalid/inaccessible input or output already exists; no model invoked")
print(f"Representability: {report.status}; no execution authorized or model invoked.")
raise SystemExit(0 if report.status == "compatible" else 2)
