#!/usr/bin/env python3
"""Chapter 5, "The fix, and why nobody finds it" and "Running it": factory amplification.

The chapter prints the factory's order swing relative to the customer's under four pipeline
delays with the supply line ignored: one week of delay gives 14.1, two gives 34.3, three gives
63.2, and four gives 101.0. It then counts the supply line at the default two weeks and the
factory's swing falls to 18.6. This figure plots the sweep and marks the counted case beside the
default it corrects:

    uv run --group figures python build/figures/fig_supply_line_fix.py

Data: run_chain([4.0] * 5 + [8.0] * 45, ChainParameters(pipeline_weeks=w)) for w in 1..4 with
supply_line_weight=0.0, and ChainParameters(supply_line_weight=1.0) at pipeline_weeks=2, from
chapters.chapter_05_beer_game.code.chain, each reduced by amplification_ratio(demand, factory
orders). The asserts pin the five printed numbers. Marker choice and label placement are layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_05_beer_game.code.amplification import amplification_ratio  # noqa: E402
from chapters.chapter_05_beer_game.code.chain import run_chain  # noqa: E402
from chapters.chapter_05_beer_game.code.models import ChainParameters  # noqa: E402


def factory_swing(demand, parameters):
    history = run_chain(demand, parameters)
    return amplification_ratio(demand, [week[3] for week in history["orders"]])


def main():
    demand = [4.0] * 5 + [8.0] * 45
    weeks = [1, 2, 3, 4]
    ignored = [factory_swing(demand, ChainParameters(pipeline_weeks=w, supply_line_weight=0.0))
               for w in weeks]
    counted = factory_swing(demand, ChainParameters(pipeline_weeks=2, supply_line_weight=1.0))

    assert [round(v, 1) for v in ignored] == [14.1, 34.3, 63.2, 101.0], ignored
    assert round(counted, 1) == 18.6, counted

    fig, ax = figure(height_in=2.5)
    ax.plot(weeks, ignored, color="black", linestyle=DASHES[0], marker="o", markersize=3.2,
            markerfacecolor="black")
    ax.plot([2], [counted], color="black", marker="s", markersize=3.6, markerfacecolor="white",
            linestyle="none")
    ax.plot([2, 2], [counted, ignored[1]], color="black", linewidth=0.5, linestyle=DASHES[2])
    for w, v in zip(weeks, ignored, strict=True):
        ax.annotate(f"{v:.1f}", xy=(w, v), xytext=(-6, 4), textcoords="offset points",
                    fontsize=6.4, ha="right", va="bottom")
    ax.annotate(f"{counted:.1f}", xy=(2, counted), xytext=(7, -2), textcoords="offset points",
                fontsize=6.4, ha="left", va="top")
    ax.text(2.55, 12, "supply line counted,\ntwo weeks of delay", fontsize=6.4, ha="left",
            va="bottom")
    ax.annotate("", xy=(2.12, counted), xytext=(2.55, 18),
                arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    ax.text(1.05, 60, "supply line ignored", fontsize=6.8, ha="left", va="bottom")
    ax.set_xlim(0.7, 4.3)
    ax.set_xticks(weeks)
    ax.set_ylim(0, 112)
    ax.set_yticks([0, 25, 50, 75, 100])
    ax.set_xlabel("weeks of delay in each direction")
    ax.set_ylabel("factory swing, times the customer's")
    fig.tight_layout()
    save(fig, "supply-line-fix")


if __name__ == "__main__":
    main()
