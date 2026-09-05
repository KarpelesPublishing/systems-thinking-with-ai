#!/usr/bin/env python3
"""Chapter 19, "The refinement test": the Euler endpoint at three halved steps.

The chapter runs step_refinement on the logistic (rate 2.6, capacity 100, from 1.0, horizon
20) with Euler at steps 1.0, 0.5, and 0.25 and prints [113.40, 100.00, 100.00]: the first
halving moves the endpoint by thirteen and the second by nothing, which is convergence. This
figure plots endpoint against step size.

    uv run --group figures python build/figures/fig_refinement_test.py

Data: chapters.chapter_19_integration.code.solvers.step_refinement(logistic(2.6, 100.0), 1.0,
horizon=20, solver="euler", steps=(1.0, 0.5, 0.25)) and converged(endpoints, tolerance=0.1).
The asserts pin the chapter's numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402

from chapters.chapter_19_integration.code.solvers import (  # noqa: E402
    converged,
    logistic,
    step_refinement,
)

STEPS = (1.0, 0.5, 0.25)


def main():
    derivative = logistic(rate=2.6, capacity=100.0)
    ends = step_refinement(derivative, 1.0, horizon=20, solver="euler", steps=STEPS)
    assert [round(e, 2) for e in ends] == [113.40, 100.00, 100.00], ends
    assert converged(ends, tolerance=0.1)

    fig, ax = figure(height_in=2.2)
    ax.plot(STEPS, ends, color="black", marker="o", markersize=3.0)
    ax.axhline(100.0, color="black", linewidth=0.4, linestyle=(0, (1.2, 1.4)))
    ax.set_xscale("log", base=2)
    ax.set_xticks(STEPS)
    ax.set_xticklabels([str(s) for s in STEPS])
    ax.set_xlim(0.2, 1.25)
    ax.set_ylim(95, 118)
    ax.set_yticks([100, 110])
    ax.set_xlabel("step size (halved twice)")
    ax.set_ylabel("endpoint at period 20")
    ax.invert_xaxis()
    for s, e in zip(STEPS, ends, strict=True):
        ax.annotate(f"{e:.2f}", xy=(s, e), xytext=(0, 5), textcoords="offset points",
                    fontsize=6.5, ha="center", va="bottom")
    ax.text(0.35, 109.5, f"first halving moves it by {ends[0] - ends[1]:.1f},\n"
            f"second by {abs(ends[1] - ends[2]):.2f}: converged", fontsize=6.3, ha="center",
            va="center", style="italic")
    ax.text(1.22, 99.5, "capacity 100", fontsize=6.0, ha="left", va="top", style="italic")

    fig.tight_layout()
    save(fig, "refinement-test")


if __name__ == "__main__":
    main()
