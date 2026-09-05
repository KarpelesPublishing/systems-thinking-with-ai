#!/usr/bin/env python3
"""Chapter 37, "The record month by month": JOLTS quits, the fit window, and the holdout.

The pipeline is fitted on 2015 to 2019 and run on, with nothing in it that knows about 2020,
into a holdout of January 2022 to December 2024. The chapter reports a quits error of 3.1 percent
in the fit window and 10.7 percent in the holdout, with the model 20.5 percent under the record
in January 2022 and 20.1 percent over it in December 2024. This figure shows why:

    uv run --group figures python build/figures/fig_jolts_quits_holdout.py

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
    record = pipeline.record()["quits"]
    path = pipeline.fitted_path()
    months = list(range(120))
    observed = [record.values[m] for m in months]
    model = [path.series["quits"][m] for m in months]
    against = {r["month"]: r for r in pipeline.against_record("quits", (84, 119))}

    assert round(fit.per_target["quits"], 3) == 0.031, fit.per_target
    assert round(fit.holdout_error["quits"], 3) == 0.107, fit.holdout_error
    assert round(against[84]["error"], 3) == -0.205 and round(against[119]["error"], 3) == 0.201
    assert observed[84] == 4413.0 and observed[119] == 3085.0

    fig, ax = figure(height_in=2.5)
    ax.plot(months, observed, color="black", linestyle=DASHES[0])
    ax.plot(months, model, color="black", linestyle=DASHES[1])
    for x in (59.5, 83.5):
        ax.axvline(x, color="black", linewidth=0.5, linestyle=DASHES[2])
    ax.set_xlim(0, 119)
    ax.set_ylim(1700, 4700)
    ax.set_yticks([2000, 2500, 3000, 3500, 4000, 4500])
    ax.set_xticks([0, 24, 48, 72, 96, 119])
    ax.set_xticklabels(["2015", "2017", "2019", "2021", "2023", "2024"])
    ax.set_ylabel("quits, thousands per month")
    ax.text(29, 1850, "fit window, error 3.1 percent", fontsize=6.6, ha="center", va="center")
    ax.text(71.5, 1850, "not fitted", fontsize=6.6, ha="center", va="center")
    ax.text(101.5, 1850, "holdout, error 10.7 percent", fontsize=6.6, ha="center", va="center")
    ax.text(40, observed[40] - 330, "JOLTS quits", fontsize=6.8, ha="center", va="top")
    ax.text(112, model[112] + 120, "fitted model", fontsize=6.8, ha="center", va="bottom")
    ax.annotate(f"{observed[63]:,.0f}, April 2020", xy=(63, observed[63]),
                xytext=(67, 2300), fontsize=6.3, ha="left",
                arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    ax.annotate(f"{observed[84]:,.0f}, January 2022", xy=(84, observed[84]),
                xytext=(88, 4580), fontsize=6.3, ha="left",
                arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    fig.tight_layout()
    save(fig, "jolts-quits-holdout")


if __name__ == "__main__":
    main()
