#!/usr/bin/env python3
"""Chapter 34, "What the staffing loop does, and does not, add": the staffing path, two policies.

The chapter says staffing ends lower under shortest first, averaging 17.7 over the last twenty
periods against 21.3 under first come, first served, and that under both it swings between
roughly eight and roughly twenty-nine without ever settling, because the rule sets its target as
a multiple of current staffing and has no level to return to. This figure plots the staff path
the pack returns for both policies over the sixty-period run.

    uv run --group figures python build/figures/fig_staffing_oscillation.py

Data: chapters.chapter_34_hospital_hybrid.code.hospital.run(StaffingPolicy(priority=p))["staff"]
for p in "fifo" and "shortest_first", default arrivals, groups, and seed. The pack has no switch
that removes the staffing loop and returns no queue path, so the two curves are the two
policies' staffing, which is what the chapter's numbers describe. The asserts pin the last-twenty
averages and the swing.
"""
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_34_hospital_hybrid.code.hospital import StaffingPolicy, run  # noqa: E402


def main():
    fifo = run(StaffingPolicy(priority="fifo"))["staff"]
    shortest = run(StaffingPolicy(priority="shortest_first"))["staff"]
    late_fifo = statistics.fmean(fifo[-20:])
    late_shortest = statistics.fmean(shortest[-20:])

    # The numbers the chapter prints.
    assert round(late_fifo, 1) == 21.3, late_fifo
    assert round(late_shortest, 1) == 17.7, late_shortest
    for path in (fifo, shortest):
        assert 8.0 <= min(path) < 9.0 and 28.5 <= max(path) <= 29.5, (min(path), max(path))

    fig, ax = figure(height_in=2.4)
    t = list(range(1, len(fifo) + 1))
    ax.plot(t, fifo, color="black", linestyle=DASHES[0])
    ax.plot(t, shortest, color="black", linestyle=DASHES[1])
    ax.axhline(30, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 33)
    ax.set_yticks([0, 10, 20, 30])
    ax.set_xlabel("period")
    ax.set_ylabel("staff")
    ax.text(59.5, 30.4, "max staff 30", fontsize=6.2, ha="right", va="bottom", style="italic")
    leader = dict(arrowstyle="-", linewidth=0.5, color="black")
    ax.annotate("first come, first served", xy=(35, fifo[34]), xytext=(38, 5.0), fontsize=6.8,
                ha="left", va="center", arrowprops=leader)
    ax.annotate("shortest first", xy=(25, shortest[24]), xytext=(12, 5.0), fontsize=6.8,
                ha="left", va="center", arrowprops=leader)
    ax.text(1.5, 31.8, f"last twenty periods: {late_fifo:.1f} against {late_shortest:.1f}",
            fontsize=6.5, ha="left", va="top")

    save(fig, "staffing-oscillation")


if __name__ == "__main__":
    main()
