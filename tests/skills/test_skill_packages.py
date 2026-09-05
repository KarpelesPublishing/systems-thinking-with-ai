import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_skill_packages_pass_static_validation() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/validate_skills.py"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stdout + result.stderr
