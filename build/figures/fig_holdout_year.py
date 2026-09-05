#!/usr/bin/env python3
"""Chapter 39, "Fit and holdout": the 2023 lookup against the 2024 bins it never saw.

The chapter holds out 2024 and reports a mean absolute error of 0.64 minutes over fourteen bins,
all inside the fitted domain, with the top bin at 20.8 minutes against a curve value of 22.4.
This figure draws the 2024 bin means as hollow markers over the 2023 lookup:

    uv run --group figures python build/figures/fig_holdout_year.py

Data: chapters.chapter_39_congestion_curve.code.calibrate.holdout_error on the committed record.
The asserts pin the holdout numbers the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_39_congestion_curve.code.calibrate import (  # noqa: E402
    HOLDOUT_YEAR,
    fitted_congestion_lookup,
    holdout_error,
    read_hour_bins,
    rows_for_year,
)


def main():
    hours = read_hour_bins()
    points = fitted_congestion_lookup(hours)
    hold = holdout_error(points, rows_for_year(hours, HOLDOUT_YEAR))
    assert round(hold["mae"], 2) == 0.64, hold["mae"]
    assert hold["bins_inside"] == 14 and hold["bins_refused"] == 0
    assert round(hold["bins"][-1][1], 1) == 20.8 and round(hold["bins"][-2][1], 1) == 22.1

    fig, ax = figure(height_in=2.5)
    ax.plot([x for x, _ in points], [y for _, y in points], color="black", linestyle=DASHES[1])
    ax.plot([b[0] for b in hold["bins"]], [b[1] for b in hold["bins"]], linestyle="none",
            marker="s", markersize=3.2, markerfacecolor="none", markeredgecolor="black",
            markeredgewidth=0.6)
    ax.set_xlim(-0.05, 1.5)
    ax.set_ylim(14, 24)
    ax.set_yticks([14, 16, 18, 20, 22, 24])
    ax.set_xlabel("hourly load, departures over the airport's 2023 p95 hour")
    ax.set_ylabel("taxi-out, minutes per departure")
    ax.text(0.30, 19.0, "2024 bin means", fontsize=6.8, ha="left", va="bottom")
    ax.text(1.0, 18.9, "2023 lookup", fontsize=6.8, ha="left", va="top")
    ax.text(0.02, 23.4, f"holdout MAE {hold['mae']:.2f} min over {hold['bins_inside']} bins",
            fontsize=6.8, ha="left", va="top")

    save(fig, "holdout-year")


if __name__ == "__main__":
    main()
