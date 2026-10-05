from pathlib import Path

import pytest

from ai_harness_compiler.intake import load_project
from ai_harness_compiler.models import ProjectInput


@pytest.fixture
def project() -> ProjectInput:
    root = Path(__file__).resolve().parents[1]
    return load_project(root / "examples/project-definition")
