#!/usr/bin/env python3
"""Chapter 4, "When two tubs are connected": two stocks in series sharing one flow.

The chapter has tub A draining into tub B, so that A's outflow is B's inflow and the size of that
flow depends on how much water is in A. It then states the update rule: compute every flow from
the state at time t, then update every stock. This figure draws the structure: a source, tub A,
the shared flow with its valve and the information link from A's level that sets it, tub B, and
a sink:

    uv run --group figures python build/figures/fig_two_tubs.py

No numeric data. The pack (chapters.chapter_04_stock_and_flow) has one stock and no tub names,
so the labels are the chapter's A and B. Placement and the curve of the information link are
layout; the elements and the rule quoted beneath them are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, flow, link, stock  # noqa: E402


def main():
    fig, ax = figure(height_in=1.9)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.2, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")

    cloud(ax, 0.4, 0.0)
    stock(ax, 2.7, 0.0, "tub A", w=1.5, h=0.8, sublabel="litres")
    stock(ax, 5.9, 0.0, "tub B", w=1.5, h=0.8, sublabel="litres")
    cloud(ax, 8.2, 0.0)
    flow(ax, (0.75, 0.0), (1.95, 0.0), label="inflow", label_side="below")
    shared = flow(ax, (3.45, 0.0), (5.15, 0.0))
    flow(ax, (6.65, 0.0), (7.85, 0.0), label="outflow", label_side="below")
    ax.text(shared[0], -0.5, "A's outflow, B's inflow", ha="center", va="top", fontsize=6.8)
    link(ax, (2.7, 0.4), (shared[0], shared[1] + 0.16), polarity="+", curve=-0.55, shrinkA=2,
         shrinkB=6)
    ax.text(3.35, 0.95, "read A's level at t", ha="center", va="bottom", fontsize=6.2,
            style="italic")
    ax.text(4.3, -1.0, "read all flows from the state at t, then write all stocks",
            ha="center", va="center", fontsize=6.2)

    fig.tight_layout()
    save(fig, "two-tubs")


if __name__ == "__main__":
    main()
