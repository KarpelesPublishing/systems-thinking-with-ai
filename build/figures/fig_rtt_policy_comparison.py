#!/usr/bin/env python3
"""Chapter 36, "Elective Backlogs as a Stock": four policies from June 2022, against the record.

The chapter resets the fitted document to the record at June 2022 and runs it unchanged and
under three policies for forty-eight months: a ten percent capacity uplift, a quarter of capacity
directed at pathways over 52 weeks, and a validation drive at nine percent of the list a month.
This figure plots those four runs from the chapter pack and the record over the same months:

    uv run --group figures python build/figures/fig_rtt_policy_comparison.py

Data: chapters.chapter_36_elective_backlog.code.calibrate.policy_document() with each policy in
calibrate.POLICIES, run for 48 months at the pack's step, and the record from
`data/nhs_rtt/rtt_national_monthly.csv`. Total incomplete pathways, millions. The asserts pin
the headline table the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_36_elective_backlog.code import calibrate as c  # noqa: E402


def main():
    headline = {r["series"]: (r["0"], r["24"], r["48"]) for r in c.headline_table()}
    assert headline["record"] == (6760060, 7621297, 7147562)
    assert headline["model"] == (6760060, 5422413, 5435468)
    assert headline["uniform_uplift"] == (6760060, 3525786, 2943347)
    assert headline["longest_first"] == (6760060, 5401897, 5430712)
    assert headline["validation_push"] == (6760060, 3708932, 3650522)

    doc = c.policy_document()
    runs = {}
    for policy in [c.baseline_policy()] + c.POLICIES:
        result = c.run(c.with_policy(doc, policy), 48)
        runs[policy.name] = (result.times, [v / 1e6 for v in result.series["total_incomplete"]])
    rows = [r for r in c.read_record() if r["period"] >= c.POLICY_START]
    record_t = [c.months_between(c.POLICY_START, r["period"]) for r in rows]
    record_v = [float(r["total_incomplete"]) / 1e6 for r in rows]

    fig, ax = figure(height_in=2.7)
    ax.plot(record_t, record_v, color="black", linestyle="none", marker="o", markersize=1.6)
    order = ["baseline", "longest_first", "validation_push", "uniform_uplift"]
    for dash, name in zip(DASHES, order):
        t, v = runs[name]
        ax.plot(t, v, color="black", linestyle=dash)
    ax.set_xlim(0, 48)
    ax.set_xticks([0, 12, 24, 36, 48])
    ax.set_xticklabels(["Jun 2022", "Jun 2023", "Jun 2024", "Jun 2025", "Jun 2026"])
    ax.set_ylim(2, 8.2)
    ax.set_yticks([2, 3, 4, 5, 6, 7, 8])
    ax.set_ylabel("incomplete pathways, millions")
    ax.text(30, 7.85, "record", fontsize=6.8, ha="left", va="center")
    ax.text(30, 5.65, "fitted model, unchanged", fontsize=6.8, ha="left", va="bottom")
    ax.text(30, 5.25, "longest first", fontsize=6.8, ha="left", va="top")
    ax.text(30, 3.85, "validation push", fontsize=6.8, ha="left", va="bottom")
    ax.text(30, 2.75, "uniform uplift", fontsize=6.8, ha="left", va="top")

    fig.tight_layout()
    save(fig, "rtt-policy-comparison")


if __name__ == "__main__":
    main()
