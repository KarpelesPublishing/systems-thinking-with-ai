#!/usr/bin/env python3
"""Chapter 17, "Three curves, read together": headcount, capacity, and junior experience
over a three-quarter hiring surge.

The chapter starts from bands of 20, 30, and 50 people holding 40, 150, and 500 person-years,
runs three quarters at 40 hires per quarter, and prints headcount 100 to 193, effective
capacity (four-year ramp) 90 to 135, and the junior band's average experience 2.00 to 1.45
years. This figure plots the three series as three panels on one time axis.

    uv run --group figures python build/figures/fig_three_curves.py

Data: chapters.chapter_17_cohorts.code.cohorts.advance(bands, hires=40.0,
maturation=[0.25, 0.2, 0.0], attrition=[0.10, 0.06, 0.04]) three times from the chapter's
starting bands (the rates are the pack test's POLICY, which the chapter's numbers come from),
then headcount, effective_capacity(bands, 4.0), and bands[0].average(). The asserts pin the
chapter's numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import STYLE, save  # noqa: E402

from chapters.chapter_17_cohorts.code.cohorts import (  # noqa: E402
    Band,
    advance,
    effective_capacity,
    headcount,
)

START = [Band(people=20, experience=40.0), Band(people=30, experience=150.0),
         Band(people=50, experience=500.0)]
POLICY = {"maturation": [0.25, 0.2, 0.0], "attrition": [0.10, 0.06, 0.04]}


def main():
    bands = START
    heads, capacity, junior = [], [], []
    for _ in range(4):
        heads.append(headcount(bands))
        capacity.append(effective_capacity(bands, 4.0))
        junior.append(bands[0].average())
        bands = advance(bands, hires=40.0, **POLICY)
    assert (round(heads[0]), round(heads[3])) == (100, 193), heads
    assert (round(capacity[0]), round(capacity[3])) == (90, 135), capacity
    assert (round(junior[0], 2), round(junior[3], 2)) == (2.00, 1.45), junior
    # The caption names the dip, so it is pinned too: the surge halves the junior band's
    # average before the ramp brings it back.
    assert round(min(junior), 2) == 0.87, junior

    plt.rcParams.update(STYLE)
    fig, axes = plt.subplots(3, 1, figsize=(4.4, 3.2), sharex=True,
                             gridspec_kw={"hspace": 0.18})
    t = [0, 1, 2, 3]
    series = [(heads, "headcount", "people", (80, 210), [100, 150, 200], (0.03, 0.88)),
              (capacity, "effective capacity", "people", (80, 150), [90, 120, 150], (0.03, 0.88)),
              (junior, "junior average experience", "years", (0.5, 2.3), [1, 2], (0.03, 0.14))]
    for ax, (values, name, unit, lim, ticks, at) in zip(axes, series, strict=True):
        ax.plot(t, values, color="black", marker="o", markersize=2.5)
        ax.set_ylim(*lim)
        ax.set_yticks(ticks)
        ax.set_ylabel(unit)
        ax.text(*at, name, transform=ax.transAxes, fontsize=6.8, ha="left", va="top")
        fmt = "{:.2f}" if unit == "years" else "{:.0f}"
        below = unit != "years"
        ax.annotate(fmt.format(values[0]), xy=(0, values[0]),
                    xytext=(4, -3 if below else 3), textcoords="offset points", fontsize=6.3,
                    ha="left", va="top" if below else "bottom")
        ax.annotate(fmt.format(values[3]), xy=(3, values[3]), xytext=(-4, 3),
                    textcoords="offset points", fontsize=6.3, ha="right", va="bottom")
    axes[-1].set_xticks(t)
    axes[-1].set_xlabel("quarters of hiring at 40 per quarter")
    axes[-1].set_xlim(-0.15, 3.15)

    save(fig, "three-curves")


if __name__ == "__main__":
    main()
