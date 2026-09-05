#!/usr/bin/env python3
"""Chapter 16, "The conveyor and the tank": the same step through two delays of mean four.

The chapter feeds a step from 0 to 10 at period 3 through run_pipeline(length=4) and
run_first_order(mean=4.0) and reads period 5 (0.0 against 4.38), period 7 (10.0 against 6.84),
and the tank reaching ninety-five percent around period fourteen. This figure plots both
outflows with direct labels and marks those periods.

    uv run --group figures python build/figures/fig_pipeline_vs_first_order.py

Data: chapters.chapter_16_delays.code.delays with step = [0.0] * 3 + [10.0] * 40,
run_pipeline(step, length=4), run_first_order(step, mean=4.0), and
time_to_fraction(first_order, 10.0, 0.95). The asserts pin the chapter's numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_16_delays.code.delays import (  # noqa: E402
    run_first_order,
    run_pipeline,
    time_to_fraction,
)


def main():
    step = [0.0] * 3 + [10.0] * 40
    pipeline = run_pipeline(step, length=4)
    first_order = run_first_order(step, mean=4.0)
    assert (pipeline[5], round(first_order[5], 2)) == (0.0, 4.38), (pipeline[5], first_order[5])
    assert (pipeline[7], round(first_order[7], 2)) == (10.0, 6.84), (pipeline[7], first_order[7])
    ninety_five = time_to_fraction(first_order, 10.0, 0.95)
    assert ninety_five == 14, ninety_five

    t = list(range(24))
    fig, ax = figure(height_in=2.5)
    ax.plot(t, pipeline[:24], color="black", linestyle=DASHES[0], drawstyle="steps-post")
    ax.plot(t, first_order[:24], color="black", linestyle=DASHES[1])
    ax.plot(t, step[:24], color="black", linewidth=0.5, linestyle=DASHES[2],
            drawstyle="steps-post")
    for p in (5, 7):
        ax.plot([p, p], [pipeline[p], first_order[p]], color="black", linewidth=0.5)
        ax.plot([p], [first_order[p]], marker="o", color="black", markersize=2.5)
        ax.plot([p], [pipeline[p]], marker="o", color="black", markersize=2.5)
    ax.text(5.3, 2.4, f"period 5: 0.0 vs {first_order[5]:.2f}", fontsize=6.3, ha="left",
            va="center")
    ax.text(7.4, 5.6, f"period 7: 10.0 vs {first_order[7]:.2f}", fontsize=6.3, ha="left",
            va="top")
    ax.plot([ninety_five], [first_order[ninety_five]], marker="o", color="black", markersize=2.5)
    ax.text(ninety_five + 0.4, first_order[ninety_five] - 0.5, f"95% at period {ninety_five}",
            fontsize=6.3, ha="left", va="top")
    ax.text(10.5, 10.55, "pipeline, length 4", fontsize=6.8, ha="left", va="bottom")
    ax.text(11.0, 7.4, "first order, mean 4", fontsize=6.8, ha="left", va="top")
    ax.text(1.4, 0.4, "input step", fontsize=6.3, ha="left", va="bottom", style="italic")
    ax.set_xlim(0, 23)
    ax.set_ylim(0, 12)
    ax.set_yticks([0, 5, 10])
    ax.set_xlabel("period")
    ax.set_ylabel("outflow")

    fig.tight_layout()
    save(fig, "pipeline-vs-first-order")


if __name__ == "__main__":
    main()
