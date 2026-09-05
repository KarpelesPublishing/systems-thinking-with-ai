#!/usr/bin/env python3
"""Chapter 37, "Why a headcount target is the wrong instrument": heads against capability.

The chapter raises the target ten percent at month 0 and runs the fitted pipeline for
twenty-four months under four rules. Headcount ends within a few hundred of 159,700 thousand
under every rule; effective capability ends at 129,864 under the baseline, 130,302 under hire
harder, 132,548 under retain, and 143,217 under shorten ramp. This figure plots both stocks:

    uv run --group figures python build/figures/fig_capability_vs_headcount.py

Data: chapters.chapter_37_hiring_pipeline.code.calibrate (run, policies, headline). The top
panel is headcount under the baseline and hire-harder rules, the bottom panel is effective
capability under all four. The asserts pin the numbers the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import DASHES, STYLE, save  # noqa: E402

from chapters.chapter_37_hiring_pipeline.code import calibrate as pipeline  # noqa: E402

ORDER = ("baseline", "hire_harder", "retain", "shorten_ramp")
LABELS = {"baseline": "baseline", "hire_harder": "hire harder", "retain": "retain",
          "shorten_ramp": "shorten ramp"}


def main():
    settings = {p.name: p.settings for p in pipeline.policies()}
    runs = {name: pipeline.run(pipeline.TARGET_STEP, 24, settings[name]) for name in ORDER}
    heads = {n: runs[n].series["headcount"] for n in ORDER}
    caps = {n: runs[n].series["effective_capability"] for n in ORDER}

    assert [round(caps[n][24]) for n in ORDER] == [129864, 130302, 132548, 143217]
    assert [round(heads[n][24]) for n in ORDER] == [159721, 159933, 159730, 159736]
    assert round(heads["baseline"][0]) == 140568 and round(caps["baseline"][0]) == 126511

    plt.rcParams.update(STYLE)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(4.4, 3.4), sharex=True,
                                      gridspec_kw={"height_ratios": [1.0, 1.3], "hspace": 0.14})
    t = list(range(25))
    top.plot(t, [h / 1000 for h in heads["baseline"]], color="black", linestyle=DASHES[0])
    top.plot(t, [h / 1000 for h in heads["hire_harder"]], color="black", linestyle=DASHES[1])
    top.set_ylim(138, 168)
    top.set_yticks([140, 150, 160])
    top.set_ylabel("headcount, millions")
    top.text(13, heads["baseline"][13] / 1000 - 3.2, "baseline", fontsize=6.6, ha="center",
             va="top")
    top.text(8, heads["hire_harder"][8] / 1000 - 1.6, "hire harder", fontsize=6.6,
             ha="center", va="top")
    top.axhline(pipeline.bounds()[0].high / 1000, color="black", linewidth=0.4,
                linestyle=DASHES[2])
    top.text(23.5, pipeline.bounds()[0].high / 1000 + 0.8, "payroll ceiling", fontsize=6.2,
             ha="right", va="bottom")

    for i, name in enumerate(ORDER):
        bottom.plot(t, [c / 1000 for c in caps[name]], color="black", linestyle=DASHES[i])
    bottom.set_ylim(122, 148)
    bottom.set_yticks([125, 130, 135, 140, 145])
    bottom.set_xlim(0, 24)
    bottom.set_xticks([0, 6, 12, 18, 24])
    bottom.set_xlabel("months after the target rises ten percent")
    bottom.set_ylabel("effective capability, millions")
    bottom.text(24.3, caps["shorten_ramp"][24] / 1000, LABELS["shorten_ramp"], fontsize=6.4,
                ha="left", va="center")
    bottom.text(24.3, caps["retain"][24] / 1000 + 0.6, LABELS["retain"], fontsize=6.4,
                ha="left", va="center")
    bottom.text(24.3, caps["hire_harder"][24] / 1000 - 0.9, LABELS["hire_harder"], fontsize=6.4,
                ha="left", va="center")
    bottom.text(24.3, caps["baseline"][24] / 1000 - 2.4, LABELS["baseline"], fontsize=6.4,
                ha="left", va="center")
    bottom.axhline(caps["baseline"][0] / 1000, color="black", linewidth=0.4, linestyle=DASHES[2])
    bottom.text(12, caps["baseline"][0] / 1000 - 0.5, "capability at month 0", fontsize=6.2,
                ha="center", va="top")
    fig.subplots_adjust(right=0.80)
    save(fig, "capability-vs-headcount")


if __name__ == "__main__":
    main()
