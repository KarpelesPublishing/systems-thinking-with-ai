#!/usr/bin/env python3
"""Chapter 39, "Fit and holdout": the fitted convex curve over the 2023 taxi-out bins.

The chapter fits taxi_out(load) = 16.79 + 3.09 * max(0, load - 0.0)^2 to fourteen pooled load
bins of the 2023 record, with a mean absolute error of 0.54 minutes, and exports the curve as
lookup points on the bin centers from 0.05 to 1.35. This figure draws the bins as hollow markers
and the lookup points joined by straight segments, with the domain ends marked:

    uv run --group figures python build/figures/fig_fitted_lookup_over_bins.py

Data: chapters.chapter_39_congestion_curve.code.calibrate.run_case() on the committed record.
The asserts pin the fitted parameters and the error the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_39_congestion_curve.code.calibrate import (  # noqa: E402
    FIT_YEAR,
    fit_curve,
    fitted_congestion_lookup,
    pooled_bins,
    read_hour_bins,
    rows_for_year,
)


def main():
    hours = read_hour_bins()
    bins = pooled_bins(rows_for_year(hours, FIT_YEAR))
    fit = fit_curve(bins)
    points = fitted_congestion_lookup(hours)
    assert fit["fitted"] == {"base": 16.79, "knee": 0.0, "curvature": 3.09}, fit
    assert round(fit["error"], 2) == 0.54, fit["error"]
    assert points[0][0] == 0.05 and points[-1][0] == 1.35 and len(points) == 14
    assert round(bins[-1][1], 1) == 19.4 and points[-1][1] == 22.422

    fig, ax = figure(height_in=2.5)
    ax.plot([b[0] for b in bins], [b[1] for b in bins], linestyle="none", marker="o",
            markersize=3.4, markerfacecolor="none", markeredgecolor="black", markeredgewidth=0.6)
    ax.plot([x for x, _ in points], [y for _, y in points], color="black", linestyle=DASHES[1])
    for x in (points[0][0], points[-1][0]):
        ax.axvline(x, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(-0.05, 1.5)
    ax.set_ylim(14, 24)
    ax.set_yticks([14, 16, 18, 20, 22, 24])
    ax.set_xlabel("hourly load, departures over the airport's p95 hour")
    ax.set_ylabel("taxi-out, minutes per departure")
    ax.text(0.62, 17.0, "2023 bin means", fontsize=6.8, ha="left", va="top")
    ax.text(1.0, 21.6, "fitted lookup", fontsize=6.8, ha="right", va="bottom")
    ax.text(1.37, 14.3, "domain\nend", fontsize=6.2, ha="left", va="bottom")
    ax.text(0.07, 23.6, "domain\nstart", fontsize=6.2, ha="left", va="top")
    ax.annotate("top bin 19.4,\ncurve 22.4", xy=(1.35, 19.37), xytext=(1.12, 15.2), fontsize=6.2,
                ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))

    save(fig, "fitted-lookup-over-bins")


if __name__ == "__main__":
    main()
