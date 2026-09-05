#!/usr/bin/env python3
"""Chapter 33, "The stocks": debt, defects, morale, and delivered features as stocks and flows.

The chapter names four stocks: technical debt (shortcuts taken and not repaid), defects
(discovered and not yet fixed), morale, and features delivered as a cumulative counter. It
then lists the links: debt creates defects, defects consume capacity through rework, debt drags
on capacity directly, morale follows the defect load and scales capacity, and repayment drains
debt. This figure draws that structure with the pack's names: the four stocks are debt.State's
fields, the flows are the rates step() computes (delivered, new_debt, repaid, surfacing, fixing),
and available capacity is the pack's function of the same name.

    uv run --group figures python build/figures/fig_debt_stocks_structure.py

No numeric data. Placement is a layout choice; nodes, flows, and link polarities are the
chapter's. The script asserts the stocks it draws are exactly debt.State's fields.
"""
import sys
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, cloud, delay_mark, flow, link, stock  # noqa: E402

from chapters.chapter_33_technical_debt.code.debt import State  # noqa: E402

STOCKS = {
    "features_done": (3.0, 3.0),
    "debt": (7.4, 3.0),
    "defects": (7.4, 0.8),
    "morale": (3.0, 0.8),
}


def main():
    assert set(STOCKS) == {f.name for f in fields(State)}, set(STOCKS)

    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.05, 10.25)
    ax.set_ylim(-0.35, 3.95)
    ax.set_aspect("equal")
    ax.axis("off")

    stock(ax, *STOCKS["features_done"], "features done", w=1.8, sublabel="cumulative")
    stock(ax, *STOCKS["debt"], "debt", w=1.8, sublabel="shortcuts unpaid")
    stock(ax, *STOCKS["defects"], "defects", w=1.8, sublabel="found, unfixed")
    stock(ax, *STOCKS["morale"], "morale", w=1.8, sublabel="0.2 to 1")

    cloud(ax, 0.4, 3.0)
    delivered = flow(ax, (0.7, 3.0), (2.1, 3.0))
    ax.text(1.0, 2.62, "delivered", ha="center", va="center", fontsize=6.8)
    cloud(ax, 5.0, 3.0)
    new_debt = flow(ax, (5.3, 3.0), (6.5, 3.0), label="new debt", label_side="below")
    flow(ax, (8.3, 3.0), (9.5, 3.0), label="repaid", label_side="below")
    cloud(ax, 9.8, 3.0)
    cloud(ax, 5.0, 0.8)
    surfacing = flow(ax, (5.3, 0.8), (6.5, 0.8), label="surfacing", label_side="below")
    flow(ax, (8.3, 0.8), (9.5, 0.8), label="fixing", label_side="above")
    cloud(ax, 9.8, 0.8)
    ax.text(8.9, 0.45, "rework", ha="center", va="center", fontsize=6.2, style="italic")
    ax.text(8.9, 3.55, "policy share", ha="center", va="center", fontsize=6.2, style="italic")
    cloud(ax, 0.4, 0.8)
    flow(ax, (0.7, 0.8), (2.1, 0.8), label="toward target", label_side="above")

    capacity = auxiliary(ax, 4.4, 1.9, "available\ncapacity", r=0.42, fontsize=6.2)

    # Links the chapter lists, with the polarity beside each head.
    link(ax, STOCKS["debt"], surfacing, None, curve=0.3, shrinkA=14, shrinkB=8)
    link(ax, STOCKS["debt"], capacity, None, curve=0.0, shrinkA=30, shrinkB=18)
    link(ax, STOCKS["defects"], capacity, None, curve=0.2, shrinkA=30, shrinkB=18)
    link(ax, STOCKS["defects"], STOCKS["morale"], None, curve=-0.25, shrinkA=32, shrinkB=32)
    delay_mark(ax, (5.2, 0.25), 0.0)   # apex of that arc, placed by hand
    link(ax, STOCKS["morale"], capacity, None, curve=0.0, shrinkA=20, shrinkB=14)
    link(ax, capacity, delivered, None, curve=-0.2, shrinkA=18, shrinkB=8)
    link(ax, delivered, new_debt, None, curve=-0.28, shrinkA=8, shrinkB=8)
    for x, y, sign in [
        (6.2, 1.2, "+"),      # debt to surfacing
        (5.15, 2.25, "-"),    # debt to capacity
        (5.15, 1.5, "-"),     # defects to capacity
        (4.25, 0.55, "-"),    # defects to morale
        (3.35, 1.7, "+"),     # morale to capacity
        (1.9, 2.25, "+"),     # capacity to delivered
        (5.45, 3.5, "+"),     # delivered to new debt
    ]:
        ax.text(x, y, sign, ha="center", va="center", fontsize=7.8, zorder=6)

    fig.tight_layout()
    save(fig, "debt-stocks-structure")


if __name__ == "__main__":
    main()
