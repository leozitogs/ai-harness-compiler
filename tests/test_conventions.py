import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_conventions.py"


@pytest.mark.parametrize(
    "flag,value,expected",
    [
        ("--message", "feat(planning): compile reviewable task graphs", 0),
        ("--message", "feat(ir)!: change contract", 0),
        ("--message", "updated stuff", 1),
        ("--message", "feat: ", 1),
        ("--message", "feat: " + "x" * 100, 1),
        ("--branch", "feat/ahc-001-canonical-intake", 0),
        ("--branch", "ci/infra-required-checks", 0),
        ("--branch", "dependabot/uv/pydantic-2.13.5", 0),
        ("--branch", "main", 0),
        ("--branch", "my-random-branch", 1),
    ],
)
def test_conventions(flag, value, expected):
    result = subprocess.run([sys.executable, str(SCRIPT), flag, value], capture_output=True)
    assert result.returncode == expected, result.stdout
