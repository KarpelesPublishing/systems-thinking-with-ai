#!/usr/bin/env python3
"""Chapter 3, "Telling the neighbors apart": growth and early S-shaped growth on one window.

The chapter says growth and S-shaped growth are identical until the ceiling starts to bite, that
no observation inside the rising segment separates them, and that a trace at two percent of its
ceiling and one at forty percent look the same and behave differently over the next window. This
figure runs both generators with the same initial value and rate and marks the window in which
the S-shaped path is still under two percent of its capacity:

    uv run --group figures python build/figures/fig_neighbor_confusion.py

Data: chapters.chapter_03_reference_modes.code.modes.exponential_growth(initial=1.0, rate=0.3,
steps=20) against s_shaped_growth(initial=1.0, capacity=100.0, rate=0.3, steps=20), the chapter's
S-shaped parameters. The chapter states no numeric tolerance, so the assert uses the chapter's
own two percent: wherever the S-shaped path is under two percent of capacity, the two paths agree
to within two percent. The shaded window and the label positions are layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_03_reference_modes.code.modes import (  # noqa: E402
    exponential_growth,
    s_shaped_growth,
)


def main():
    steps, capacity = 20, 100.0
    growth = exponential_growth(initial=1.0, rate=0.3, steps=steps)
    logistic = s_shaped_growth(initial=1.0, capacity=capacity, rate=0.3, steps=steps)

    early = [i for i, v in enumerate(logistic) if v < 0.02 * capacity]
    assert early == [0, 1, 2], early
    for i in early:
        assert abs(logistic[i] - growth[i]) / growth[i] < 0.02, (i, growth[i], logistic[i])
    assert logistic[10] / growth[10] < 0.92 and logistic[20] / growth[20] < 0.4

    fig, ax = figure(height_in=2.5)
    t = list(range(steps + 1))
    ax.plot(t, growth, color="black", linestyle=DASHES[0])
    ax.plot(t, logistic, color="black", linestyle=DASHES[1])
    ax.axhline(capacity, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.axvspan(0, early[-1] + 1, color="black", alpha=0.08, linewidth=0)
    ax.set_xlim(0, steps + 2.2)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_ylim(0, 200)
    ax.set_yticks([0, 50, 100, 150, 200])
    ax.set_xlabel("time step")
    ax.set_ylabel("level")
    ax.text(20.3, growth[-1], "growth", fontsize=6.8, ha="left", va="center")
    ax.text(20.3, logistic[-1], "S-shaped\ngrowth", fontsize=6.8, ha="left", va="center")
    ax.text(0.5, 106, "capacity", fontsize=6.5, ha="left", va="bottom")
    ax.text(3.6, 22, "under 2 percent\nof capacity", fontsize=6.3, ha="left", va="bottom")
    ax.annotate("", xy=(3.0, 20), xytext=(3.6, 26),
                arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    fig.tight_layout()
    save(fig, "neighbor-confusion")


if __name__ == "__main__":
    main()
