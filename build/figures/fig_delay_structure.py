#!/usr/bin/env python3
"""Chapter 16, "Material and information": a material delay beside an information delay.

The chapter separates a material delay, which holds a physical quantity in transit and enters the
conservation check, from an information delay, which holds a belief or a signal and conserves
nothing. This figure draws the first as a stock with an inflow and an outflow and the second as
a perception smoothing a signal through a delay mark.

    uv run --group figures python build/figures/fig_delay_structure.py

No numeric data. Placement is a layout choice; the two kinds and their properties are the
chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, flow, link, stock, text_node  # noqa: E402


def main():
    fig, ax = figure(height_in=2.4)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.75, 1.35)
    ax.set_aspect("equal")
    ax.axis("off")

    # material delay: conserved
    y = 0.45
    cloud(ax, 0.45, y)
    stock(ax, 2.35, y, "in transit", w=1.6, h=0.7, sublabel="units, counted")
    cloud(ax, 4.25, y)
    flow(ax, (0.8, y), (1.55, y), label="ship", valve=False)
    flow(ax, (3.15, y), (3.9, y), label="arrive", valve=False)
    ax.text(2.35, -0.35, "material delay", ha="center", va="center", fontsize=7.0)
    ax.text(2.35, -0.72, "what is inside is real:\nit enters the conservation check",
            ha="center", va="top", fontsize=6.0, style="italic")

    # information delay: nothing conserved
    text_node(ax, 5.6, y, "true value", fontsize=7.0)
    stock(ax, 7.5, y, "perceived value", w=1.7, h=0.7, sublabel="a belief")
    link(ax, (5.6, y), (7.5, y), polarity="", curve=0.0, delay=True, shrinkA=22, shrinkB=32)
    ax.text(6.9, -0.35, "information delay", ha="center", va="center", fontsize=7.0)
    ax.text(6.9, -0.72, "a signal, smoothed over time:\nnothing is conserved",
            ha="center", va="top", fontsize=6.0, style="italic")
    ax.plot([4.85, 4.85], [-1.55, 1.15], color="black", linewidth=0.5, linestyle=(0, (1.2, 1.4)))

    fig.tight_layout()
    save(fig, "delay-structure")


if __name__ == "__main__":
    main()
