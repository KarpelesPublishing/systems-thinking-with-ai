#!/usr/bin/env python3
"""Chapter 5, "Four stations and what each can see": the chain with its two pipelines.

The chapter names four stations and gives each an inventory and a backlog, an order pipeline
carrying orders upstream and a shipment pipeline carrying cases downstream, each a delay. This
figure draws the four stations in a row, from the customer at the left to the factory at the
right, with shipments flowing downstream on the upper track and orders flowing upstream on the
lower track, each crossing carrying a delay mark:

    uv run --group figures python build/figures/fig_beer_game_chain.py

No numeric data. Station names are STAGE_NAMES from chapters.chapter_05_beer_game.code.models,
in pack order. The two-week delay marks stand for the pack's default pipeline_weeks=2 in each
direction. Placement is layout; the stations, the two pipelines, and their directions are the
chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, delay_mark, flow, link, stock  # noqa: E402

from chapters.chapter_05_beer_game.code.models import STAGE_NAMES  # noqa: E402


def main():
    fig, ax = figure(height_in=2.15)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.35, 1.45)
    ax.set_aspect("equal")
    ax.axis("off")

    xs = [1.55, 3.45, 5.35, 7.25]
    for x, name in zip(xs, STAGE_NAMES, strict=True):
        stock(ax, x, 0.0, name, w=1.45, h=0.78, sublabel="inventory, backlog")
    cloud(ax, 0.3, 0.0)
    ax.text(0.3, -0.52, "customer", ha="center", va="center", fontsize=6.2)
    ax.text(8.35, 0.0, "raw\nmaterial", ha="center", va="center", fontsize=6.0)

    # shipments downstream on the upper track (right to left)
    for a, b in zip(xs[1:], xs[:-1], strict=True):
        flow(ax, (a - 0.725, 0.2), (b + 0.725, 0.2), valve=False, double=True)
    flow(ax, (xs[0] - 0.725, 0.2), (0.62, 0.2), valve=False)
    # orders upstream on the lower track (left to right)
    for a, b in zip(xs[:-1], xs[1:], strict=True):
        link(ax, (a + 0.725, -0.2), (b - 0.725, -0.2), polarity="", curve=0.0, shrinkA=0,
             shrinkB=0, lw=0.9)
        delay_mark(ax, ((a + b) / 2, -0.2), 0.0)
    link(ax, (0.62, -0.2), (xs[0] - 0.725, -0.2), polarity="", curve=0.0, shrinkA=0, shrinkB=0,
         lw=0.9)
    flow(ax, (8.05, 0.2), (xs[3] + 0.725, 0.2), valve=False, shrinkA=0)

    ax.text(4.4, 0.98, "shipment pipeline: cases moving downstream, two weeks in transit",
            ha="center", va="center", fontsize=6.2)
    ax.text(4.4, -0.98, "order pipeline: orders moving upstream, two weeks to be seen",
            ha="center", va="center", fontsize=6.2)

    fig.tight_layout()
    save(fig, "beer-game-chain")


if __name__ == "__main__":
    main()
