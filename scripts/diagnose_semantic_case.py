"""Offline structural diagnosis; never executes a provider or rewrites an assessment."""

import argparse
from dataclasses import asdict
from pathlib import Path

from ai_harness_compiler.case_diagnostics import diagnose_case
from ai_harness_compiler.models.semantic_analysis_v3 import SemanticAnalysisV3
from ai_harness_compiler.models.semantic_assessment import AssessmentCase
from ai_harness_compiler.reserved_runs import bounded_read, write_new

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--case", type=Path, required=True)
parser.add_argument("--analysis", type=Path, required=True)
parser.add_argument(
    "--output", type=Path, required=True, help="New file; existing files are preserved"
)
args = parser.parse_args()
case = AssessmentCase.model_validate_json(bounded_read(args.case))
analysis = SemanticAnalysisV3.model_validate_json(bounded_read(args.analysis))
write_new(args.output, asdict(diagnose_case(case, analysis)))
print("Structural diagnostic saved; assessments and semantic authority unchanged.")
