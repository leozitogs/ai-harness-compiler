"""The initial IR describes a development harness, not an executable agent runtime."""

from typing import Literal, Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier, Text
from ai_harness_compiler.models.capability import CapabilityGraph
from ai_harness_compiler.models.project import ProjectDNA


class ContextPolicy(Contract):
    strategy: Literal["on-demand"] = "on-demand"
    token_budget: int = Field(default=8000, gt=0)
    external_content: Literal["untrusted-data"] = "untrusted-data"


class PermissionPolicy(Contract):
    external_writes: Literal["require-approval"] = "require-approval"
    execute_generated_code: Literal[False] = False
    network_during_compilation: Literal[False] = False


class EvalCase(Contract):
    id: Identifier
    capability_id: Identifier
    criterion: Text
    method: Literal["manual-review"] = "manual-review"
    status: Literal["not-run"] = "not-run"


class ArchitectureDecision(Contract):
    id: Identifier
    decision: Text
    rationale: Text
    evidence_ids: list[Identifier] = Field(min_length=1)
    capability_ids: list[Identifier] = Field(default_factory=list)


class HarnessSpec(Contract):
    schema_version: Literal["HarnessSpec/v2"] = "HarnessSpec/v2"
    profile: Literal["development-baseline"] = "development-baseline"
    project_dna: ProjectDNA
    capability_graph: CapabilityGraph
    context: ContextPolicy = Field(default_factory=ContextPolicy)
    permissions: PermissionPolicy = Field(default_factory=PermissionPolicy)
    decisions: list[ArchitectureDecision] = Field(min_length=1)
    evals: list[EvalCase] = Field(min_length=1)
    runtime_status: Literal["not-implemented"] = "not-implemented"

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        project = self.project_dna.project
        if self.capability_graph.project_id != project.id:
            raise ValueError("Capability graph belongs to a different project")
        nodes = {node.id: node for node in self.capability_graph.capabilities}
        if set(nodes) != {item.id for item in project.backlog}:
            raise ValueError("Capabilities must cover the project backlog exactly in v1")
        for item in project.backlog:
            if nodes[item.id].model_dump(exclude={"evidence_ids"}) != item.model_dump():
                raise ValueError(f"Capability {item.id} differs from its source backlog item")
        evidence = [item.id for item in self.project_dna.evidence]
        if len(evidence) != len(set(evidence)):
            raise ValueError("Evidence IDs must be unique")
        references = list(self.project_dna.domain.evidence_ids)
        for node in nodes.values():
            references.extend(node.evidence_ids)
        for decision in self.decisions:
            references.extend(decision.evidence_ids)
        if set(references) - set(evidence):
            raise ValueError("Unresolved evidence references")
        entries = {item.id: item for item in self.project_dna.evidence}
        sources = {item.id: item for item in self.project_dna.sources}
        for reference in references:
            if sources[entries[reference].source_id].verification_status == "rejected":
                raise ValueError("Rejected source cannot support an active reference")
        for node in nodes.values():
            if len(node.evidence_ids) != len(set(node.evidence_ids)):
                raise ValueError("Duplicate capability evidence references")
            for reference in node.evidence_ids:
                entry = entries[reference]
                if entry.scope != "capability" or entry.capability_id != node.id:
                    raise ValueError("Evidence is incompatible with capability scope")
        for decision in self.decisions:
            if len(decision.evidence_ids) != len(set(decision.evidence_ids)):
                raise ValueError("Duplicate decision evidence references")
            if len(decision.capability_ids) != len(set(decision.capability_ids)):
                raise ValueError("Duplicate decision capability references")
            if set(decision.capability_ids) - set(nodes):
                raise ValueError("Unknown decision capability")
            for reference in decision.evidence_ids:
                entry = entries[reference]
                if (
                    entry.scope == "capability"
                    and entry.capability_id not in decision.capability_ids
                ):
                    raise ValueError("Evidence is incompatible with decision scope")
        for registry in (self.evals, self.decisions):
            ids = [item.id for item in registry]
            if len(ids) != len(set(ids)):
                raise ValueError("Registry IDs must be unique")
        covered: set[tuple[str, str]] = set()
        for case in self.evals:
            if case.capability_id not in nodes:
                raise ValueError(f"Unknown eval capability: {case.capability_id}")
            if case.criterion not in nodes[case.capability_id].acceptance_criteria:
                raise ValueError("Eval criterion must originate in the backlog")
            covered.add((case.capability_id, case.criterion))
        required = {
            (node.id, criterion)
            for node in nodes.values()
            for criterion in node.acceptance_criteria
        }
        if covered != required:
            raise ValueError("Every acceptance criterion requires an evaluation case")
        return self
