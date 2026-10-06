"""Load one structured manifest; assets remain references and are never executed."""

import sys
from collections.abc import Hashable
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError
from yaml.events import AliasEvent
from yaml.nodes import MappingNode, Node, ScalarNode

from ai_harness_compiler.models import ProjectInput

DEFAULT_MAX_MANIFEST_BYTES = 1024 * 1024
MAX_YAML_DEPTH = 64
MAX_YAML_NODES = 50_000


class IntakeError(ValueError):
    """Stable public diagnostic without input values or filesystem details."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        super().__init__(f"{code}: {message}")


class ManifestLoader(yaml.SafeLoader):
    """Bound composition before construction; never expand aliases or merge keys."""

    def __init__(self, stream: str) -> None:
        super().__init__(stream)
        self.depth = 0
        self.node_count = 0

    def compose_node(self, parent: Any, index: Any) -> Node | None:
        if self.check_event(AliasEvent):
            raise IntakeError("INTAKE_YAML_ALIAS", "YAML aliases are not supported.")
        if self.depth >= MAX_YAML_DEPTH:
            raise IntakeError("INTAKE_YAML_DEPTH", "YAML nesting exceeds 64 levels.")
        self.node_count += 1
        if self.node_count > MAX_YAML_NODES:
            raise IntakeError("INTAKE_YAML_NODES", "YAML exceeds 50000 nodes.")
        self.depth += 1
        try:
            return super().compose_node(parent, index)
        finally:
            self.depth -= 1

    def construct_mapping(self, node: Node, deep: bool = False) -> dict[Hashable, Any]:
        if not isinstance(node, MappingNode):
            raise IntakeError("INTAKE_YAML_MAPPING", "Expected a YAML mapping.")
        keys: set[str] = set()
        for key_node, _ in node.value:
            if key_node.tag == "tag:yaml.org,2002:merge":
                raise IntakeError("INTAKE_YAML_MERGE", "YAML merge keys are not supported.")
            if not isinstance(key_node, ScalarNode) or key_node.tag != "tag:yaml.org,2002:str":
                raise IntakeError("INTAKE_YAML_KEY", "Mapping keys must be strings.")
            if key_node.value in keys:
                raise IntakeError("INTAKE_DUPLICATE_KEY", "Duplicate YAML mapping key.")
            keys.add(key_node.value)
        return super().construct_mapping(node, deep=deep)


def load_project(
    path: Path, *, max_manifest_bytes: int = DEFAULT_MAX_MANIFEST_BYTES
) -> ProjectInput:
    if (
        not isinstance(max_manifest_bytes, int)
        or isinstance(max_manifest_bytes, bool)
        or max_manifest_bytes <= 0
        or max_manifest_bytes >= sys.maxsize
    ):
        raise IntakeError(
            "INTAKE_LIMIT", "Manifest byte limit must be a positive readable integer."
        )
    manifest = path / "project.yaml" if path.is_dir() else path
    try:
        with manifest.open("rb") as stream:
            content = stream.read(max_manifest_bytes + 1)
    except OSError as exc:
        raise IntakeError("INTAKE_READ", "Unable to read project manifest.") from exc
    if len(content) > max_manifest_bytes:
        raise IntakeError("INTAKE_TOO_LARGE", "Manifest exceeds configured byte limit.")
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise IntakeError("INTAKE_ENCODING", "Manifest must use UTF-8.") from exc
    loader: ManifestLoader | None = None
    try:
        loader = ManifestLoader(text)
        payload = loader.get_single_data()
    except IntakeError:
        raise
    except (yaml.YAMLError, ValueError, OverflowError) as exc:
        raise IntakeError("INTAKE_YAML", "Invalid or unsupported YAML document.") from exc
    finally:
        if loader is not None:
            loader.dispose()
    if not isinstance(payload, dict):
        raise IntakeError("INTAKE_SHAPE", "Manifest must be a mapping.")
    if payload.get("schema_version", "ProjectInput/v1") != "ProjectInput/v1":
        raise IntakeError("INTAKE_SCHEMA_VERSION", "Unsupported ProjectInput schema version.")
    try:
        return ProjectInput.model_validate(payload)
    except ValidationError as exc:
        raise IntakeError("INTAKE_CONTRACT", "Manifest does not satisfy ProjectInput/v1.") from exc
