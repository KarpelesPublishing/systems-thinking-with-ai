#!/usr/bin/env python3
"""Chapter 38, "Capacity Arrives When the Price Has Gone": the utilization record, 1972 to 2026.

The chapter reads the Federal Reserve G.17 manufacturing capacity utilization series and finds,
on the 1990-01 to 2019-12 window, a dominant period of ninety months and a detrended
peak-to-trough amplitude of eighteen points, with the window's high at 84.7 in December 1994
and its low at 63.5 in June 2009. This figure plots the committed record and marks the fit window
and the holdout window:

    uv run --group figures python build/figures/fig_utilisation_record.py

Data: data/fred_capacity/capacity_monthly.csv, column utilization, through
chapters.chapter_38_capacity_cycle.code.calibrate. The asserts pin the numbers the chapter prints.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_38_capacity_cycle.code import calibrate as c  # noqa: E402


def main():
    with c.RECORD.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    years = [int(r["period"][:4]) + (int(r["period"][5:7]) - 1) / 12 for r in rows]
    values = [float(r["utilization"]) for r in rows]
    record = list(c.record().values)

    # The numbers the chapter prints.
    assert c.cycle_period(record) == 90
    assert round(c.amplitude(record), 1) == 18.0
    assert (round(max(record), 1), round(min(record), 1)) == (84.7, 63.5)
    assert rows[0]["period"] == "1972-01-01"
    assert c.cycle_period(list(c.holdout_record().values)) == 64

    fig, ax = figure(height_in=2.4)
    ax.plot(years, values, color="black", linestyle=DASHES[0], linewidth=0.9)
    ax.axvspan(1990.0, 2020.0, facecolor="black", alpha=0.06, linewidth=0)
    ax.set_xlim(1972, 2027)
    ax.set_ylim(60, 92)
    ax.set_yticks([60, 70, 80, 90])
    ax.set_xticks([1975, 1985, 1995, 2005, 2015, 2025])
    ax.set_ylabel("utilization, percent")
    ax.set_xlabel("year")
    ax.text(1981.0, 90.0, "holdout 1972 to 1989", ha="center", va="center", fontsize=6.6)
    ax.text(2005.0, 90.0, "fit window 1990 to 2019", ha="center", va="center", fontsize=6.6)
    ax.annotate("84.7, Dec 1994", xy=(1994.92, 84.7), xytext=(1996.5, 87.4), fontsize=6.3,
                ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    ax.annotate("63.5, Jun 2009", xy=(2009.42, 63.5), xytext=(2010.8, 62.2), fontsize=6.3,
                ha="left", va="center")
    fig.tight_layout()
    save(fig, "utilisation-record")


if __name__ == "__main__":
    main()
