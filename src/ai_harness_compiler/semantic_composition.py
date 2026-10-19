"""Component-grounded generation and advisory auditing; no execution or host repair."""

import json
from copy import deepcopy
from typing import Any

from ai_harness_compiler.models.compact_analysis import compact_context, compact_input
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.semantic_analysis_v3 import AnalysisProposalV3, SemanticAnalysisV3
from ai_harness_compiler.models.semantic_verification_v4 import (
    VERIFIER_PROMPT_V4,
    SemanticVerifierReportV4,
    VerifierProposalV4,
    verification_v4_program_digest,
)
from ai_harness_compiler.semantic_verification import (
    ANALYSIS_PROMPT,
    JSONGenerator,
    analysis_response_schema,
)

COMPOSITION_PROGRAM_VERSION = "semantic-composition/v3.1"
COMPOSITION_PROMPT = (
    ANALYSIS_PROMPT.replace("SemanticAnalysisProposal/v2", "SemanticAnalysisProposal/v3")
    + """
Each rule condition, outcome and exception is EvidenceText: text plus exact source_atom_ids.
Source IDs correspond to context_atom_ids below; preserve each criterion's source_atom_id
and order. Each component must cite sources supporting that component, not merely a nearby
permission. Do not add separately declared guards to the original authorization rule.
Represent those restrictions as separate guards with condition, effect and their own sources.
target_scope=criteria applies a guard to specified criterion atom IDs; project scope requires
an empty target list and covers broader declared operations not all represented as criteria.
A guard restricts an applicable operation; it never grants authorization or overrides a
confirmed rule. Target identifiers are applicability links, not supporting quotations.
If a criterion itself contains an intrinsic qualification, keep it with the relevant sources.
Do not invent guards or condition exceptions; every addition requires exact supporting atoms.
"""
)


def composition_response_schema(extraction: GroundingExtraction) -> dict[str, Any]:
    extraction = GroundingExtraction.model_validate(extraction.model_dump())
    schema = AnalysisProposalV3.model_json_schema()
    criteria = [a.id for a in extraction.atoms if a.kind == "acceptance-criterion"]
    schema["properties"]["criteria"].update(minItems=len(criteria), maxItems=len(criteria))
    schema["$defs"]["AnalysisIssue"] = analysis_response_schema(extraction)["$defs"][
        "AnalysisIssue"
    ]
    schema["$defs"]["EvidenceText"]["properties"]["source_atom_ids"]["items"] = {
        "type": "string",
        "enum": [a.id for a in compact_context(extraction)],
    }
    criterion = schema["$defs"]["CriterionV3"]
    criterion_variants = []
    for kind in ("business-rule", "requirement", "needs-clarification"):
        variant = deepcopy(criterion)
        properties = variant["properties"]
        properties["kind"] = {"type": "string", "const": kind}
        if kind == "business-rule":
            for name in ("condition", "outcome"):
                properties[name] = {"$ref": "#/$defs/EvidenceText"}
            properties["question"] = {"type": "null"}
        else:
            for name in ("condition", "outcome"):
                properties[name] = {"type": "null"}
            properties["exceptions"]["maxItems"] = 0
            properties["question"] = (
                {"$ref": "#/$defs/MaterialQuestion"}
                if kind == "needs-clarification"
                else {"type": "null"}
            )
        criterion_variants.append(variant)
    schema["$defs"]["CriterionV3"] = {"anyOf": criterion_variants}
    guard = schema["$defs"]["GuardSpec"]
    variants = []
    for scope in ("project", "criteria"):
        variant = deepcopy(guard)
        variant["properties"]["target_scope"] = {"type": "string", "const": scope}
        target = variant["properties"]["target_criterion_atom_ids"]
        target["items"] = {"type": "string", "enum": criteria}
        target.update({"maxItems": 0} if scope == "project" else {"minItems": 1})
        variants.append(variant)
    schema["$defs"]["GuardSpec"] = {"anyOf": variants}
    return schema


