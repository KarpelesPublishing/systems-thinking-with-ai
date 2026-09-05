#!/usr/bin/env python3
"""Chapter 38, "Capacity Arrives When the Price Has Gone": four investment rules, one structure.

The chapter runs the fitted document under four rules at the fitted values and no draws. Building
when margins are good, the fitted rule, cycles with a period of 93 months and an amplitude of 18.1
points around a mean of 72.8. A trigger on current utilization with the same appetite cycles at 33
months with an amplitude of 5.1 around 77.8. The fitted rule with a dead band a tenth wide damps to
an amplitude of 2.0. Fixed replacement holds utilization flat at 80. This figure plots the four
paths:

    uv run --group figures python build/figures/fig_investment_rule_comparison.py

Data: chapters.chapter_38_capacity_cycle.code.calibrate.policies and policy_statistics. The
asserts pin the numbers the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402
from sdvocab import legend_rows  # noqa: E402

from chapters.chapter_22_runtime.code.runtime import Runtime  # noqa: E402
from chapters.chapter_35_calibration.code.calibrate import with_values  # noqa: E402
from chapters.chapter_38_capacity_cycle.code import calibrate as c  # noqa: E402

LABELS = {
    "build_when_margins_good": "build when margins are good",
    "utilisation_trigger": "utilization trigger",
    "smoothed_margin_trigger": "margin rule with dead band",
    "fixed_replacement": "fixed replacement",
}


def main():
    stats = {r["policy"]: r for r in c.policy_statistics()}

    # The numbers the chapter prints.
    base = stats["build_when_margins_good"]
    assert (base["period"], base["amplitude"], base["mean_utilization"]) == (93, 18.1, 72.8)
    trig = stats["utilisation_trigger"]
    assert (trig["period"], trig["amplitude"], trig["mean_utilization"]) == (33, 5.1, 77.8)
    band = stats["smoothed_margin_trigger"]
    assert (band["period"], band["amplitude"], band["mean_utilization"]) == (None, 2.0, 78.0)
    fixed = stats["fixed_replacement"]
    assert (fixed["period"], fixed["amplitude"], fixed["mean_utilization"]) == (None, 0.0, 80.0)

    doc = c.fitted_document()
    fig, ax = figure(height_in=2.5)
    for i, policy in enumerate(c.policies()):
        path = Runtime(with_values(doc, policy.settings), c.SETTINGS).run().series["utilization"]
        years = [m / 12 for m in range(len(path))]
        ax.plot(years, path, color="black", linestyle=DASHES[i], linewidth=0.9)
    ax.set_xlim(0, 30)
    ax.set_ylim(60, 90)
    ax.set_yticks([60, 70, 80, 90])
    ax.set_xticks([0, 5, 10, 15, 20, 25, 30])
    ax.set_xlabel("years from the start of the run")
    ax.set_ylabel("utilization, percent")
    legend_rows(ax, [
        (DASHES[0], "build when margins are good: 93 months, 18.1 points"),
        (DASHES[1], "utilization trigger: 33 months, 5.1 points"),
        (DASHES[2], "margin rule with dead band: 2.0 points"),
        (DASHES[3], "fixed replacement: flat at 80"),
    ], x=13.2, y=89.0, dy=1.55, sample=2.2, fontsize=6.2)
    fig.tight_layout()
    save(fig, "investment-rule-comparison")


if __name__ == "__main__":
    main()
