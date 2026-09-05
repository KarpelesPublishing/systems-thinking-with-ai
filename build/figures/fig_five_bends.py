#!/usr/bin/env python3
"""Chapter 15, "Five bends worth knowing": saturation, threshold, congestion, diminishing
returns, and network effects, each held as a Lookup from the chapter pack.

The chapter names the five shapes in prose and gives observed points only for saturation (the six
points used in "Two ways to hold a bend"). The other four point tables here are illustrative
placements chosen to show the shape the chapter describes, not measurements; each is held in the
pack's Lookup so the curve is what the pack would interpolate. The asserts pin each curve's
endpoints as the Lookup returns them, and the shape property the chapter attaches to it.

    uv run --group figures python build/figures/fig_five_bends.py

Data: chapters.chapter_15_lookups.code.lookup.Lookup(points)(x) over each table's domain. The
saturation points are the chapter's; the layout and the other four tables are this figure's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import grid_figure, save  # noqa: E402

from chapters.chapter_15_lookups.code.lookup import Lookup  # noqa: E402

SHAPES = [
    ("saturation", [(0, 0), (1, 0.35), (2, 0.6), (3, 0.78), (4, 0.88), (5, 0.93)]),
    ("threshold", [(0, 0.05), (1, 0.06), (2, 0.08), (3, 0.12), (3.6, 0.35), (4, 0.75),
                   (4.5, 0.95), (5, 1.0)]),
    ("congestion", [(0, 0), (1, 0.45), (2, 0.75), (2.6, 0.85), (3.2, 0.78), (4, 0.5),
                    (5, 0.15)]),
    ("diminishing returns", [(0, 0), (1, 0.4), (2, 0.6), (3, 0.73), (4, 0.83), (5, 0.9)]),
    ("network effects", [(0, 0.02), (1, 0.05), (2, 0.11), (3, 0.24), (4, 0.5), (5, 1.0)]),
]


def main():
    lookups = {name: Lookup(pts, name) for name, pts in SHAPES}
    assert lookups["saturation"](0) == 0 and lookups["saturation"](5) == 0.93
    assert lookups["saturation"].is_monotonic()
    assert lookups["threshold"](0) == 0.05 and lookups["threshold"](5) == 1.0
    assert not lookups["congestion"].is_monotonic()
    assert lookups["congestion"](0) == 0 and lookups["congestion"](5) == 0.15
    diminishing = lookups["diminishing returns"]
    assert diminishing(5) == 0.9 and diminishing.is_monotonic()
    assert lookups["network effects"](0) == 0.02 and lookups["network effects"](5) == 1.0
    for lk in lookups.values():
        assert lk.domain == (0, 5) and lk.is_bounded_by(0.0, 1.0)

    fig, axes = grid_figure(2, 3, height_in=2.7)
    flat = list(axes.flat)
    xs = [i / 40 for i in range(0, 201)]
    for ax, (name, _) in zip(flat, SHAPES, strict=False):
        lk = lookups[name]
        ax.plot(xs, [lk(x) for x in xs], color="black")
        ax.set_xlim(0, 5)
        ax.set_ylim(0, 1.08)
        ax.set_xticks([0, 5])
        ax.set_yticks([0, 1])
        ax.set_title(name, fontsize=7, pad=2)
    flat[-1].axis("off")
    flat[-1].text(0.0, 0.85, "input on the horizontal,\noutput on the vertical,\n"
                  "each held as a Lookup\nover the observed points", fontsize=6.2,
                  style="italic", va="top", ha="left", transform=flat[-1].transAxes)
    fig.tight_layout(pad=0.4)
    save(fig, "five-bends")


if __name__ == "__main__":
    main()
