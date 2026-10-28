"""Explicit hash selection of trusted generation programs, without response rewriting."""

from ai_harness_compiler.models.evidence import canonical_project_digest
from ai_harness_compiler.models.grounding import GroundingExtraction
from ai_harness_compiler.models.semantic_analysis_v4 import AnalysisProposalV4, SemanticAnalysisV4
from ai_harness_compiler.models.semantic_program import SemanticProgramVersion
from ai_harness_compiler.semantic_generation_v4 import (
    GENERATION_PROMPT_V4,
    generation_program_v4,
    generation_prompt_v4,
    generation_schema_v4,
)
from ai_harness_compiler.semantic_verification import JSONGenerator

RELATIONAL_GUIDANCE_V41 = """
RELATIONAL CLASSIFICATION AND QUESTION MATERIALITY:
Distinguish an unconditional normative obligation from a relation governing an action.
An explicit necessary precondition, actor permission, exclusive visibility restriction,
or temporal ordering belongs in project_analysis.criteria as kind=business-rule, with separately
source-bound condition/outcome components. Literal text copied into a requirement alone
does not represent that relation. The ban on invented triggers does not erase a relation
already stated. Restate only the action/actor/restriction present in its source; never
invent an event, deadline, exception, role equivalence, extra approver or sufficiency.
A necessary condition restricts an action; satisfying it does not by itself grant the
action. A permission must preserve the stated actor and exclusions without adding a gate.
An exclusive visibility rule must not grant access to other members of the audience.
An unconditional obligation without such a relation remains a requirement with required
or prohibited force and no invented applicability. Do not force all norms into rules,
or use a duplicate requirement as a substitute for the criterion's relational structure.
At intent-analysis time a role can remain symbolic. Identifying which person fills it
is an implementation detail unless the sources establish a material dependency or
incompatible role allocation that changes a declared authorization, outcome or rule.
Do not block intent merely because the role holder is unnamed or two roles might overlap.
Preserve genuine conflicts and missing outcome definitions as material uncertainties.
Questions may seek implementation details with impact=implementation-detail; do not
label them rule/authorization/outcome merely because their topic mentions a business norm.
These distinctions guide analysis only: no executable authorization or human approval.
"""

PRECEDENCE_GUIDANCE_V42 = """
ACTIONABLE CONFLICT UNCERTAINTY:
Preserve every genuine unresolved conflict with all incompatible source sides.
Recognizing a conflict and marking the project blocked does not ask the human what
decision is needed. For each such conflict, also emit an explicit question in the
project_analysis.issues channel with kind=question and impact=precedence, citing all
the conflicting context_indices. Ask which stated rule takes precedence, or how the
incompatible declarations should be reconciled. Preserve both sides without selecting
a winner or inventing a resolution, new approval gate, deadline or exception.
The conflict statement is not a substitute for that question; a generic request for
more detail or a question citing only one side is not enough. Compatible rules,
symbolic role holders and unconditional identity obligations do not by themselves
constitute a conflict. Do not add a precedence question or block an otherwise clear
project merely because the input contains several different norms or roles.
This is an analysis requirement, not an executable permission or automatic approval.
"""


def _instructions(version: SemanticProgramVersion) -> str:
    if version == "semantic-composition/v4.1":
        return GENERATION_PROMPT_V4 + RELATIONAL_GUIDANCE_V41
    if version == "semantic-composition/v4.2":
        return GENERATION_PROMPT_V4 + RELATIONAL_GUIDANCE_V41 + PRECEDENCE_GUIDANCE_V42
    raise ValueError("Unknown generation program")


def program_digest(extraction: GroundingExtraction, version: SemanticProgramVersion) -> str:
    if version == "semantic-composition/v4.0":
        return generation_program_v4(extraction)
    return canonical_project_digest(
        dict(
            version=version,
            prompt=_instructions(version),
            schema=generation_schema_v4(extraction),
        )
    )


def resolve_program(extraction: GroundingExtraction, digest: str) -> SemanticProgramVersion:
    versions: tuple[SemanticProgramVersion, ...] = (
        "semantic-composition/v4.0",
        "semantic-composition/v4.1",
        "semantic-composition/v4.2",
    )
    for version in versions:
        if program_digest(extraction, version) == digest:
            return version
    raise ValueError("Generation program digest is not registered for the input schema")


def program_prompt(extraction: GroundingExtraction, digest: str) -> str:
    version = resolve_program(extraction, digest)
    legacy = generation_prompt_v4(extraction)
    if version == "semantic-composition/v4.0":
        return legacy
    # Same instruction base and exact source packet; no expectations or extra examples.
    return _instructions(version) + legacy.removeprefix(GENERATION_PROMPT_V4)


def analyze_program(
    extraction: GroundingExtraction,
    generator: JSONGenerator,
    digest: str,
) -> SemanticAnalysisV4:
    extraction = GroundingExtraction.model_validate(extraction.model_dump())
    raw = generator.generate_json(
        program_prompt(extraction, digest), generation_schema_v4(extraction)
    )
    proposal = AnalysisProposalV4.model_validate_json(raw)
    if any(c.uncertainties for c in proposal.project_analysis.criteria):
        raise ValueError("V4 secondary questions must use the multi-source issues channel")
    return SemanticAnalysisV4(extraction=extraction, proposal=proposal)