def analyze_composition(
    extraction: GroundingExtraction, generator: JSONGenerator
) -> SemanticAnalysisV3:
    packet = compact_input(extraction).model_dump()
    packet["criterion_atom_ids"] = [
        a.id for a in extraction.atoms if a.kind == "acceptance-criterion"
    ]
    packet["context_atom_ids"] = [a.id for a in compact_context(extraction)]
    proposal = AnalysisProposalV3.model_validate_json(
        generator.generate_json(
            COMPOSITION_PROMPT + "\nINPUT DATA:\n" + json.dumps(packet, ensure_ascii=False),
            composition_response_schema(extraction),
        )
    )
    return SemanticAnalysisV3(extraction=extraction, proposal=proposal)


def component_audit_schema(analysis: SemanticAnalysisV3) -> dict[str, Any]:
    analysis = SemanticAnalysisV3.model_validate(analysis.model_dump())
    schema = VerifierProposalV4.model_json_schema()
    schema["properties"]["findings"].update(
        minItems=len(analysis.findings), maxItems=len(analysis.findings)
    )
    schema["properties"]["source_coverage"].update(
        minItems=len(analysis.sources), maxItems=len(analysis.sources)
    )
    count = sum(len(f.component_bindings) for f in analysis.findings)
    schema["properties"]["component_judgments"].update(minItems=count, maxItems=count)
    finding_key = schema["properties"]["findings"]["items"]["$ref"].rsplit("/", 1)[-1]
    base = schema["$defs"][finding_key]
    variants = []
    for question in (False, True):
        ids = [f.id for f in analysis.findings if (f.kind == "question") == question]
        if not ids:
            continue
        variant = deepcopy(base)
        variant["properties"]["finding_id"] = {"type": "string", "enum": ids}
        variant["properties"]["materiality"] = {
            "type": "string",
            "enum": ["appropriate", "inappropriate"] if question else ["not-applicable"],
        }
        variants.append(variant)
    schema["$defs"][finding_key] = {"anyOf": variants}
    component = schema["$defs"]["ComponentJudgment"]
    variants = []
    for name in ("condition", "outcome", "exception"):
        variant = deepcopy(component)
        variant["properties"]["component_name"] = {"type": "string", "const": name}
        variant["properties"]["component_index"] = (
            {"type": "integer", "minimum": 0} if name == "exception" else {"type": "null"}
        )
        variants.append(variant)
    schema["$defs"]["ComponentJudgment"] = {"anyOf": variants}
    omission = schema["$defs"]["MissingFinding"]
    variants = []
    for kind in ("rule", "question", "conflict"):
        variant = deepcopy(omission)
        variant["properties"]["kind"] = {"type": "string", "const": kind}
        variant["properties"]["impact"] = (
            {"type": "string", "enum": ["rule", "authorization", "outcome", "precedence"]}
            if kind == "question"
            else {"type": "null"}
        )
        if kind == "conflict":
            variant["properties"]["source_atom_ids"]["minItems"] = 2
        variants.append(variant)
    schema["$defs"]["MissingFinding"] = {"anyOf": variants}
    return schema


def audit_composition(
    analysis: SemanticAnalysisV3, generator: JSONGenerator, requested_model: str
) -> SemanticVerifierReportV4:
    analysis = SemanticAnalysisV3.model_validate(analysis.model_dump())
    payload = {
        "analysis_sha256": analysis.snapshot_sha256,
        "findings": [f.model_dump() | {"finding_sha256": f.sha256} for f in analysis.findings],
        "sources": [s.model_dump() for s in analysis.sources],
        "disposition": analysis.disposition,
        "content_trust": "untrusted-data",
    }
    proposal = VerifierProposalV4.model_validate_json(
        generator.generate_json(
            VERIFIER_PROMPT_V4 + "\nINPUT DATA:\n" + json.dumps(payload, ensure_ascii=False),
            component_audit_schema(analysis),
        )
    )
    return SemanticVerifierReportV4(
        analysis=analysis,
        proposal=proposal,
        requested_model=requested_model,
        program_sha256=verification_v4_program_digest(),
    )
