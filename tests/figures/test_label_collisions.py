"""No figure prints one label on top of another.

The build gates cannot see this. A caption can be checked against the chapter and a
plotted number against the pack, but a polarity sign set on top of a flow name still
renders, still passes epubcheck, and still reaches the reader as a smudge. Two such
collisions were found by this check after the defect loop had converged.

Each generator is run with figstyle.save intercepted, so the figure is measured on the
real renderer just before it is written. Overlap is reported when the shared area is
more than a small fraction of the smaller label, which lets adjacent text touch at the
edges without failing.
"""
import pathlib
import runpy
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
FIGDIR = ROOT / "build/figures"
SCRIPTS = sorted(FIGDIR.glob("fig_*.py"))

pytest.importorskip("matplotlib")

# Two annotation blocks whose bounding boxes overlap while their text lines interleave
# cleanly. Checked by eye at 288 dpi on 2026-09-03.
ALLOWED = {("fig-limits-to-growth-curve", "2 percent of capacity", "10 percent of capacity")}

OVERLAP_LIMIT = 0.12


def _labels(fig):
    renderer = fig.canvas.get_renderer()
    out = []
    for ax in fig.get_axes():
        texts = list(ax.texts)
        texts += [t for t in ax.get_xticklabels() + ax.get_yticklabels() if t.get_text()]
        if ax.get_legend():
            texts += ax.get_legend().get_texts()
        for t in texts:
            if t.get_text().strip() and t.get_visible():
                try:
                    out.append((t.get_text().strip(), t.get_window_extent(renderer=renderer)))
                except Exception:
                    continue
    return out


def _shared(a, b):
    dx = min(a.x1, b.x1) - max(a.x0, b.x0)
    dy = min(a.y1, b.y1) - max(a.y0, b.y0)
    return dx * dy if dx > 0 and dy > 0 else 0.0


def _allowed(slug, one, two):
    for entry_slug, first, second in ALLOWED:
        if entry_slug == slug and first in (one + two) and second in (one + two):
            return True
    return False


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda p: p.stem)
def test_no_label_sits_on_another(script, monkeypatch):
    sys.path.insert(0, str(FIGDIR))
    sys.path.insert(0, str(ROOT))
    import matplotlib

    matplotlib.use("Agg")
    import figstyle

    collisions = []
    original = figstyle.save

    def measured_save(fig, slug):
        fig.canvas.draw()
        boxes = _labels(fig)
        for i in range(len(boxes)):
            for j in range(i + 1, len(boxes)):
                (one, box_one), (two, box_two) = boxes[i], boxes[j]
                shared = _shared(box_one, box_two)
                if shared <= 0:
                    continue
                smaller = min(
                    (box_one.x1 - box_one.x0) * (box_one.y1 - box_one.y0),
                    (box_two.x1 - box_two.x0) * (box_two.y1 - box_two.y0),
                )
                fraction = shared / smaller if smaller else 0.0
                name = slug if slug.startswith("fig-") else f"fig-{slug}"
                if fraction > OVERLAP_LIMIT and not _allowed(name, one, two):
                    collisions.append(f"{name}: {one!r} over {two!r} ({fraction:.0%})")
        return original(fig, slug)

    monkeypatch.setattr(figstyle, "save", measured_save)
    try:
        runpy.run_path(str(script), run_name="__main__")
    except SystemExit:
        pass
    assert not collisions, "\n".join(collisions)
