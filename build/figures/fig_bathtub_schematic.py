#!/usr/bin/env python3
"""Chapter 4, "Level and rate, in plain language": the bathtub as a stock with two flows.

The chapter defines a stock as an amount that exists at a moment and a flow as a rate that exists
over an interval, then states that a stock changes only through its flows. This figure draws
the structure the chapter describes: a source cloud, an inflow valve, the tub as a stock, an
outflow valve, and a sink cloud, with the units the chapter attaches to each.

    uv run --group figures python build/figures/fig_bathtub_schematic.py

No numeric data. Placement is a layout choice; the elements and units are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, flow, stock  # noqa: E402


def main():
    fig, ax = figure(height_in=1.55)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-0.75, 1.25)
    ax.set_aspect("equal")
    ax.axis("off")

    cloud(ax, 0.55, 0.0)
    stock(ax, 4.2, 0.0, "water in the tub", w=2.4, h=0.8, sublabel="litres, a level")
    cloud(ax, 7.85, 0.0)
    flow(ax, (0.9, 0.0), (2.95, 0.0), label="inflow", shrinkA=0.0, shrinkB=0.0)
    flow(ax, (5.45, 0.0), (7.5, 0.0), label="outflow", shrinkA=0.0, shrinkB=0.0)
    ax.text(1.92, -0.42, "litres per minute", ha="center", va="center", fontsize=6.2,
            style="italic")
    ax.text(6.48, -0.42, "litres per minute", ha="center", va="center", fontsize=6.2,
            style="italic")
    ax.text(0.55, -0.55, "source", ha="center", va="center", fontsize=6.2)
    ax.text(7.85, -0.55, "sink", ha="center", va="center", fontsize=6.2)

    fig.tight_layout()
    save(fig, "bathtub-schematic")


if __name__ == "__main__":
    main()
