"""Component-grounded generation and advisory auditing; no execution or host repair."""

import json
from copy import deepcopy
from typing import Any, Literal

from ai_harness_compiler.models.compact_analysis import compact_context, compact_input
from ai_harness_compiler.models.evidence import canonical_project_digest
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
CANDIDATE_COMPOSITION_PROGRAM_VERSION = "semantic-composition/v3.2"
MULTISOURCE_COMPOSITION_PROGRAM_VERSION = "semantic-composition/v3.3"
MATERIALITY_COMPOSITION_PROGRAM_VERSION = "semantic-composition/v3.4"
CompositionProgramVersion = Literal[
    "semantic-composition/v3.1",
    "semantic-composition/v3.2",
    "semantic-composition/v3.3",
    "semantic-composition/v3.4",
]
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

# Candidate only: the operational default and the historical prompt stay unchanged.
CANDIDATE_COMPOSITION_PROMPT = (
    COMPOSITION_PROMPT
    + """
Preserve the normative force of every explicit obligation, including constraints outside
acceptance criteria. A declaration without a stated trigger must not acquire a trigger
from a nearby description, permission, role, or operation. The v3 guard contract requires
a condition: when no condition is supported, do not force the obligation into a guard.
Preserve it as an explicit normative context finding with subject=constraint, citing its
own original context indices, and state that its applicability was not specified.
Do not claim that this representation supplies an executable applicability policy.
Use guards only when their conditions AND effects are independently supported. A target
link alone does not establish that a condition applies to the obligation.
Do not equate roles or invent extra approval. Missing implementation details such as
assigning a named person do not block a clear rule unless they change its business meaning.
"""
)

MULTISOURCE_COMPOSITION_PROMPT = (
    CANDIDATE_COMPOSITION_PROMPT
    + """
In this program all secondary questions belong in issues with kind=question and exact
context_indices for every declaration needed by that question. Criterion uncertainties
must be empty: that local field inherits only the criterion atom and cannot cite other
sources. Keep a determinable business rule even when a separate issue asks for precedence.
A question comparing declarations must itself cite both sides; a separate well-sourced
conflict or globally visible context cannot repair the question's own missing citation.
Do not add all context indices indiscriminately. Cite only the original declarations
supporting this question and its stated material impact. Preserve ambiguity without
choosing precedence. A primary needs-clarification question may remain on a criterion
only when its text and rationale are supported by that criterion alone; otherwise retain
the known criterion content and express the cross-source question as an issue.
"""
)

MATERIALITY_COMPOSITION_PROMPT = (
    MULTISOURCE_COMPOSITION_PROMPT
    + """
Assess each question independently at the scope of project-intent analysis, not runtime
implementation. A question is blocking only when its unresolved answer is needed to
determine a declared rule, authorization, outcome, or precedence. In its concise rationale,
identify the specific source-bound business decision that cannot be determined. An already
blocked project does not justify adding other blockers; source support alone does not
establish materiality. Do not invent alternative rules to manufacture an ambiguity.
Preserve an explicit unconditional obligation as normative context even if execution timing,
implementation mechanism, or assignment of a person is absent. Such absence alone does not
prevent understanding that obligation. Record the limitation in context_findings; if a useful
follow-up question is retained, use impact=implementation-detail rather than impact=rule.
This is not a blanket exemption: unresolved permission, conflicting declared obligations,
missing business completion conditions, and genuinely indeterminate responsible roles may
still require a blocking question when the cited declarations establish that dependency.
Do not suppress these questions to obtain ready. Do not claim implementation-detail supplies
runtime enforcement or authorization. Keep legitimate conflicts and blockers, preserve all
known rules, and never treat a positive audit or ready/blocked match as human approval.
"""
)


def composition_prompt(program_version: CompositionProgramVersion) -> str:
    """Select an explicit recipe without promoting the unqualified candidate."""
    if program_version == COMPOSITION_PROGRAM_VERSION:
        return COMPOSITION_PROMPT
    if program_version == CANDIDATE_COMPOSITION_PROGRAM_VERSION:
        return CANDIDATE_COMPOSITION_PROMPT
    if program_version == MULTISOURCE_COMPOSITION_PROGRAM_VERSION:
        return MULTISOURCE_COMPOSITION_PROMPT
    if program_version == MATERIALITY_COMPOSITION_PROGRAM_VERSION:
        return MATERIALITY_COMPOSITION_PROMPT
    raise ValueError("Unknown composition program version")


def composition_program_digest(
    extraction: GroundingExtraction,
    program_version: CompositionProgramVersion = "semantic-composition/v3.1",
) -> str:
    """Bind the selected prompt and dynamic response schema for future comparisons."""
    return canonical_project_digest(
        {
            "program_version": program_version,
            "prompt": composition_prompt(program_version),
            "response_schema": composition_response_schema(
                extraction, program_version=program_version
            ),
        }
    )


