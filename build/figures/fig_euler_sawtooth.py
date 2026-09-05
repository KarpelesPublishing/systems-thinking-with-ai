#!/usr/bin/env python3
"""Chapter 19, "What Euler assumes": the same logistic under Euler at steps of 1.0 and 0.5.

At a step of one, Euler sawtooths between the forties and the hundred and twenties (48 to 123
over the run) around a capacity of 100. Halving the step settles the path onto the ceiling,
having peaked at 101.1 on the way. This figure plots both paths.

    uv run --group figures python build/figures/fig_euler_sawtooth.py

Data: chapters.chapter_19_integration.code.solvers.integrate(logistic(2.6, 100.0), 1.0, dt, 20,
"euler") for dt in 1.0 and 0.5. The asserts pin the chapter's numbers: the coarse path's range
after it first crosses the capacity, and the fine path's peak.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_19_integration.code.solvers import integrate, logistic  # noqa: E402


def main():
    derivative = logistic(rate=2.6, capacity=100.0)
    coarse = integrate(derivative, 1.0, 1.0, 20, "euler")
    fine = integrate(derivative, 1.0, 0.5, 20, "euler")
    first_over = next(i for i, v in enumerate(coarse) if v > 100.0)
    low, high = min(coarse[first_over:]), max(coarse)
    assert (round(low), round(high)) == (48, 123), (low, high)
    assert round(max(fine), 1) == 101.1, max(fine)
    assert round(coarse[-1], 2) == 113.40

    fig, ax = figure(height_in=2.5)
    ax.plot(list(range(21)), coarse, color="black", linestyle=DASHES[0], marker="o",
            markersize=2.0)
    ax.plot([i * 0.5 for i in range(41)], fine, color="black", linestyle=DASHES[1])
    ax.axhline(100.0, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 130)
    ax.set_yticks([0, 50, 100])
    ax.set_xlabel("period")
    ax.set_ylabel("state")
    ax.text(0.3, 102, "capacity 100", fontsize=6.0, ha="left", va="bottom", style="italic")
    ax.text(6.0, 36, f"step 1.0 (solid, marked): sawtooth from {low:.0f} to {high:.0f}",
            fontsize=6.5, ha="left", va="bottom")
    ax.text(6.0, 30, f"step 0.5 (dashed): settles onto 100, peak {max(fine):.1f}",
            fontsize=6.5, ha="left", va="top")
    ax.set_xticks([0, 5, 10, 15, 20])

    fig.tight_layout()
    save(fig, "euler-sawtooth")


if __name__ == "__main__":
    main()
