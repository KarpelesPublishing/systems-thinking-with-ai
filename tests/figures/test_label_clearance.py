"""Direct labels must stay legible where a plotted curve passes behind them."""
import importlib.util
from pathlib import Path

import pytest

pytest.importorskip("matplotlib")
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("filename,label", [
    ("fig_lookup_vs_formula.py", "degree-5 fit,\npast the data"),
    ("fig_scenario_spread.py", "aggressive, 0.60"),
])
def test_crossed_direct_labels_have_opaque_white_background(monkeypatch, filename, label):
    spec = importlib.util.spec_from_file_location("label_figure", ROOT / "build/figures" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    figures = []
    monkeypatch.setattr(module, "save", lambda fig, name: figures.append(fig))
    module.main()
    texts = [text for ax in figures[0].axes for text in ax.texts if text.get_text() == label]
    assert len(texts) == 1
    background = texts[0].get_bbox_patch()
    assert background is not None
    assert background.get_facecolor() == (1.0, 1.0, 1.0, 1.0)
