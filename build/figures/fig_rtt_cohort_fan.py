#!/usr/bin/env python3
"""Chapter 36, "Elective Backlogs as a Stock": the waiting-time bands of the RTT list as a fan.

The chapter reads the list as an aging chain: pathways enter at zero weeks and move through the
bands the return reports. This figure draws the record's own bands, cumulative from the top, so
the vertical distance between two lines is the count in that band: under 18 weeks, 18 to 52
weeks, and over 52 weeks, from April 2016 to June 2026.

    uv run --group figures python build/figures/fig_rtt_cohort_fan.py

Data: `data/nhs_rtt/rtt_national_monthly.csv` (NHS England, Open Government Licence v3.0),
read through the chapter pack. No model output. The asserts pin the record values the chapter
quotes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_36_elective_backlog.code.calibrate import months_between  # noqa: E402
from chapters.chapter_36_elective_backlog.code.model import read_record  # noqa: E402

START = "2016-04"


def main():
    rows = [r for r in read_record() if r["period"] >= START]
    t = [months_between(START, r["period"]) for r in rows]
    total = [float(r["total_incomplete"]) / 1e6 for r in rows]
    over18 = [float(r["over_18_weeks"]) / 1e6 for r in rows]
    over52 = [float(r["over_52_weeks"]) / 1e6 for r in rows]
    by = {r["period"]: r for r in rows}

    # The numbers the chapter prints.
    assert by["2016-04"]["total_incomplete"] == "3603606"
    assert by["2016-04"]["over_52_weeks"] == "886"
    assert by["2021-03"]["over_52_weeks"] == "436127"
    assert by["2023-08"]["total_incomplete"] == "7745784"  # the list's peak
    assert by["2023-09"]["total_incomplete"] == "7744585"
    assert by["2026-06"]["total_incomplete"] == "7147562"
    assert by["2026-06"]["over_52_weeks"] == "103318"

    fig, ax = figure(height_in=2.7)
    ax.plot(t, total, color="black", linestyle=DASHES[0])
    ax.plot(t, over18, color="black", linestyle=DASHES[1])
    ax.plot(t, over52, color="black", linestyle=DASHES[2])
    ax.fill_between(t, over18, total, facecolor="white", hatch="..", edgecolor="black",
                    linewidth=0.0)
    ax.fill_between(t, over52, over18, facecolor="white", hatch="//", edgecolor="black",
                    linewidth=0.0)
    ax.set_ylim(0, 8.3)
    ax.set_yticks([0, 2, 4, 6, 8])
    ax.set_ylabel("incomplete pathways, millions")
    years = list(range(2016, 2027, 2))
    ax.set_xlim(0, 123)
    ax.set_xticks([months_between(START, f"{y}-01") for y in years])
    ax.set_xticklabels([str(y) for y in years])
    ax.set_xlabel("month end")
    ax.text(100, 5.6, "under 18 weeks", fontsize=6.8, ha="center", va="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.text(100, 1.6, "18 to 52 weeks", fontsize=6.8, ha="center", va="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("over 52 weeks, peak 436 thousand", xy=(59, 0.44), xytext=(4, 1.15),
                fontsize=6.5, ha="left", va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
                arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    ax.text(2, 8.1, "3.6 million in April 2016, peaking at 7.7 million in August 2023",
            fontsize=6.5, ha="left", va="top",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    fig.tight_layout()
    save(fig, "rtt-cohort-fan")


if __name__ == "__main__":
    main()
