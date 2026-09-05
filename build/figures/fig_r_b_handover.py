#!/usr/bin/env python3
"""Chapter 8, "Loops that compete": the service growth trap's R and B loops on one variable.

The chapter describes a reinforcing loop where satisfied customers bring more customers and a
balancing loop where more customers strain capacity, erode quality, and drive customers away,
sharing the customers variable, with dominance shifting from R to B as load approaches capacity.
This figure draws the two loops around that shared variable:

    uv run --group figures python build/figures/fig_r_b_handover.py

Structure: a Link list written for this figure from the chapter's paragraph and audited with
chapters.chapter_08_causal_graph.code.graph. The chapter prints no audit counts for this diagram,
so the asserts pin what the drawing claims: two loops, one reinforcing and one balancing, both
through "customers". Evidence levels are "inferred" as the chapter's account is narrative.
Placement is layout; the variables and polarities follow the chapter's sentences.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import delay_mark, link, loop_id, text_node  # noqa: E402

from chapters.chapter_08_causal_graph.code.graph import (  # noqa: E402
    Link,
    audit,
    find_loops,
    loop_polarity,
)

LINKS = [
    Link("customers", "word of mouth", 1, "inferred", delayed=False),
    Link("word of mouth", "customers", 1, "inferred", delayed=True),
    Link("customers", "load on capacity", 1, "inferred", delayed=False),
    Link("load on capacity", "quality", -1, "inferred", delayed=True),
    Link("quality", "customers", 1, "inferred", delayed=True),
]


def causal(ax, a, b, sign, curve=0.0, delay=False, shrinkA=14, shrinkB=14, sign_gap=0.22,
           fontsize=7.8):
    """Causal arrow with the polarity and any delay mark set on the arc matplotlib draws."""
    link(ax, a, b, polarity="", curve=curve, shrinkA=shrinkA, shrinkB=shrinkB)
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    cx, cy = (x1 + x2) / 2 + curve * dy, (y1 + y2) / 2 - curve * dx
    if delay:
        mx, my = (x1 + x2) / 2 + curve * dy / 2, (y1 + y2) / 2 - curve * dx / 2
        delay_mark(ax, (mx, my), math.degrees(math.atan2(dy, dx)))
    t = 0.80
    px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
    py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
    side = 1.0 if curve >= 0 else -1.0
    ax.text(px + side * dy / n * sign_gap, py - side * dx / n * sign_gap, sign, ha="center",
            va="center", fontsize=fontsize, zorder=6)


def main():
    summary = audit(LINKS)
    assert summary["loops"] == 2 and summary["reinforcing"] == 1 and summary["balancing"] == 1
    loops = find_loops(LINKS)
    assert all("customers" in loop for loop in loops), loops
    kinds = {loop_polarity(loop, LINKS): loop for loop in loops}
    assert "word of mouth" in kinds["reinforcing"] and "quality" in kinds["balancing"]

    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.3, 8.7)
    ax.set_ylim(-0.55, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")

    pos = {"customers": (3.7, 1.2), "word of mouth": (1.0, 1.2),
           "load on capacity": (6.6, 2.3), "quality": (6.6, 0.1)}
    for name, (x, y) in pos.items():
        text_node(ax, x, y, name)
    curves = {("customers", "word of mouth"): 0.5, ("word of mouth", "customers"): 0.5,
              ("customers", "load on capacity"): -0.3, ("load on capacity", "quality"): -0.35,
              ("quality", "customers"): -0.3}
    shrinks = {("customers", "load on capacity"): (22, 34),
               ("load on capacity", "quality"): (10, 10),
               ("quality", "customers"): (18, 22)}
    for item in LINKS:
        key = (item.source, item.target)
        sa, sb = shrinks.get(key, (22, 22))
        causal(ax, pos[item.source], pos[item.target], "+" if item.polarity > 0 else "-",
               curve=curves[key], delay=bool(item.delayed), shrinkA=sa, shrinkB=sb)
    loop_id(ax, 2.35, 1.2, "R", direction="cw", r=0.24)
    loop_id(ax, 5.55, 1.2, "B", direction="cw", r=0.24)
    ax.text(2.35, 2.6, "R dominates while capacity is ample", ha="center", va="center",
            fontsize=6.4, style="italic")
    ax.text(4.6, -0.35, "B strengthens as load approaches capacity", ha="center", va="center",
            fontsize=6.4, style="italic")

    fig.tight_layout()
    save(fig, "r-b-handover")


if __name__ == "__main__":
    main()
