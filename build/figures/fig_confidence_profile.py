#!/usr/bin/env python3
"""Chapter 40, "Reading the confidence profile": claim counts by evidence level for the pass.

The chapter reproduces the profile after the training ramp was measured: six claims observed,
two inferred, eleven assumed, two proposed and excluded from the model, twenty-one in all, and
names the weakest claim the recommendation depends on, churn sensitivity, which is assumed.
This figure draws the four counts as hatched bars with the chapter's examples beside them.

    uv run --group figures python build/figures/fig_confidence_profile.py

Data: the counts and examples in the chapter's table. The chapter shows no code that produces
the profile, so the values are transcribed and the asserts check the transcription: the counts
sum to twenty-one and the assumed row dominates, which is the chapter's point.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402

PROFILE = [
    ("observed", 6,
     "customers, workforce, tenure, churn last 4 quarters,\nintake cap, capacity ramp (measured)"),
    ("inferred", 2, "attrition rate, referral rate"),
    ("assumed", 11,
     "churn sensitivity to quality, quality response to load,\ntraining cost, and eight others"),
    ("proposed", 2, "morale link, competitor response, both outside the model"),
]
HATCH = {"observed": "xxxx", "inferred": "////", "assumed": "", "proposed": "...."}


def main():
    counts = {level: n for level, n, _ in PROFILE}
    assert sum(counts.values()) == 21, counts
    assert counts["assumed"] == 11 and counts["assumed"] > sum(
        v for k, v in counts.items() if k != "assumed"), counts
    assert counts["observed"] == 6 and counts["inferred"] == 2 and counts["proposed"] == 2

    fig, ax = figure(height_in=2.3)
    ys = list(range(len(PROFILE)))[::-1]
    for y, (level, n, examples) in zip(ys, PROFILE):
        ax.barh(y, n, height=0.62, facecolor="white", edgecolor="black", linewidth=0.7,
                hatch=HATCH[level])
        ax.text(n + 0.3, y, f"{n}", ha="left", va="center", fontsize=7)
        ax.text(n + 1.3, y, examples, ha="left", va="center", fontsize=5.6, style="italic")
    ax.set_yticks(ys)
    ax.set_yticklabels([level for level, _, _ in PROFILE])
    ax.set_xlim(0, 26)
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel("claims, of 21")
    ax.text(25.8, ys[2] - 0.5, "weakest claim in the chain: churn sensitivity, assumed",
            ha="right", va="top", fontsize=6.0)
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="y", length=0)

    save(fig, "confidence-profile")


if __name__ == "__main__":
    main()
