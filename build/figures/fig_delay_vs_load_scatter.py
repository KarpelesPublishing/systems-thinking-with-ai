#!/usr/bin/env python3
"""Chapter 39, "The record read across airports": taxi-out and schedule delay against hourly load.

The chapter reads the 2023 record for the thirty busiest origin airports as one point per airport
and load bin (load is an hour's scheduled departures over the airport's p95 hourly count), and
finds that taxi-out, a proxy for runway queueing, rises from 15.9 minutes in the lowest bin to
20.9 at load 1.15 while departure delay against the schedule falls from 19.2 to 12.5 over the
same range.
This figure plots the airport-bin points from the committed record:

    uv run --group figures python build/figures/fig_delay_vs_load_scatter.py

Data: data/bts_ontime/airport_hour_load.csv through
chapters.chapter_39_congestion_curve.code.calibrate.read_hour_bins, 2023 rows with at least
2,000 flights in the bin, and the pooled flight-weighted bin means as a heavier line. The asserts
pin the pooled numbers the chapter prints before anything is drawn.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import DASHES, STYLE, save  # noqa: E402

from chapters.chapter_39_congestion_curve.code.calibrate import (  # noqa: E402
    FIT_YEAR,
    pooled_bins,
    read_hour_bins,
    rows_for_year,
)


def main():
    rows = [r for r in rows_for_year(read_hour_bins(), FIT_YEAR) if r["flights"] >= 2000]
    taxi = pooled_bins(rows_for_year(read_hour_bins(), FIT_YEAR))
    delay = pooled_bins(rows_for_year(read_hour_bins(), FIT_YEAR), "mean_dep_delay_minutes")
    taxi_by, delay_by = {b[0]: b[1] for b in taxi}, {b[0]: b[1] for b in delay}
    assert round(taxi_by[0.05], 1) == 15.9 and round(taxi_by[1.15], 1) == 20.9, taxi
    assert round(delay_by[0.05], 1) == 19.2 and round(delay_by[1.15], 1) == 12.5, delay

    plt.rcParams.update(STYLE)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(4.4, 3.4), sharex=True,
                                      gridspec_kw={"hspace": 0.12})
    x = [r["load_bin_low"] + 0.05 for r in rows]
    top.plot(x, [r["mean_taxi_out"] for r in rows], linestyle="none", marker="o",
             markersize=2.6, markerfacecolor="none", markeredgecolor="black", markeredgewidth=0.5)
    top.plot([b[0] for b in taxi], [b[1] for b in taxi], color="black", linestyle=DASHES[0],
             linewidth=1.3)
    top.set_ylabel("taxi-out, minutes")
    top.set_ylim(10, 32)
    top.set_yticks([10, 15, 20, 25, 30])
    top.text(0.20, 11.2, "pooled mean", fontsize=6.8, ha="left", va="center")

    bottom.plot(x, [r["mean_dep_delay_minutes"] for r in rows], linestyle="none", marker="o",
                markersize=2.6, markerfacecolor="none", markeredgecolor="black",
                markeredgewidth=0.5)
    bottom.plot([b[0] for b in delay], [b[1] for b in delay], color="black",
                linestyle=DASHES[0], linewidth=1.3)
    bottom.set_ylabel("departure delay, minutes")
    bottom.set_ylim(0, 32)
    bottom.set_yticks([0, 10, 20, 30])
    bottom.set_xlabel("hourly load, departures over the airport's p95 hour")
    bottom.set_xlim(0, 1.5)
    bottom.text(0.25, 4.0, "pooled mean", fontsize=6.8, ha="left", va="center")

    save(fig, "delay-vs-load-scatter")


if __name__ == "__main__":
    main()
