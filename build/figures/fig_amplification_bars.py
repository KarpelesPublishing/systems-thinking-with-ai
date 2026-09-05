#!/usr/bin/env python3
"""Chapter 5, "What the reconstruction produces": amplification and variability by station.

The chapter runs the chain on a step from four cases a week to eight and prints, station by
station from the retailer to the factory, an order swing relative to the customer's of 5.7x,
14.9x, 28.3x, and 34.3x, and a week-to-week variability of 8.4, 20.9, 39.6, and 48.0. This figure
sets the two measures side by side as grouped bars, hatched and plain:

    uv run --group figures python build/figures/fig_amplification_bars.py

Data: run_chain([4.0] * 5 + [8.0] * 45, ChainParameters(supply_line_weight=0.0)) from
chapters.chapter_05_beer_game.code.chain, then amplification_ratio(demand, stage orders) and
stage_variability(history) from the same pack's amplification module. Station names come from
STAGE_NAMES. The asserts pin the eight printed numbers. Bar width and hatch are layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402

from chapters.chapter_05_beer_game.code.amplification import (  # noqa: E402
    amplification_ratio,
    stage_variability,
)
from chapters.chapter_05_beer_game.code.chain import run_chain  # noqa: E402
from chapters.chapter_05_beer_game.code.models import STAGE_NAMES, ChainParameters  # noqa: E402


def main():
    demand = [4.0] * 5 + [8.0] * 45
    history = run_chain(demand, ChainParameters(supply_line_weight=0.0))
    amplification = [
        amplification_ratio(demand, [week[i] for week in history["orders"]])
        for i in range(len(STAGE_NAMES))
    ]
    variability = stage_variability(history)

    assert [round(a, 1) for a in amplification] == [5.7, 14.9, 28.3, 34.3], amplification
    assert [round(v, 1) for v in variability] == [8.4, 20.9, 39.6, 48.0], variability

    fig, ax = figure(height_in=2.5)
    x = list(range(len(STAGE_NAMES)))
    w = 0.36
    left = [xi - w / 2 for xi in x]
    right = [xi + w / 2 for xi in x]
    ax.bar(left, amplification, width=w, facecolor="white", edgecolor="black", linewidth=0.7,
           hatch="////")
    ax.bar(right, variability, width=w, facecolor="black", edgecolor="black", linewidth=0.7)
    for xi, a in zip(left, amplification, strict=True):
        ax.text(xi, a + 1.0, f"{a:.1f}x", ha="center", va="bottom", fontsize=6.3)
    for xi, v in zip(right, variability, strict=True):
        ax.text(xi, v + 1.0, f"{v:.1f}", ha="center", va="bottom", fontsize=6.3)
    ax.set_xticks(x)
    ax.set_xticklabels(STAGE_NAMES)
    ax.set_ylim(0, 58)
    ax.set_yticks([0, 10, 20, 30, 40, 50])
    ax.set_ylabel("order swing, order variability")
    ax.text(-0.35, 51, "hatched: swing relative to the customer's (x)", fontsize=6.4, ha="left",
            va="bottom")
    ax.text(-0.35, 46, "solid: week-to-week variability (cases)", fontsize=6.4, ha="left",
            va="bottom")
    fig.tight_layout()
    save(fig, "amplification-bars")


if __name__ == "__main__":
    main()
