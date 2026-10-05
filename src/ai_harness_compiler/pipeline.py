"""Pure baseline transformations. No LLM, I/O, agent execution, or domain inference."""

from ai_harness_compiler.models import CapabilityGraph, HarnessSpec, ProjectDNA, ProjectInput
from ai_harness_compiler.models.capability import Capability
from ai_harness_compiler.models.harness import ArchitectureDecision, EvalCase
from ai_harness_compiler.models.project import DomainProfile, Evidence


def understand(project: ProjectInput) -> ProjectDNA:
    evidence = [
        Evidence(
            id="project-intent",
            source="project.yaml#/conception",
            claim=project.conception,
            kind="declared",
        )
    ]
    unknowns = [
        "Architecture has not been researched or benchmarked.",
        "Product acceptance criteria have not been executed.",
    ]
    domain = DomainProfile(status="DOMAIN_UNCERTAIN")
    if project.domain:
        evidence.append(
            Evidence(
                id="domain-declaration",
                source="project.yaml#/domain",
                claim=project.domain,
                kind="declared",
            )
        )
        domain = DomainProfile(
            primary=project.domain, status="declared", evidence_ids=["domain-declaration"]
        )
    else:
        unknowns.append("DOMAIN_UNCERTAIN: no domain was declared; inference is not implemented.")
    for index, item in enumerate(project.backlog):
        evidence.append(
            Evidence(
                id=f"backlog-{index + 1}",
                source=f"project.yaml#/backlog/{index}",
                claim=item.description,
                kind="declared",
            )
        )
        if item.implementation == "undecided":
            unknowns.append(f"{item.id}: implementation strategy requires evaluation.")
        if item.risk == "unknown":
            unknowns.append(f"{item.id}: risk classification requires review.")
    return ProjectDNA(project=project, domain=domain, evidence=evidence, unknowns=unknowns)


def build_graph(dna: ProjectDNA) -> CapabilityGraph:
    return CapabilityGraph(
        project_id=dna.project.id,
        capabilities=[
            Capability(**item.model_dump(), evidence_ids=[f"backlog-{index + 1}"])
            for index, item in enumerate(dna.project.backlog)
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
