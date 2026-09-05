#!/usr/bin/env python3
"""Chapter 32, "The structure": the referral, hiring, and quality loops as a causal-loop diagram.

The chapter names four stocks (customers, workforce, experience, quality) and three loops: a
reinforcing referral loop, a balancing hiring loop with a delay, and a balancing quality loop
that runs through load. This figure draws those loops with the pack's own names: the stock names
are growth.State's fields, the flows are the four rates step() computes (joining, leaving, hiring,
departures), and load and effective capacity are the pack's two functions.

    uv run --group figures python build/figures/fig_growth_loop_structure.py

No numeric data. Placement and arc curvature are layout choices; the nodes, links, polarities,
the delay on hiring, and the loop names are the chapter's. The script asserts that the stocks it
draws are exactly growth.State's fields, so a renamed field breaks the figure.
"""
import sys
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import link, loop_id, text_node  # noqa: E402

from chapters.chapter_32_service_growth.code.growth import State  # noqa: E402

STOCKS = {
    "customers": (2.0, 3.4),
    "workforce": (8.4, 1.2),
    "experience": (6.4, 0.4),
    "quality": (4.4, 1.2),
}


def main():
    assert set(STOCKS) == {f.name for f in fields(State)}, set(STOCKS)

    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.2, 9.4)
    ax.set_ylim(-0.1, 4.55)
    ax.set_aspect("equal")
    ax.axis("off")

    for name, (x, y) in STOCKS.items():
        text_node(ax, x, y, name, fontsize=7.2)
    joining = text_node(ax, 0.6, 2.0, "joining")
    leaving = text_node(ax, 2.4, 0.5, "leaving")
    load = text_node(ax, 4.4, 3.4, "load")
    capacity = text_node(ax, 6.4, 2.3, "effective\ncapacity")
    hiring = text_node(ax, 8.4, 3.4, "hiring")
    customers, workforce = STOCKS["customers"], STOCKS["workforce"]
    experience, quality = STOCKS["experience"], STOCKS["quality"]

    # Referral loop, reinforcing. Polarities are placed by hand beside each head.
    link(ax, customers, joining, None, curve=0.35)
    link(ax, joining, customers, None, curve=0.35)
    link(ax, quality, joining, None, curve=0.0, shrinkA=18, shrinkB=18)
    loop_id(ax, 1.25, 2.7, "R", direction="ccw", r=0.22)

    # Quality loop, balancing, through load.
    link(ax, customers, load, None, curve=0.0, shrinkA=22, shrinkB=12)
    link(ax, load, quality, None, curve=0.0)
    link(ax, quality, leaving, None, curve=0.25, shrinkA=18, shrinkB=18)
    link(ax, leaving, customers, None, curve=0.25, shrinkA=18, shrinkB=22)
    loop_id(ax, 3.3, 2.4, "B", direction="cw", r=0.22)

    # Hiring loop, balancing, with the delay on hiring.
    link(ax, customers, hiring, None, curve=-0.28, shrinkA=22, shrinkB=14)
    link(ax, workforce, hiring, None, curve=0.32, shrinkA=16, shrinkB=12)
    link(ax, hiring, workforce, None, curve=0.32, delay=True, shrinkA=12, shrinkB=16)
    link(ax, workforce, capacity, None, curve=0.0, shrinkA=22, shrinkB=22)
    link(ax, workforce, experience, None, curve=-0.2, shrinkA=22, shrinkB=24)
    link(ax, experience, capacity, None, curve=0.0, shrinkA=16, shrinkB=22)
    link(ax, capacity, load, None, curve=0.0, shrinkA=22, shrinkB=12)
    loop_id(ax, 8.4, 2.3, "B", direction="cw", r=0.22)

    for x, y, sign in [
        (0.55, 2.55, "+"),    # customers to joining
        (1.75, 2.85, "+"),    # joining to customers
        (1.6, 1.5, "+"),    # quality to joining
        (3.95, 3.6, "+"),     # customers to load
        (4.65, 1.75, "-"),    # load to quality
        (3.15, 0.75, "-"),    # quality to leaving
        (2.35, 2.95, "-"),    # leaving to customers
        (7.3, 3.8, "+"),     # customers to hiring
        (7.85, 3.05, "-"),    # workforce to hiring
        (8.95, 1.6, "+"),     # hiring to workforce
        (6.95, 2.0, "+"),     # workforce to capacity
        (7.25, 0.2, "+"),     # workforce to experience
        (6.65, 1.6, "+"),     # experience to capacity
        (4.85, 2.75, "-"),    # capacity to load
    ]:
        ax.text(x, y, sign, ha="center", va="center", fontsize=7.8, zorder=6)

    ax.text(0.6, 1.55, "referral", ha="center", va="center", fontsize=6.0, style="italic")
    ax.text(2.4, 0.1, "churn", ha="center", va="center", fontsize=6.0, style="italic")
    ax.text(8.4, 3.85, "with delay", ha="center", va="center", fontsize=6.0, style="italic")

    fig.tight_layout()
    save(fig, "growth-loop-structure")


if __name__ == "__main__":
    main()
