#!/usr/bin/env python3
"""Chapter 4, "Reading the graph, slowly": rates above, level below, on the five-minute tub.

The chapter's table starts a tub at fifty litres, runs an inflow of 10, 9, 8, 7, 6 litres per
minute against a steady outflow of 4, and prints the level at the end of each minute: 56, 61, 65,
68, 70. The inflow falls every minute and the level rises every minute. This figure puts the two
rates in the top panel and the level in the bottom one so the two readings sit on one page:

    uv run --group figures python build/figures/fig_level_vs_rate.py

Data: chapters.chapter_04_stock_and_flow.code.stock.integrate(50.0, [10, 9, 8, 7, 6], [4] * 5),
which returns the path the chapter prints, [50.0, 56.0, 61.0, 65.0, 68.0, 70.0]. Rates are drawn
as steps because each holds for a whole minute; the level is drawn as a line through the minute
ends. The asserts pin the printed path and the twenty litres gained. Panel heights are layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import DASHES, STYLE, save  # noqa: E402

from chapters.chapter_04_stock_and_flow.code.stock import integrate  # noqa: E402


def main():
    inflow = [10.0, 9.0, 8.0, 7.0, 6.0]
    outflow = [4.0] * 5
    level = integrate(50.0, inflow, outflow)
    net = [i - o for i, o in zip(inflow, outflow, strict=True)]

    assert level == [50.0, 56.0, 61.0, 65.0, 68.0, 70.0], level
    assert net == [6.0, 5.0, 4.0, 3.0, 2.0], net
    assert level[-1] - level[0] == 20.0

    plt.rcParams.update(STYLE)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(4.4, 3.1), sharex=True,
                                      gridspec_kw={"height_ratios": [1.0, 1.0], "hspace": 0.15})
    edges = list(range(6))
    top.stairs(inflow, edges, baseline=None, color="black", linestyle=DASHES[0])
    top.stairs(outflow, edges, baseline=None, color="black", linestyle=DASHES[1])
    top.stairs(net, edges, baseline=None, color="black", linestyle=DASHES[2])
    top.set_ylim(0, 12)
    top.set_yticks([0, 4, 8, 12])
    top.set_ylabel("litres per minute")
    top.text(0.15, 10.45, "inflow", fontsize=6.8, ha="left", va="bottom")
    top.text(0.15, 4.4, "outflow", fontsize=6.8, ha="left", va="bottom")
    top.text(1.15, 5.3, "net", fontsize=6.8, ha="left", va="bottom")

    minutes = list(range(6))
    bottom.plot(minutes, level, color="black", linestyle=DASHES[0], marker="o", markersize=2.6,
                markerfacecolor="black")
    for m, v in zip(minutes[1:], level[1:], strict=True):
        bottom.annotate(f"{v:.0f}", xy=(m, v), xytext=(0, -9), textcoords="offset points",
                        fontsize=6.3, ha="center", va="top")
    bottom.set_ylim(45, 75)
    bottom.set_yticks([50, 60, 70])
    bottom.set_ylabel("litres in the tub")
    bottom.set_xlabel("minute")
    bottom.set_xlim(0, 5)
    bottom.set_xticks(minutes)
    bottom.text(0.15, 67.5, "level rises while the net rate falls", fontsize=6.6, ha="left",
                va="bottom", style="italic")

    save(fig, "level-vs-rate")


if __name__ == "__main__":
    main()
