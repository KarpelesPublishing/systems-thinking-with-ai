#!/usr/bin/env python3
"""Chapter 34, "The policy that improves the average": mean wait per group under two policies.

The chapter's opening table runs the hospital model under first come, first served and under
shortest first, same arrivals, same staffing rule, same seed, and prints routine and complex
mean waits of 1.23 and 1.17 under FIFO and 0.94 and 5.89 under shortest first, a gap of 1.05
against 6.29, and a population mean of 1.22 against 2.18 once the groups are weighted by their
shares. This figure draws the per-group means as hatched bars and the population mean as a marker.

    uv run --group figures python build/figures/fig_per_group_waits.py

Data: chapters.chapter_34_hospital_hybrid.code.hospital.run(StaffingPolicy(priority=p)) for
p in "fifo" and "shortest_first", default periods, arrivals, groups, and seed, then
equity_gap() on each outcome. The population mean weights each group's mean by its share in
DEFAULT_GROUPS, which is how the chapter computes it. The asserts pin the printed numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402

from chapters.chapter_34_hospital_hybrid.code.hospital import (  # noqa: E402
    DEFAULT_GROUPS,
    StaffingPolicy,
    equity_gap,
    run,
)

POLICIES = [("fifo", "first come,\nfirst served"), ("shortest_first", "shortest first")]


def main():
    outcomes = {p: run(StaffingPolicy(priority=p)) for p, _ in POLICIES}
    means = {p: o["mean_by_group"] for p, o in outcomes.items()}
    population = {p: sum(g.share * means[p][g.name] for g in DEFAULT_GROUPS) for p in means}

    # The numbers the chapter prints.
    assert round(means["fifo"]["routine"], 2) == 1.23 and round(means["fifo"]["complex"], 2) == 1.17
    assert round(means["shortest_first"]["routine"], 2) == 0.94
    assert round(means["shortest_first"]["complex"], 2) == 5.89
    assert round(equity_gap(outcomes["fifo"]), 2) == 1.05
    assert round(equity_gap(outcomes["shortest_first"]), 2) == 6.29
    assert round(population["fifo"], 2) == 1.22 and round(population["shortest_first"], 2) == 2.18
    assert outcomes["shortest_first"]["queue_left"] == 49.0

    fig, ax = figure(height_in=2.4)
    width = 0.28
    centres = [0.0, 1.3]
    hatches = {"routine": "////", "complex": "...."}
    for i, (p, label) in zip(centres, POLICIES):
        for j, group in enumerate(("routine", "complex")):
            x = i + (j - 0.5) * width
            v = means[p][group]
            ax.bar(x, v, width=width, facecolor="white", edgecolor="black", linewidth=0.7,
                   hatch=hatches[group])
            ax.text(x, v + 0.12, f"{v:.2f}", ha="center", va="bottom", fontsize=6.5)
        ax.plot([i - width, i + width], [population[p]] * 2, color="black", linewidth=1.0,
                zorder=5)
        ax.plot([i], [population[p]], marker="D", color="black", markersize=3.5,
                linestyle="none", zorder=5)
        ax.text(i + width + 0.05, population[p], f"population {population[p]:.2f}", ha="left",
                va="center", fontsize=6.5)
    ax.set_xticks(centres)
    ax.set_xticklabels([label for _, label in POLICIES])
    ax.set_xlim(-0.5, 2.55)
    ax.set_ylim(0, 6.8)
    ax.set_yticks([0, 2, 4, 6])
    ax.set_ylabel("mean wait, periods")
    ax.text(-0.45, 6.6, "routine, hatched; complex, dotted", fontsize=6.5, ha="left", va="top",
            style="italic")
    ax.text(centres[1] + width + 0.05, 5.6,
            f"gap {equity_gap(outcomes['shortest_first']):.2f} to 1,\n"
            f"{outcomes['shortest_first']['queue_left']:.0f} never served",
            fontsize=6.5, ha="left", va="top")

    save(fig, "per-group-waits")


if __name__ == "__main__":
    main()
