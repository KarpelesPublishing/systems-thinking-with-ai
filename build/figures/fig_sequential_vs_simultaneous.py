#!/usr/bin/env python3
"""Chapter 19, "Simultaneous update, again": one closed transfer, two update orders.

Two stocks starting at 100 and 0 exchange a quantity with k = 0.3 over one step of 1.0.
Simultaneous update gives (70, 30) and conserves the total of 100. Sequential update gives
(70, 21) and the total comes to 91: nine units have vanished. This figure draws the two results
as paired stacked bars with the totals stated.

    uv run --group figures python build/figures/fig_sequential_vs_simultaneous.py

Data: chapters.chapter_19_integration.code.solvers.sequential_pair(100.0, 0.0, dt=1.0, k=0.3)
and simultaneous_pair(100.0, 0.0, dt=1.0, k=0.3). The asserts pin the chapter's numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402

from chapters.chapter_19_integration.code.solvers import (  # noqa: E402
    sequential_pair,
    simultaneous_pair,
)

WHITE = dict(facecolor="white", edgecolor="none", pad=0.8)


def main():
    seq = sequential_pair(100.0, 0.0, dt=1.0, k=0.3)
    sim = simultaneous_pair(100.0, 0.0, dt=1.0, k=0.3)
    assert seq == (70.0, 21.0), seq
    assert sim == (70.0, 30.0), sim
    assert round(sum(seq)) == 91 and round(sum(sim)) == 100

    fig, ax = figure(height_in=2.0)
    rows = [("start", (100.0, 0.0)), ("simultaneous update", sim), ("sequential update", seq)]
    for i, (name, (a, b)) in enumerate(rows):
        y = len(rows) - 1 - i
        ax.barh(y, a, height=0.55, color="white", edgecolor="black", linewidth=0.8)
        ax.barh(y, b, left=a, height=0.55, color="white", edgecolor="black", linewidth=0.8,
                hatch="////")
        ax.text(a / 2, y, f"A {a:.0f}", ha="center", va="center", fontsize=6.5)
        if b > 0:
            ax.text(a + b / 2, y, f"B {b:.0f}", ha="center", va="center", fontsize=6.5,
                    bbox=dict(facecolor="white", edgecolor="none", pad=0.6))
        ax.text(a + b + 1.5, y, f"total {a + b:.0f}", ha="left", va="center", fontsize=6.8,
                bbox=WHITE)
    ax.set_yticks([2, 1, 0])
    ax.set_yticklabels([name for name, _ in rows])
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 50, 100])
    ax.set_xlabel("units held, k 0.3, one step of 1.0")
    ax.axvline(100.0, color="black", linewidth=0.4, linestyle=(0, (1.2, 1.4)))
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    fig.tight_layout()
    save(fig, "sequential-vs-simultaneous")


if __name__ == "__main__":
    main()
