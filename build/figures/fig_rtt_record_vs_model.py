#!/usr/bin/env python3
"""Chapter 36, "Elective Backlogs as a Stock": the RTT record against the fitted model.

The chapter fits a three-stock model to total incomplete pathways from April 2016 to December
2019, then runs the same document on to June 2026 and reports the holdout from April 2021. This
figure plots the record and that one run from the chapter pack:

    uv run --group figures python build/figures/fig_rtt_record_vs_model.py

Data: `data/nhs_rtt/rtt_national_monthly.csv` (NHS England, Open Government Licence v3.0) and
chapters.chapter_36_elective_backlog.code.calibrate.fitted_document(), run for the length of the
record. Top panel: total incomplete pathways, millions. Bottom panel: pathways over 52 weeks,
thousands. The fit window and the holdout window are marked by vertical rules. The asserts pin
the numbers the chapter prints; if the pack or the record moves, this script fails before it
draws.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import DASHES, STYLE, save  # noqa: E402

from chapters.chapter_36_elective_backlog.code import calibrate as c  # noqa: E402


def main():
    total, over = c.record()
    fitted = c.fitted_document()
    path = c.run(fitted, fitted.horizon)
    fit = c.fit()

    # The numbers the chapter prints.
    assert round(fit.per_target["total_incomplete"], 4) == 0.0363
    assert round(fit.holdout_error["total_incomplete"], 4) == 0.3557
    assert round(c.at_month(path, "total_incomplete", 44)) == 4206670
    assert round(c.at_month(path, "total_incomplete", 122)) == 4676007
    assert c.record_at("2019-12")["total_incomplete"] == 4414911
    assert c.record_at("2023-09")["total_incomplete"] == 7744585
    assert c.record_at("2021-03")["over_52_weeks"] == 436127

    fit_end = c.months_between(c.FIT_START, c.FIT_END)
    hold_start = c.months_between(c.FIT_START, c.HOLDOUT_START)
    years = list(range(2016, 2027, 2))
    ticks = [c.months_between(c.FIT_START, f"{y}-01") for y in years]

    plt.rcParams.update(STYLE)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(4.4, 3.4), sharex=True,
                                      gridspec_kw={"height_ratios": [1.3, 1.0], "hspace": 0.12})
    keep = [i for i, t in enumerate(total.times) if t >= 0]
    top.plot([total.times[i] for i in keep], [total.values[i] / 1e6 for i in keep],
             color="black", linestyle=DASHES[0])
    top.plot(path.times, [v / 1e6 for v in path.series["total_incomplete"]], color="black",
             linestyle=DASHES[1])
    top.set_ylabel("pathways, millions")
    top.set_ylim(3, 8.2)
    top.set_yticks([3, 4, 5, 6, 7, 8])
    for x in (fit_end, hold_start):
        top.axvline(x, color="black", linewidth=0.4, linestyle=DASHES[2])
        bottom.axvline(x, color="black", linewidth=0.4, linestyle=DASHES[2])
    top.text(2, 7.85, "fit window", fontsize=6.5, ha="left", va="top")
    top.text(hold_start + 2, 7.85, "holdout", fontsize=6.5, ha="left", va="top")
    top.text(72, 5.35, "record", fontsize=6.8, ha="left", va="top")
    top.text(90, 4.35, "fitted model", fontsize=6.8, ha="left", va="top")

    keep = [i for i, t in enumerate(over.times) if t >= 0]
    bottom.plot([over.times[i] for i in keep], [over.values[i] / 1e3 for i in keep],
                color="black", linestyle=DASHES[0])
    bottom.plot(path.times, [v / 1e3 for v in path.series["long_waiters"]], color="black",
                linestyle=DASHES[1])
    bottom.set_ylabel("over 52 weeks, thousands")
    bottom.set_ylim(0, 480)
    bottom.set_yticks([0, 200, 400])
    bottom.set_xlim(0, 123)
    bottom.set_xticks(ticks)
    bottom.set_xticklabels([str(y) for y in years])
    bottom.set_xlabel("month end")
    bottom.text(62, 430, "record: 436 thousand, March 2021", fontsize=6.5, ha="left",
                va="center")
    bottom.text(6, 40, "fitted model stays near zero", fontsize=6.5, ha="left", va="bottom")

    save(fig, "rtt-record-vs-model")


if __name__ == "__main__":
    main()
