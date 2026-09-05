#!/usr/bin/env python3
"""Chapter 9, "Four templates and what each one warns about": the limit multiplier over load.

The chapter says that in its own logistic engine a system at two percent of capacity is growing at
ninety-eight percent of its unconstrained rate, and at ten percent it is at ninety percent.
The engine is fixed_limit, whose step adds rate * state * (1 - state / capacity), so the multiplier
on the unconstrained rate is 1 - state / capacity. This figure plots that multiplier against load
and marks the two readings the chapter gives:

    uv run --group figures python build/figures/fig_limits_to_growth_curve.py

Data: chapters.chapter_09_archetypes.code.limits.fixed_limit(initial=1.0, capacity=100.0,
rate=0.3, steps=120), the chapter's Boundary A run. At each step the realised increment divided
by the unconstrained increment rate * state is the multiplier. The chapter's readings are taken
at exactly two percent and ten percent of capacity, where the multiplier is 0.98 and 0.90; the
run's own steps land near but not on those loads, so the marks are read off the exact relation
rather than off a sampled step. The asserts pin both, and pin that the
multiplier equals 1 - load at every step. Marker and label placement are layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_09_archetypes.code.limits import fixed_limit  # noqa: E402


def main():
    capacity, rate = 100.0, 0.3
    path = fixed_limit(initial=1.0, capacity=capacity, rate=rate, steps=120)
    load = [s / capacity for s in path[:-1]]
    multiplier = [(nxt - s) / (rate * s) for s, nxt in zip(path[:-1], path[1:], strict=True)]
    for x, m in zip(load, multiplier, strict=True):
        assert abs(m - (1.0 - x)) < 1e-9, (x, m)

    marks = [(0.02, 1.0 - 0.02), (0.10, 1.0 - 0.10)]
    assert [round(m, 2) for _, m in marks] == [0.98, 0.90], marks

    fig, ax = figure(height_in=2.4)
    ax.plot(load, multiplier, color="black", linestyle=DASHES[0])
    for (x, m), text, tx, ty in zip(marks,
                                    ("2 percent of capacity:\n0.98 of full rate",
                                     "10 percent of capacity:\n0.90 of full rate"),
                                    (0.30, 0.46), (0.98, 0.80), strict=True):
        ax.plot([x], [m], color="black", marker="o", markersize=3.0, markerfacecolor="white")
        ax.annotate(text, xy=(x, m), xytext=(tx, ty),
                    fontsize=6.4, ha="left", va="top",
                    arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black",
                                    shrinkA=0, shrinkB=3))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.05)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("load, state as a fraction of capacity")
    ax.set_ylabel("share of unconstrained growth rate")
    fig.tight_layout()
    save(fig, "limits-to-growth-curve")


if __name__ == "__main__":
    main()
