#!/usr/bin/env python3
"""Chapter 36, "Elective Backlogs as a Stock": the three-stock structure and its three loops.

The chapter's model has three stocks (the waiting list under 52 weeks, the long waiters over
52 weeks, and treatment capacity), an aging transfer with a delay between the first two, and
three loops: R1, long waiters erode effective capacity; B1, validation removals scale with the
list; B2, a large list suppresses referrals. This figure draws that structure with the book's
stock-and-flow vocabulary.

    uv run --group figures python build/figures/fig_rtt_structure.py

No numeric data. Placement is a layout choice; the stocks, flows, and loops are the chapter's,
and the variable names are the ids in chapters/chapter_36_elective_backlog/code/model.py.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, cloud, flow, link, loop_id, stock  # noqa: E402

from chapters.chapter_36_elective_backlog.code.model import build  # noqa: E402

# Every variable this figure names. The docstring claims these are the pack's own ids, so
# the claim is checked here: a rename in the model fails the figure instead of drifting
# quietly away from it.
DRAWN = [
    "waiting_list", "long_waiters", "capacity", "effective_capacity", "referrals",
    "aging_in", "long_treatments", "treatments", "validation_removals",
    "long_validation", "capacity_change",
]


def main():
    ids = {v.id for v in build().variables}
    missing = [name for name in DRAWN if name not in ids]
    assert not missing, f"figure names variables the model does not have: {missing}"
    stocks = {v.id for v in build().variables if v.kind == "stock"}
    assert stocks == {"waiting_list", "long_waiters", "capacity"}, stocks

    fig, ax = figure(height_in=3.2)
    ax.set_xlim(-0.2, 11.2)
    ax.set_ylim(-3.1, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")

    # main line: source, list, long waiters, sink
    cloud(ax, 0.4, 0.0)
    stock(ax, 3.2, 0.0, "waiting_list", w=2.0, h=0.75, sublabel="under 52 weeks")
    stock(ax, 7.9, 0.0, "long_waiters", w=2.0, h=0.75, sublabel="over 52 weeks")
    cloud(ax, 10.7, 0.0)
    flow(ax, (0.75, 0.0), (2.2, 0.0))
    ax.text(1.30, 0.34, "referrals", ha="center", va="bottom", fontsize=6.4)
    flow(ax, (4.2, 0.0), (6.9, 0.0), double=True)
    ax.text(5.55, 0.36, "aging_in, after a delay", ha="center", va="bottom", fontsize=6.4)
    flow(ax, (8.9, 0.0), (10.35, 0.0))
    ax.text(9.62, 0.36, "long_treatments", ha="center", va="bottom", fontsize=6.0)

    # outflows downward: treatments and validation from the list, validation from long waiters
    cloud(ax, 2.6, -2.5)
    cloud(ax, 3.9, -2.5)
    cloud(ax, 7.9, -2.5)
    flow(ax, (2.6, -0.38), (2.6, -2.15), valve=True)
    flow(ax, (3.9, -0.38), (3.9, -2.15), valve=True)
    flow(ax, (7.9, -0.38), (7.9, -2.15), valve=True)
    ax.text(2.45, -1.7, "treatments", ha="right", va="center", fontsize=6.0)
    ax.text(4.05, -1.7, "validation_removals", ha="left", va="center", fontsize=6.0)
    ax.text(8.05, -1.7, "long_validation", ha="left", va="center", fontsize=6.0)

    # capacity above, feeding effective capacity
    cloud(ax, 2.9, 1.9)
    stock(ax, 5.3, 1.9, "capacity", w=1.7, h=0.6)
    flow(ax, (3.25, 1.9), (4.45, 1.9))
    ax.text(3.85, 2.25, "capacity_change", ha="center", va="bottom", fontsize=6.0)
    auxiliary(ax, 8.6, 1.75, "effective\ncapacity", r=0.45, fontsize=5.8)
    link(ax, (6.15, 1.9), (8.15, 1.8), polarity="+", curve=0.0, shrinkA=2, shrinkB=2)

    # R1: long waiters lower effective capacity; effective capacity raises treatments
    link(ax, (8.4, 0.38), (8.5, 1.3), polarity="-", curve=0.0, shrinkA=2, shrinkB=2)
    link(ax, (8.15, 1.75), (2.75, -1.27), polarity="+", curve=0.32, shrinkA=6, shrinkB=6)
    loop_id(ax, 6.0, 1.05, "R1", direction="cw", r=0.24)

    # B1: the list drives its own validation removals
    link(ax, (4.2, -0.3), (4.0, -1.27), polarity="+", curve=-0.5, shrinkA=2, shrinkB=2)
    loop_id(ax, 4.95, -1.0, "B1", direction="ccw", r=0.24)

    # B2: the list suppresses referrals
    link(ax, (2.3, 0.3), (1.5, 0.15), polarity="-", curve=0.5, shrinkA=2, shrinkB=2)
    loop_id(ax, 1.55, 1.05, "B2", direction="ccw", r=0.24)

    ax.text(5.5, -3.0, "three stocks, seven flows, one delay, three loops", ha="center",
            va="center", fontsize=6.4, style="italic")

    fig.tight_layout()
    save(fig, "rtt-structure")


if __name__ == "__main__":
    main()
