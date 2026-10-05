"""Load one structured manifest; assets remain references and are never executed."""

from pathlib import Path

import yaml

from ai_harness_compiler.models import ProjectInput


def load_project(path: Path) -> ProjectInput:
    manifest = path / "project.yaml" if path.is_dir() else path
    payload = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    return ProjectInput.model_validate(payload)
