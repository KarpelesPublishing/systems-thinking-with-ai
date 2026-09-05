#!/usr/bin/env python3
"""Chapter 19, "Three answers from one model": Euler, Heun, and RK4 on one logistic.

The chapter integrates logistic growth with rate 2.6 toward a capacity of 100 from an initial
value of 1 for twenty periods at a step of one and prints final values of 113.40, 56.51, and
99.88, with highest values of 123.35, 69.50, and 99.88. This figure plots the three paths.

    uv run --group figures python build/figures/fig_three_solvers.py

Data: chapters.chapter_19_integration.code.solvers.integrate(logistic(2.6, 100.0), 1.0, 1.0, 20,
solver) for solver in euler, heun, rk4. The asserts pin the chapter's table.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_19_integration.code.solvers import integrate, logistic  # noqa: E402


def main():
    derivative = logistic(rate=2.6, capacity=100.0)
    paths = {s: integrate(derivative, 1.0, 1.0, 20, s) for s in ("euler", "heun", "rk4")}
    ends = {s: round(p[-1], 2) for s, p in paths.items()}
    highs = {s: round(max(p), 2) for s, p in paths.items()}
    assert ends == {"euler": 113.40, "heun": 56.51, "rk4": 99.88}, ends
    assert highs == {"euler": 123.35, "heun": 69.50, "rk4": 99.88}, highs

    t = list(range(21))
    fig, ax = figure(height_in=2.6)
    names = {"euler": "Euler", "heun": "Heun", "rk4": "Runge-Kutta 4"}
    for i, s in enumerate(("euler", "heun", "rk4")):
        ax.plot(t, paths[s], color="black", linestyle=DASHES[i])
    ax.axhline(100.0, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 130)
    ax.set_yticks([0, 50, 100])
    ax.set_xlabel("period, step 1.0")
    ax.set_ylabel("state")
    ax.text(0.3, 102, "capacity 100", fontsize=6.0, ha="left", va="bottom", style="italic")
    ax.text(20.3, ends["euler"], f"{names['euler']} {ends['euler']:.2f}", fontsize=6.5,
            ha="left", va="center", bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.text(20.3, ends["rk4"], f"{names['rk4']} {ends['rk4']:.2f}", fontsize=6.5, ha="left",
            va="center", bbox=dict(facecolor="white", edgecolor="none", pad=0.8))
    ax.text(20.3, ends["heun"], f"{names['heun']} {ends['heun']:.2f}", fontsize=6.5, ha="left",
            va="center")
    ax.set_xlim(0, 26)
    ax.set_xticks([0, 5, 10, 15, 20])

    fig.tight_layout()
    save(fig, "three-solvers")


if __name__ == "__main__":
    main()
