#!/usr/bin/env python3
"""Chapter 6, "One clinic, two sketches": the same clinic as an aggregate and as a queue.

The chapter runs the clinic twice. As an aggregate stock and flow, nine arrivals an hour against a
capacity of ten for two hundred hours, the queue never forms and the mean wait is zero. As
individual patients on ten servers with the same averages, seed 11, 1786 patients pass through
and the wait summary is mean 0.54, median 0.21, p90 1.62, p99 2.18, worst 2.38 hours. The left
panel is the aggregate queue over time (flat at zero); the right panel is the queue sketch's
sorted individual waits with the p90 and p99 marked:

    uv run --group figures python build/figures/fig_two_sketches.py

Data: run_aggregate([9.0] * 200, capacity=10.0) and mean_wait(path, 10.0) from
chapters.chapter_06_two_sketches.code.aggregate; run_queue(arrivals_per_period=9.0, servers=10,
service_time=1.0, periods=200, seed=11) and wait_summary(waits) from the same pack's queueing
module. The asserts pin the printed numbers. The sorted-wait presentation is layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, grid_figure, save  # noqa: E402

from chapters.chapter_06_two_sketches.code.aggregate import mean_wait, run_aggregate  # noqa: E402
from chapters.chapter_06_two_sketches.code.queueing import run_queue, wait_summary  # noqa: E402


def main():
    path = run_aggregate([9.0] * 200, capacity=10.0)
    waits = run_queue(arrivals_per_period=9.0, servers=10, service_time=1.0, periods=200,
                      seed=11)
    summary = wait_summary(waits)

    assert max(path) == 0.0 and mean_wait(path, 10.0) == 0.0
    assert len(waits) == 1786, len(waits)
    assert {k: round(v, 2) for k, v in summary.items()} == {
        "mean": 0.54, "median": 0.21, "p90": 1.62, "p99": 2.18, "worst": 2.38}, summary

    fig, (left, right) = grid_figure(1, 2, height_in=2.3)

    left.plot(range(1, len(path) + 1), path, color="black", linestyle=DASHES[0])
    left.set_xlim(0, 200)
    left.set_ylim(-0.1, 2.6)
    left.set_yticks([0, 1, 2])
    left.set_xlabel("hour")
    left.set_ylabel("patients waiting")
    left.set_title("aggregate sketch", fontsize=7.5, pad=2)
    left.text(100, 0.18, "queue never forms, mean wait 0", fontsize=6.4, ha="center",
              va="bottom")

    ordered = sorted(waits)
    share = [100.0 * (i + 1) / len(ordered) for i in range(len(ordered))]
    right.plot(share, ordered, color="black", linestyle=DASHES[0])
    for key, label, dy in (("p90", "p90: 1.62 h", 0.05), ("p99", "p99: 2.18 h", 0.05)):
        pct = float(key[1:])
        right.plot([pct, pct], [0, summary[key]], color="black", linewidth=0.5,
                   linestyle=DASHES[2])
        right.plot([pct], [summary[key]], color="black", marker="o", markersize=2.8,
                   markerfacecolor="white")
    right.text(88, summary["p90"] + 0.06, "p90: 1.62 h", fontsize=6.3, ha="right", va="bottom")
    right.text(97, summary["p99"] + 0.06, "p99: 2.18 h", fontsize=6.3, ha="right", va="bottom")
    right.text(4, 0.62, "mean 0.54 h", fontsize=6.3, ha="left", va="bottom")
    right.axhline(summary["mean"], color="black", linewidth=0.4, linestyle=DASHES[1])
    right.set_xlim(0, 100)
    right.set_ylim(-0.1, 2.6)
    right.set_yticks([0, 1, 2])
    right.set_xlabel("share of 1786 patients (percent)")
    right.set_ylabel("wait (hours)")
    right.set_title("queue sketch", fontsize=7.5, pad=2)

    fig.tight_layout(w_pad=1.0)
    save(fig, "two-sketches")


if __name__ == "__main__":
    main()
