#!/usr/bin/env python3
"""Chapter 38, "Capacity Arrives When the Price Has Gone": the stock, the two delays, the loop.

The chapter's document has one stock, capacity, filled by completions and drained by retirement.
Utilization is production over capacity; a saturating lookup turns it into a margin; an
information delay turns the margin into a perceived margin; desired investment responds to the
perceived margin; a construction delay turns desired investment into completions. Demand is a
constant outside the loop. This figure draws that structure with the book's vocabulary; the two
double bars are the two delays the chapter fits around:

    uv run --group figures python build/figures/fig_capacity_structure.py

No numeric data. Placement is a layout choice; the elements are the document's variable ids.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, cloud, delay_mark, flow, link, loop_id, stock  # noqa: E402

from chapters.chapter_38_capacity_cycle.code.model import document  # noqa: E402

# The docstring claims these are the document's own variable ids, so the claim is checked.
DRAWN = ["capacity", "completions", "retirement", "utilization", "margin", "demand"]


def main():
    ids = {v.id for v in document().variables}
    missing = [name for name in DRAWN if name not in ids]
    assert not missing, f"figure names variables the document does not have: {missing}"

    fig, ax = figure(height_in=2.45)
    ax.set_xlim(-0.3, 9.3)
    ax.set_ylim(-3.0, 0.75)
    ax.set_aspect("equal")
    ax.axis("off")

    # material chain: source, completions, capacity, retirement, sink
    cloud(ax, 0.45, 0.0)
    stock(ax, 4.5, 0.0, "capacity", w=2.0, h=0.75, sublabel="units of output")
    cloud(ax, 8.55, 0.0)
    flow(ax, (0.8, 0.0), (3.5, 0.0), label="completions", label_side="above")
    delay_mark(ax, (1.5, 0.0), 0.0)
    flow(ax, (5.5, 0.0), (8.2, 0.0), label="retirement", label_side="above")
    ax.text(2.15, -0.42, "construction delay", ha="center", va="center", fontsize=6.0,
            style="italic")
    ax.text(6.85, -0.42, "capacity / lifetime", ha="center", va="center", fontsize=6.0,
            style="italic")

    # information side, below the stock
    invest = auxiliary(ax, 1.05, -1.65, "desired\ninvestment", r=0.52, fontsize=6.0)
    perceived = auxiliary(ax, 2.85, -2.45, "perceived\nmargin", r=0.46, fontsize=6.0)
    margin = auxiliary(ax, 4.85, -2.45, "margin", r=0.34, fontsize=6.0)
    util = auxiliary(ax, 6.6, -1.65, "utilization", r=0.46, fontsize=6.0)
    demand = auxiliary(ax, 8.55, -1.65, "demand", r=0.38, fontsize=6.0, dashed=True)

    link(ax, (4.5, -0.38), util, polarity="", curve=-0.2, shrinkA=4.0, shrinkB=14.0)
    link(ax, demand, util, polarity="", curve=0.0, shrinkA=11.5, shrinkB=14.0)
    link(ax, util, margin, polarity="", curve=0.15, shrinkA=14.0, shrinkB=10.5)
    link(ax, margin, perceived, polarity="", curve=0.0, shrinkA=10.5, shrinkB=14.0, delay=True)
    link(ax, perceived, invest, polarity="", curve=0.15, shrinkA=14.0, shrinkB=16.0)
    link(ax, invest, (1.5, -0.1), polarity="", curve=0.15, shrinkA=16.0, shrinkB=4.0)
    # polarities, placed by hand beside each arrow head
    for x, y, sign in ((5.95, -1.15, "-"), (7.95, -1.45, "+"), (5.45, -2.05, "+"),
                       (3.55, -2.25, "+"), (1.75, -1.95, "+"), (1.05, -0.55, "+")):
        ax.text(x, y, sign, ha="center", va="center", fontsize=8.0)
    ax.text(5.75, -2.75, "lookup", ha="center", va="center", fontsize=6.0, style="italic")
    ax.text(3.85, -2.85, "perception delay", ha="center", va="center", fontsize=6.0,
            style="italic")
    loop_id(ax, 3.85, -1.45, "B", direction="ccw", r=0.26)
    ax.text(3.85, -0.95, "capacity chases the margin", ha="center", va="center", fontsize=6.0,
            style="italic")

    fig.tight_layout()
    save(fig, "capacity-structure")


if __name__ == "__main__":
    main()
