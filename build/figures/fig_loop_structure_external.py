#!/usr/bin/env python3
"""Chapter 8, "Two structures for the same behavior": structure two, external transmission.

The chapter describes structure two as the operation responding to a demand signal that was
already swinging when it arrived, because the customer's own ordering policy amplified something
further downstream. It gives structure two in prose only; the Link list in the pack's audit
example is structure one. This figure writes the prose as links: end demand reaches the
customer, the customer's ordering rule (a balancing loop on the customer's own inventory,
Chapter 5's mechanism) turns it into orders, and the orders drive production and employment at
the operation through delays, with no loop closing inside the operation:

    uv run --group figures python build/figures/fig_loop_structure_external.py

Structure: a Link list written for this figure from the chapter's paragraph, audited with
chapters.chapter_08_causal_graph.code.graph. The assert pins what that list must show for the
figure to be honest: exactly one loop, balancing, and it lies on the customer's side of the
boundary. Evidence levels are "proposed" because the chapter presents this as a candidate. Node
placement is layout.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import boundary, delay_mark, link, loop_id, text_node  # noqa: E402

from chapters.chapter_08_causal_graph.code.graph import (  # noqa: E402
    Link,
    audit,
    find_loops,
    loop_polarity,
)

LINKS = [
    Link("end demand", "customer orders", 1, "proposed", delayed=True),
    Link("customer orders", "customer inventory", 1, "proposed", delayed=True),
    Link("customer inventory", "customer orders", -1, "proposed", delayed=False),
    Link("customer orders", "orders received", 1, "proposed", delayed=True),
    Link("orders received", "production", 1, "proposed", delayed=True),
    Link("production", "employment", 1, "proposed", delayed=True),
]
OPERATION = {"orders received", "production", "employment"}


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
    loops = find_loops(LINKS)
    assert summary["loops"] == 1 and summary["balancing"] == 1, summary
    assert loop_polarity(loops[0], LINKS) == "balancing"
    assert not (set(loops[0]) & OPERATION), loops
    assert summary["no_time_semantics"] == 0

    fig, ax = figure(height_in=2.6)
    ax.set_xlim(-0.3, 9.0)
    ax.set_ylim(-0.9, 3.0)
    ax.set_aspect("equal")
    ax.axis("off")

    pos = {"end demand": (0.6, 1.6), "customer orders": (3.0, 1.6),
           "customer inventory": (3.0, -0.05), "orders received": (5.7, 1.6),
           "production": (8.0, 1.6), "employment": (8.0, 0.15)}
    for name, (x, y) in pos.items():
        text_node(ax, x, y, name)
    curves = {("customer orders", "customer inventory"): 0.65,
              ("customer inventory", "customer orders"): 0.65}
    shrinks = {("customer orders", "customer inventory"): (10, 10),
               ("customer inventory", "customer orders"): (10, 10),
               ("production", "employment"): (9, 9),
               ("end demand", "customer orders"): (19, 30),
               ("customer orders", "orders received"): (30, 30),
               ("orders received", "production"): (30, 20)}
    for item in LINKS:
        key = (item.source, item.target)
        sa, sb = shrinks.get(key, (22, 22))
        causal(ax, pos[item.source], pos[item.target], "+" if item.polarity > 0 else "-",
               curve=curves.get(key, 0.0), delay=bool(item.delayed), shrinkA=sa, shrinkB=sb)
    loop_id(ax, 3.0, 0.78, "B", direction="cw", r=0.2)
    boundary(ax, 4.65, -0.35, 8.9, 2.45, "the operation")
    ax.text(4.35, 2.8, "structure two: the swing arrives from outside, no loop closes inside",
            ha="center", va="center", fontsize=6.8, style="italic")
    ax.text(3.0, -0.62, "customer's ordering rule,\nChapter 5's mechanism", ha="center",
            va="center", fontsize=6.0, style="italic")

    fig.tight_layout()
    save(fig, "loop-structure-external")


if __name__ == "__main__":
    main()