def composition_response_schema(
    extraction: GroundingExtraction,
    *,
    program_version: CompositionProgramVersion = "semantic-composition/v3.1",
) -> dict[str, Any]:
    composition_prompt(program_version)
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
    if program_version in (
        MULTISOURCE_COMPOSITION_PROGRAM_VERSION,
        MATERIALITY_COMPOSITION_PROGRAM_VERSION,
    ):
        criterion["properties"]["uncertainties"]["maxItems"] = 0
        for variant in schema["$defs"]["AnalysisIssue"]["anyOf"]:
            indices = variant["properties"]["context_indices"]
            indices["items"] = {
                "type": "integer",
                "enum": list(range(len(compact_context(extraction)))),
            }
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
    extraction: GroundingExtraction,
    generator: JSONGenerator,
    *,
    program_version: CompositionProgramVersion = "semantic-composition/v3.1",
) -> SemanticAnalysisV3:
    prompt = composition_prompt(program_version)
    packet = compact_input(extraction).model_dump()
    packet["criterion_atom_ids"] = [
        a.id for a in extraction.atoms if a.kind == "acceptance-criterion"
    ]
    packet["context_atom_ids"] = [a.id for a in compact_context(extraction)]
    proposal = AnalysisProposalV3.model_validate_json(
        generator.generate_json(
            prompt + "\nINPUT DATA:\n" + json.dumps(packet, ensure_ascii=False),
            composition_response_schema(extraction, program_version=program_version),
        )
    )
    if program_version in (
        MULTISOURCE_COMPOSITION_PROGRAM_VERSION,
        MATERIALITY_COMPOSITION_PROGRAM_VERSION,
    ) and any(criterion.uncertainties for criterion in proposal.criteria):
        raise ValueError(
            "COMPOSITION_QUESTION_ROUTE: Secondary questions must use source-bound issues"
        )
    return SemanticAnalysisV3(extraction=extraction, proposal=proposal)


ComponentAuditProgramVersion = Literal["component-audit/v4.0", "component-audit/v4.1"]
BOUND_COMPONENT_AUDIT_PROGRAM_VERSION = "component-audit/v4.1"


def component_audit_schema(
    analysis: SemanticAnalysisV3,
    *,
    program_version: ComponentAuditProgramVersion = "component-audit/v4.0",
) -> dict[str, Any]:
    if program_version not in ("component-audit/v4.0", BOUND_COMPONENT_AUDIT_PROGRAM_VERSION):
        raise ValueError("Unknown component audit program version")
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
    if program_version == BOUND_COMPONENT_AUDIT_PROGRAM_VERSION:
        _bind_audit_inventory(schema, analysis, finding_key, base)
    return schema


def _exact_array(values: list[str]) -> dict[str, Any]:
    """Use an exact value without normalizing or repairing a model response."""
    return {"type": "array", "const": values, "items": {"type": "string"}}


def _bind_audit_inventory(
    schema: dict[str, Any],
    analysis: SemanticAnalysisV3,
    finding_key: str,
    base: dict[str, Any],
) -> None:
    schema["properties"]["analysis_sha256"] = {"type": "string", "const": analysis.snapshot_sha256}
    variants = []
    for finding in analysis.findings:
        variant = deepcopy(base)
        props = variant["properties"]
        props["finding_id"] = {"type": "string", "const": finding.id}
        props["finding_sha256"] = {"type": "string", "const": finding.sha256}
        props["source_atom_ids"] = _exact_array(finding.source_atom_ids)
        props["materiality"] = {
            "type": "string",
            "enum": ["appropriate", "inappropriate"]
            if finding.kind == "question"
            else ["not-applicable"],
        }
        variants.append(variant)
    schema["$defs"][finding_key] = {"anyOf": variants}
    component = VerifierProposalV4.model_json_schema()["$defs"]["ComponentJudgment"]
    variants = []
    for finding in analysis.findings:
        for binding in finding.component_bindings:
            variant = deepcopy(component)
            props = variant["properties"]
            props["finding_id"] = {"type": "string", "const": finding.id}
            props["component_name"] = {"type": "string", "const": binding.name}
            props["component_index"] = (
                {"type": "null"}
                if binding.index is None
                else {"type": "integer", "const": binding.index}
            )
            props["source_atom_ids"] = _exact_array(binding.source_atom_ids)
            variants.append(variant)
    if variants:
        schema["$defs"]["ComponentJudgment"] = {"anyOf": variants}
    else:
        schema["properties"]["component_judgments"]["maxItems"] = 0
    coverage = VerifierProposalV4.model_json_schema()["$defs"]["SourceCoverage"]
    variants = []
    for source in analysis.sources:
        variant = deepcopy(coverage)
        props = variant["properties"]
        props["atom_id"] = {"type": "string", "const": source.atom_id}
        props["quote_sha256"] = {"type": "string", "const": source.quote_sha256}
        variants.append(variant)
    schema["$defs"]["SourceCoverage"] = {"anyOf": variants}


def component_audit_program_digest(
    analysis: SemanticAnalysisV3,
    program_version: ComponentAuditProgramVersion = "component-audit/v4.0",
) -> str:
    """Recipe fingerprint is separate from the unchanged report's logical v4 program."""
    return canonical_project_digest(
        {
            "program_version": program_version,
            "logical_program_sha256": verification_v4_program_digest(),
            "prompt": VERIFIER_PROMPT_V4,
            "response_schema": component_audit_schema(analysis, program_version=program_version),
        }
    )


def audit_composition(
    analysis: SemanticAnalysisV3,
    generator: JSONGenerator,
    requested_model: str,
    *,
    program_version: ComponentAuditProgramVersion = "component-audit/v4.0",
) -> SemanticVerifierReportV4:
    analysis = SemanticAnalysisV3.model_validate(analysis.model_dump())
    schema = component_audit_schema(analysis, program_version=program_version)
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
            schema,
        )
    )
    return SemanticVerifierReportV4(
        analysis=analysis,
        proposal=proposal,
        requested_model=requested_model,
        program_sha256=verification_v4_program_digest(),
    )
