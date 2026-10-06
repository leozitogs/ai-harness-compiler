"""Pure baseline transformations. No LLM, I/O, agent execution, or domain inference."""

from ai_harness_compiler.models import CapabilityGraph, HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.capability import Capability
from ai_harness_compiler.models.domain import DomainProfile
from ai_harness_compiler.models.evidence import Evidence, SourceRecord, canonical_project_digest
from ai_harness_compiler.models.harness import ArchitectureDecision, EvalCase


def understand(project: ProjectInput) -> ProjectDNA:
    project = ProjectInput.model_validate(project.model_dump())
    sources = [
        SourceRecord(
            id="project-manifest",
            location="project.yaml",
            origin="user-declaration",
            sha256=canonical_project_digest(project.model_dump()),
        )
    ]
    evidence = [
        Evidence(
            id="project-intent",
            source_id="project-manifest",
            source="project.yaml#/conception",
            claim=project.conception,
            kind="declared",
            scope="project",
        )
    ]
    unknowns = [
        "Architecture has not been researched or benchmarked.",
        "Product acceptance criteria have not been executed.",
    ]
    domain = DomainProfile(status="DOMAIN_UNCERTAIN", origin="unknown")
    if project.domain:
        evidence.append(
            Evidence(
                id="domain-declaration",
                source_id="project-manifest",
                source="project.yaml#/domain",
                claim=project.domain,
                kind="declared",
                scope="domain",
            )
        )
        domain = DomainProfile(
            primary=project.domain,
            status="declared",
            origin="user-declaration",
            evidence_ids=["domain-declaration"],
        )
    else:
        unknowns.append("DOMAIN_UNCERTAIN: no domain was declared; inference is not implemented.")
    if project.domain_profile:
        domain = project.domain_profile.model_copy(deep=True)
        evidence.append(
            Evidence(
                id="domain-profile",
                source_id="project-manifest",
                source="project.yaml#/domain_profile",
                claim=domain.model_dump_json(),
                kind="declared",
                scope="domain",
            )
        )
        unknowns = [item for item in unknowns if not item.startswith("DOMAIN_UNCERTAIN:")]
        if domain.status == "DOMAIN_UNCERTAIN":
            unknowns.append("DOMAIN_UNCERTAIN: supplied profile does not select a primary domain.")
        if domain.status == "hypothesis" or domain.hypotheses:
            unknowns.append(
                "Domain hypotheses were supplied and have not been independently evaluated."
            )
    for index, item in enumerate(project.backlog):
        evidence.append(
            Evidence(
                id=f"backlog-{index + 1}",
                source_id="project-manifest",
                source=f"project.yaml#/backlog/{index}",
                claim=item.description,
                kind="declared",
                scope="capability",
                capability_id=item.id,
            )
        )
        if item.implementation == "undecided":
            unknowns.append(f"{item.id}: implementation strategy requires evaluation.")
        if item.risk == "unknown":
            unknowns.append(f"{item.id}: risk classification requires review.")
    if project.evidence_pack:
        sources.extend(project.evidence_pack.sources)
        evidence.extend(project.evidence_pack.evidence)
    return ProjectDNA(
        project=project, domain=domain, sources=sources, evidence=evidence, unknowns=unknowns
    )


def build_graph(dna: ProjectDNA) -> CapabilityGraph:
    dna = ProjectDNA.model_validate(dna.model_dump())
    sources = {source.id: source for source in dna.sources}
    return CapabilityGraph(
        project_id=dna.project.id,
        capabilities=[
            Capability(
                **item.model_dump(),
                evidence_ids=[
                    entry.id
                    for entry in dna.evidence
                    if entry.scope == "capability"
                    and entry.capability_id == item.id
                    and sources[entry.source_id].verification_status != "rejected"
                ],
            )
            for item in dna.project.backlog
        ],
    )


def design_baseline(dna: ProjectDNA, graph: CapabilityGraph) -> HarnessSpec:
    cases = [
        EvalCase(id=f"eval-{index + 1}-{number + 1}", capability_id=node.id, criterion=criterion)
        for index, node in enumerate(graph.capabilities)
        for number, criterion in enumerate(node.acceptance_criteria)
    ]
    return HarnessSpec(
        project_dna=dna,
        capability_graph=graph,
        decisions=[
            ArchitectureDecision(
                id="adr-001",
                decision="Begin with a reviewable development harness and no agent runtime.",
                rationale=(
                    "Project intent and backlog are available; architecture search and runtime "
                    "evaluation are not implemented. Preserve requested AI strategies as "
                    "declarations until evidence supports an executable architecture."
                ),
                evidence_ids=["project-intent"],
            )
        ],
        evals=cases,
    )


def plan(project: ProjectInput) -> HarnessSpec:
    dna = understand(project)
    return design_baseline(dna, build_graph(dna))
