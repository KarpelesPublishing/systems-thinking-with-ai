"""Every figure generator runs, self-checks its pinned numbers, and writes both outputs."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "build/figures"
SCRIPTS = sorted(FIGDIR.glob("fig_*.py"))

pytest.importorskip("matplotlib")


def slug_of(script: Path) -> str:
    return "fig-" + script.stem.removeprefix("fig_").replace("_", "-")


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_generator_runs_and_self_checks(script):
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_both_outputs_exist_at_print_width(script):
    from PIL import Image

    slug = slug_of(script)
    png = FIGDIR / "png" / f"{slug}.png"
    pdf = FIGDIR / "print" / f"{slug}.pdf"
    assert png.exists() and pdf.exists()
    with Image.open(png) as im:
        assert 900 <= im.width <= 1700, im.width


def test_generators_document_their_chapter_and_avoid_dashes():
    for script in SCRIPTS:
        text = script.read_text(encoding="utf-8")
        doc = text.split('"""')[1]
        assert "Chapter" in doc or "back matter" in doc.lower(), script.name
        assert "—" not in text and "–" not in text, script.name
