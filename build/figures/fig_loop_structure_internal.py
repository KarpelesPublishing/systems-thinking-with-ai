#!/usr/bin/env python3
"""Chapter 8, "Two structures for the same behavior": structure one, internal amplification.

The chapter describes structure one as a backlog that builds, production increased to clear it,
the increase arriving after the backlog has fallen, inventory overshooting, production cut, and
the cycle repeating, every link inside the operation. Its "A graph that audits itself" section
writes that structure as six links and prints the audit: six links, three loops, all balancing,
two unsupported, two without time semantics. This figure draws those six links as a causal loop
diagram with the pack's polarities and loop labels:

    uv run --group figures python build/figures/fig_loop_structure_internal.py

Structure: the chapter's Link list, passed through find_loops, loop_polarity, and audit from
chapters.chapter_08_causal_graph.code.graph. The asserts pin the printed audit. Delay marks sit
on the four links the chapter records as delayed; the two links with no recorded time semantics
are drawn dashed. Node placement and arc curvature are layout.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import delay_mark, legend_rows, link, loop_id, text_node  # noqa: E402

from chapters.chapter_08_causal_graph.code.graph import (  # noqa: E402
    Link,
    audit,
    find_loops,
    loop_polarity,
)

LINKS = [
    Link("backlog", "production", 1, "observed", delayed=True),
    Link("production", "backlog", -1, "observed", delayed=True),
    Link("production", "inventory", 1, "observed", delayed=True),
    Link("inventory", "production", -1, "inferred", delayed=True),
    Link("inventory", "shipments", 1, "assumed"),
    Link("shipments", "inventory", -1, "proposed"),
]


def causal(ax, a, b, sign, curve=0.0, delay=False, shrinkA=14, shrinkB=14, linestyle="solid",
           sign_gap=0.22, fontsize=7.8):
    """Causal arrow with the polarity and any delay mark set on the arc matplotlib draws."""
    link(ax, a, b, polarity="", curve=curve, shrinkA=shrinkA, shrinkB=shrinkB,
         linestyle=linestyle)
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
    assert summary == {"links": 6, "loops": 3, "reinforcing": 0, "balancing": 3,
                       "unsupported": 2, "no_time_semantics": 2}, summary
    loops = find_loops(LINKS)
    assert all(loop_polarity(loop, LINKS) == "balancing" for loop in loops)

    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.3, 8.7)
    ax.set_ylim(-0.6, 3.1)
    ax.set_aspect("equal")
    ax.axis("off")

    pos = {"backlog": (0.9, 1.4), "production": (3.4, 1.4), "inventory": (5.9, 1.4),
           "shipments": (8.1, 1.4)}
    for name, (x, y) in pos.items():
        text_node(ax, x, y, name)
    for item in LINKS:
        a, b = pos[item.source], pos[item.target]
        causal(ax, a, b, "+" if item.polarity > 0 else "-", curve=-0.45,
               delay=bool(item.delayed), shrinkA=20, shrinkB=20,
               linestyle="solid" if item.delayed is not None else (0, (2.5, 1.5)))
    loop_id(ax, 2.15, 1.4, "B", direction="cw", r=0.24)
    loop_id(ax, 4.65, 1.4, "B", direction="cw", r=0.24)
    loop_id(ax, 7.0, 1.4, "B", direction="cw", r=0.24)
    ax.text(4.2, 2.85, "structure one: every link inside the operation", ha="center",
            va="center", fontsize=6.8, style="italic")
    legend_rows(ax, [("solid", "delay recorded"), ((0, (2.5, 1.5)), "no time semantics recorded")],
                x=0.4, y=-0.05, dy=0.3, sample=0.5)
    ax.text(8.4, -0.05, "6 links, 3 loops, 3 balancing", ha="right", va="center", fontsize=6.4)
    ax.text(8.4, -0.35, "2 unsupported, 2 without time semantics", ha="right", va="center",
            fontsize=6.4)

    fig.tight_layout()
    save(fig, "loop-structure-internal")


if __name__ == "__main__":
    main()
