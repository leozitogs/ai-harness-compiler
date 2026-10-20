"""Validate a saved real round offline; never reinterpret structural success as quality."""

import hashlib
import json
from pathlib import Path

from ai_harness_compiler.models.semantic_analysis_v3 import AnalysisProposalV3
from ai_harness_compiler.models.semantic_assessment_v3 import SemanticAssessmentV3
from ai_harness_compiler.models.semantic_verification_v4 import (
    SemanticVerifierReportV4,
    VerifierProposalV4,
)
from ai_harness_compiler.semantic_composition import composition_program_digest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/evidence/sprint-2-6-v33-development-20261020"


def test_v33_round_preserves_frozen_scope_budget_and_all_attempts():
    protocol_bytes = (EVIDENCE / "protocol-v2.json").read_bytes()
    protocol = json.loads(protocol_bytes)
    selection = json.loads((EVIDENCE / "protocol-selection.json").read_text(encoding="utf-8"))
    run = json.loads((EVIDENCE / "execution/summary.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(protocol_bytes).hexdigest() == selection["active_sha256"]
    assert run["protocol_sha256"] == selection["active_sha256"]
    assert (
        hashlib.sha256((EVIDENCE / "runner-source-v2.txt").read_bytes()).hexdigest()
        == (protocol["runner_sha256"])
    )
    for key in ["baseline_manifest", "development_manifest"]:
        source = protocol[key]
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
    assert protocol["budget"]["max_concurrency"] == 1
    assert protocol["budget"]["retries"] == protocol["budget"]["repair_attempts"] == 0
    assert protocol["budget"]["holdout_calls"] == 0
    assert len(run["cases"]) == 8
    assert run["calls_used"] == protocol["budget"]["max_calls"] == 16
    inventory = json.loads((EVIDENCE / "artifact-inventory.json").read_bytes())
    for artifact in inventory["artifacts"]:
        assert (
            hashlib.sha256((ROOT / artifact["path"]).read_bytes()).hexdigest() == artifact["sha256"]
        )
    starts = list((EVIDENCE / "execution").glob("*/*-call-start.json"))
    assert len(starts) == 16
    assert sorted(json.loads(p.read_bytes())["number"] for p in starts) == list(range(1, 17))
    for path in starts:
        start = json.loads(path.read_bytes())
        end = json.loads(path.with_name(path.name.replace("-start", "-finish")).read_bytes())
        assert end["status"] == "returned"
        assert 1 <= start["timeout_seconds"] <= 180
        assert all(start[k] == end[k] for k in start if k != "status")


def test_v33_initial_assessments_do_not_reuse_changed_historical_reviews():
    comparison = json.loads((EVIDENCE / "comparison.json").read_text(encoding="utf-8"))
    assert comparison["human_reviews_reused"] == 0
    assert comparison["assessments"] == {"pass": 0, "fail": 0, "not-run": 8, "error": 0}
    for row in comparison["cases"]:
        for source in row["sources"]:
            assert (
                hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
            )
        assert row["identical_to_baseline"] is False
        folder = EVIDENCE / "execution" / row["case"]
        assessment = SemanticAssessmentV3.model_validate_json(
            (folder / "assessment.json").read_bytes()
        )
        advice = SemanticVerifierReportV4.model_validate_json((folder / "advice.json").read_bytes())
        assert advice.analysis == assessment.analysis
        assert (
            AnalysisProposalV3.model_validate_json(
                (folder / "generation-response.txt").read_bytes()
            )
            == assessment.analysis.proposal
        )
        assert (
            VerifierProposalV4.model_validate_json((folder / "audit-response.txt").read_bytes())
            == advice.proposal
        )
        assert assessment.review is None and assessment.status == "not-run"
        assert assessment.analysis_sha256 == row["analysis_sha256"]
        assert composition_program_digest(
            assessment.analysis.extraction, "semantic-composition/v3.3"
        ) == next(
            c["program_sha256"]
            for c in json.loads((EVIDENCE / "protocol-v2.json").read_bytes())["cases"]
            if c["case"] == row["case"]
        )
        assert assessment.compilation_eligibility == "not-authorized"
        assert assessment.model_qualification == "not-established"


def test_fresh_po_judgments_keep_materiality_separate_from_source_support():
    manifest = json.loads((EVIDENCE / "human-review/manifest.json").read_bytes())
    assert manifest["assessments"] == {"pass_count": 6, "fail_count": 2, "not_run_count": 0}
    assert manifest["criteria_judged"] == 48 and manifest["criteria_pending"] == 0
    assert manifest["candidate_promoted"] is False
    for row in manifest["cases"]:
        source = row["assessment"]
        assert hashlib.sha256((ROOT / source["path"]).read_bytes()).hexdigest() == source["sha256"]
        assessment = SemanticAssessmentV3.model_validate_json((ROOT / source["path"]).read_bytes())
        assert assessment.status == row["status"]
        assert assessment.analysis.disposition == assessment.case.expected_behavior
        checks = {c.criterion: c.outcome for c in assessment.checks}
        assert checks["rule-coverage"] == checks["citation-support"] == "pass"
        assert checks["uncertainty"] == (
            "fail" if row["case"] in {"dev-ambiguous", "dev-branding-conflict"} else "pass"
        )
        assert assessment.compilation_eligibility == "not-authorized"
        assert assessment.model_qualification == "not-established"
