"""A dependency graph with explicit uncertainty and evaluation requirements."""

from graphlib import CycleError, TopologicalSorter
from typing import Self

from pydantic import Field, model_validator

from ai_harness_compiler.models.base import Contract, Identifier
from ai_harness_compiler.models.project import BacklogItem


class Capability(BacklogItem):
    evidence_ids: list[Identifier] = Field(min_length=1)


class CapabilityGraph(Contract):
    schema_version: str = Field(default="CapabilityGraph/v1", pattern=r"^CapabilityGraph/v1$")
    project_id: Identifier
    capabilities: list[Capability] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_dependencies(self) -> Self:
        ids = [node.id for node in self.capabilities]
        if len(ids) != len(set(ids)):
            raise ValueError("Capability IDs must be unique")
        for node in self.capabilities:
            if len(node.depends_on) != len(set(node.depends_on)):
                raise ValueError(f"Duplicate dependencies for {node.id}")
            unknown = set(node.depends_on) - set(ids)
            if unknown:
                raise ValueError(f"Unknown dependencies for {node.id}: {sorted(unknown)}")
        try:
            self.execution_order()
        except CycleError as exc:
            raise ValueError("Capability graph must be acyclic") from exc
        return self

    def execution_order(self) -> list[str]:
        graph = {node.id: node.depends_on for node in self.capabilities}
        return list(TopologicalSorter(graph).static_order())
