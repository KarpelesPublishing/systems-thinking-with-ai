#!/usr/bin/env python3
"""Chapter 37, "The record month by month": JOLTS hires against the fitted pipeline, 2015 to 2019.

The chapter fits three knobs (target growth, base quit rate, ramp time) to hires and quits over
January 2015 to December 2019 and reports a mean absolute percentage error of 2.4 percent on
hires. This figure plots the record and the fitted model over the fit window:

    uv run --group figures python build/figures/fig_jolts_hires_vs_model.py

Data: data/bls_jolts/jolts_monthly.csv through chapters.chapter_37_hiring_pipeline.code.calibrate
(record, fitted_path, fit). The asserts pin the numbers the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_37_hiring_pipeline.code import calibrate as pipeline  # noqa: E402


def main():
    fit = pipeline.fit()
    record = pipeline.record()["hires"]
    path = pipeline.fitted_path()
    months = list(range(60))
    observed = [record.values[m] for m in months]
    model = [path.series["hires"][m] for m in months]

    assert round(fit.per_target["hires"], 3) == 0.024, fit.per_target
    assert observed[0] == 5061.0 and observed[59] == 5951.0
    assert round(model[0]) == 4639 and round(model[59]) == 5868

    fig, ax = figure(height_in=2.4)
    ax.plot(months, observed, color="black", linestyle=DASHES[0])
    ax.plot(months, model, color="black", linestyle=DASHES[1])
    ax.set_xlim(0, 59)
    ax.set_ylim(4400, 6200)
    ax.set_yticks([4500, 5000, 5500, 6000])
    ax.set_xticks([0, 12, 24, 36, 48, 59])
    ax.set_xticklabels(["Jan 2015", "2016", "2017", "2018", "2019", "Dec 2019"])
    ax.set_ylabel("hires, thousands per month")
    ax.text(9, 5640, "JOLTS hires, seasonally adjusted", fontsize=6.8, ha="left", va="bottom")
    ax.text(44, 5330, "fitted model, error 2.4 percent", fontsize=6.8, ha="center", va="top")
    ax.annotate(f"{model[0]:,.0f}", xy=(0, model[0]), xytext=(2.5, 4560), fontsize=6.5,
                ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    ax.annotate(f"{observed[59]:,.0f}", xy=(59, observed[59]), xytext=(50, 6080), fontsize=6.5,
                ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    fig.tight_layout()
    save(fig, "jolts-hires-vs-model")


if __name__ == "__main__":
    main()
