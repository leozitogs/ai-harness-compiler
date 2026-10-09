"""Offline protocol fixtures, not model execution or human semantic approval."""

import json
from pathlib import Path

from ai_harness_compiler.grounding import extract_grounding
from ai_harness_compiler.models.compact_analysis import (
    CompactAnalysisSpec,
    CompactProposal,
    compact_input,
)
from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.semantic_eval import (
    CRITERIA,
    SemanticReview,
    UnderstandingEvalReport,
    UnderstandingEvalSuite,
    UnderstandingRubric,
    case_checks,
)
from ai_harness_compiler.models.understanding import ProjectUnderstandingSpec
from ai_harness_compiler.understanding import prepare_understanding

root = Path(__file__).resolve().parents[1]
suite = UnderstandingEvalSuite.model_validate_json(
    (root / "evals/understanding/v1/development.json").read_bytes()
)
rubric = UnderstandingRubric.model_validate_json(
    (root / "evals/understanding/v1/rubric.json").read_bytes()
)
case = next(c for c in suite.cases if c.id == "dev-ambiguous")
request = prepare_understanding(case.project)
ref = next(r for r in request.references if r.pointer == case.required_rules[0].source_pointer)
spec = ProjectUnderstandingSpec(
    request=request,
    proposal={
        "questions": [
            {
                "id": "clarify",
                "question": (
                    "Quem deve confirmar a publicação e quais etapas são obrigatórias "
                    "no processo adequado?"
                ),
                "source_refs": [ref.id],
                "blocking": True,
            }
        ]
    },
)
print(
    json.dumps(
        {
            "scenario": "clarification-only",
            "checks": [(c.criterion, c.outcome) for c in case_checks(case, spec, None)],
        }
    )
)

x = extract_grounding(case.project)
p = CompactProposal(
    criteria=[
        {
            "kind": "business-rule",
            "condition": "Fixture condition",
            "outcome": "Fixture outcome",
            "note": "Protocol fixture, no semantic claim",
            "uncertainties": ["Qual formato do log?"],
        }
        for _ in compact_input(x).criteria
    ]
)
projected = CompactAnalysisSpec(extraction=x, interpretation=p).understanding
print(
    json.dumps(
        {
            "scenario": "implementation-detail-uncertainty",
            "questions": [(q.question, q.blocking) for q in projected.proposal.questions],
        }
    )
)

review = SemanticReview(
    reviewer="protocol-fixture-not-human",
    note="Reproduction only; not real semantic approval",
    case_sha256=canonical_project_digest(case.model_dump()),
    rubric_sha256=canonical_project_digest(rubric.model_dump()),
    proposal_sha256=canonical_project_digest(projected.proposal.model_dump()),
    checks=[
        {"criterion": c, "outcome": "not-run", "note": "Fixture pending aggregate"}
        for c in CRITERIA
    ],
    support=[
        {
            "item_id": projected.proposal.business_rules[0].id,
            "source_refs": projected.proposal.business_rules[0].source_refs,
            "outcome": "fail",
            "note": "Fixture negative support",
        }
    ],
)
report = UnderstandingEvalReport(
    case=case,
    rubric=rubric,
    corpus_sha256="0" * 64,
    split="development",
    understanding=projected,
    review=review,
    checks=case_checks(case, projected, review),
    status="not-run",
    input_sha256=request.original_sha256,
    proposal_sha256=canonical_project_digest(projected.proposal.model_dump()),
)
print(
    json.dumps(
        {
            "scenario": "negative-support-pending-aggregate",
            "accepted_status": report.status,
            "support_outcome": report.review.support[0].outcome,
        }
    )
)
