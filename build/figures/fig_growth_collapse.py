#!/usr/bin/env python3
"""Chapter 32, "Reading the collapse": customers, quality, and load over eighty periods.

The chapter runs the service-growth model with Policy(intake_rate=0.25,
churn_sensitivity=1.2, hiring_aggression=0.10) for eighty periods and reads
the path aloud: a peak of a hundred and eighty-five and a half at period four, a trough of
ninety-two at period seven, a rally to a hundred and forty-six at period twelve, then peaks of
119, 101, 83, 68 and troughs of 80, 67, 54, 45, 37, ending at twenty-two by period eighty. This
figure plots exactly that run from the chapter pack:

    uv run --group figures python build/figures/fig_growth_collapse.py

Data: chapters.chapter_32_service_growth.code.growth.run(policy, periods=80) with that policy.
The top panel is customers, the bottom panel is quality and load on one axis. Direct labels
replace a legend. The asserts below pin the numbers the chapter prints; if a pack default
moves, this script fails before it draws.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import DASHES, STYLE, save  # noqa: E402

from chapters.chapter_32_service_growth.code.growth import Policy, load, run  # noqa: E402


def turning_points(values):
    peaks, troughs = [], []
    for i in range(1, len(values) - 1):
        if values[i] > values[i - 1] and values[i] >= values[i + 1]:
            peaks.append((i, values[i]))
        if values[i] < values[i - 1] and values[i] <= values[i + 1]:
            troughs.append((i, values[i]))
    return peaks, troughs


def main():
    policy = Policy(intake_rate=0.25, churn_sensitivity=1.2, hiring_aggression=0.10)
    path = run(policy, periods=80)
    customers = [s.customers for s in path]
    quality = [s.quality for s in path]
    loads = [load(s, policy) for s in path]
    peaks, troughs = turning_points(customers)

    # The numbers the chapter prints.
    assert round(customers[4], 1) == 185.5, customers[4]
    assert [round(v) for _, v in peaks[:6]] == [185, 146, 119, 101, 83, 68], peaks
    assert [round(v) for _, v in troughs[:6]] == [92, 80, 67, 54, 45, 37], troughs
    assert [i for i, _ in peaks[:2]] == [4, 12] and [i for i, _ in troughs[:2]] == [7, 16]
    assert round(customers[80], 1) == 22.3, customers[80]
    assert loads[0] < 1.0 < loads[1]

    plt.rcParams.update(STYLE)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(4.4, 3.1), sharex=True,
                                      gridspec_kw={"height_ratios": [1.35, 1.0], "hspace": 0.12})
    t = list(range(len(path)))
    top.plot(t, customers, color="black", linestyle=DASHES[0])
    top.set_ylabel("customers")
    top.set_ylim(0, 210)
    top.set_yticks([0, 50, 100, 150, 200])
    for i, v in peaks[:2]:
        top.annotate(f"{v:.0f}", xy=(i, v), xytext=(i + 1.5, v + 8), fontsize=6.5, ha="left")
    top.annotate(f"{customers[80]:.0f}", xy=(80, customers[80]), xytext=(74, 40), fontsize=6.5,
                 ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))

    bottom.plot(t, quality, color="black", linestyle=DASHES[0])
    bottom.plot(t, loads, color="black", linestyle=DASHES[1])
    bottom.axhline(1.0, color="black", linewidth=0.4, linestyle=DASHES[2])
    bottom.set_ylim(0, 2.6)
    bottom.set_yticks([0, 1, 2])
    bottom.set_xlabel("period")
    bottom.set_xlim(0, 80)
    bottom.text(26, quality[26] - 0.22, "quality", fontsize=6.8, ha="left", va="top")
    bottom.text(26, loads[26] + 0.18, "load", fontsize=6.8, ha="left", va="bottom")

    save(fig, "growth-collapse")


if __name__ == "__main__":
    main()
