#!/usr/bin/env python3
"""Chapter 39, "The headline table": peak-hour queue delay against movements lost, per policy.

The chapter compares no_cap, cap_at_p95, and cap_at_p90 across forty uncertainty draws and
reports mean peak-hour queue delay of 4.62, 3.97, and 3.38 minutes per departure against
movements lost (cap plus cancellations) of 1.3, 2.3, and 3.8 percent. This figure places the
three policies on those two axes, with the no_cap spread across draws as a vertical bar:

    uv run --group figures python build/figures/fig_cap_tradeoff.py

Data: chapters.chapter_39_congestion_curve.code.calibrate.run_case()["policies"]. The asserts
pin the table the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_39_congestion_curve.code.calibrate import run_case  # noqa: E402


def main():
    table = run_case()["policies"]
    delay = {p: table[p]["realized_delay"]["mean"] for p in table}
    lost = {p: 100 * table[p]["movements_lost_share"]["mean"] for p in table}
    assert [round(delay[p], 2) for p in ("no_cap", "cap_at_p95", "cap_at_p90")] == \
        [4.62, 3.97, 3.38], delay
    assert [round(lost[p], 1) for p in ("no_cap", "cap_at_p95", "cap_at_p90")] == \
        [1.3, 2.3, 3.8], lost
    spread = table["no_cap"]["realized_delay"]
    low, high = spread["worst"], spread["best"]
    assert (round(low, 2), round(high, 2)) == (3.98, 5.29)

    fig, ax = figure(height_in=2.4)
    order = ("no_cap", "cap_at_p95", "cap_at_p90")
    ax.plot([lost[p] for p in order], [delay[p] for p in order], color="black",
            linestyle=DASHES[2], linewidth=0.7)
    ax.plot([lost[p] for p in order], [delay[p] for p in order], linestyle="none", marker="o",
            markersize=4.0, markerfacecolor="none", markeredgecolor="black", markeredgewidth=0.7)
    ax.plot([lost["no_cap"], lost["no_cap"]], [low, high], color="black", linewidth=0.7)
    labels = {"no_cap": "no cap", "cap_at_p95": "cap at p95", "cap_at_p90": "cap at p90"}
    offsets = {"no_cap": (0.15, 0.0), "cap_at_p95": (0.15, 0.08), "cap_at_p90": (0.15, 0.08)}
    for p in order:
        dx, dy = offsets[p]
        ax.text(lost[p] + dx, delay[p] + dy, labels[p], fontsize=6.8, ha="left", va="bottom")
    ax.text(lost["no_cap"] + 0.15, high, "spread across 40 draws", fontsize=6.2, ha="left",
            va="center")
    ax.set_xlim(0, 5)
    ax.set_ylim(2.5, 6)
    ax.set_yticks([3, 4, 5, 6])
    ax.set_xlabel("movements lost, percent of scheduled departures")
    ax.set_ylabel("peak-hour queue delay,\nminutes per departure")

    save(fig, "cap-tradeoff")


if __name__ == "__main__":
    main()
