#!/usr/bin/env python3
"""Chapter 18, "Exchange frequency is a modeling decision": staffing under two exchange rates.

The chapter runs the coupled model for sixty periods with seed 5, exchanging every period and
every eighth period, and reports staffing volatility of 1.01 against 4.75, with the fast run
inside a band from 7.9 to 13.2 and the slow run ranging from 6.6 to 27.7 around a baseline of
ten. This figure plots the two staffing paths with direct labels.

    uv run --group figures python build/figures/fig_exchange_frequency.py

Data: chapters.chapter_18_hybrid.code.coupling.run_coupled(periods=60,
interface=Interface(exchange_every=1), seed=5) and the same with exchange_every=8, reading
history["staff"]. Volatility is statistics.pstdev, as the pack test computes it. The asserts
pin the chapter's numbers. The chapter's code block uses seed 5, and so does this figure.
"""
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_18_hybrid.code.coupling import Interface, run_coupled  # noqa: E402


def main():
    fast = run_coupled(periods=60, interface=Interface(exchange_every=1), seed=5)["staff"]
    slow = run_coupled(periods=60, interface=Interface(exchange_every=8), seed=5)["staff"]
    assert round(statistics.pstdev(fast), 2) == 1.01, statistics.pstdev(fast)
    assert round(statistics.pstdev(slow), 2) == 4.75, statistics.pstdev(slow)
    assert (round(min(fast), 1), round(max(fast), 1)) == (7.9, 13.2), (min(fast), max(fast))
    assert (round(min(slow), 1), round(max(slow), 1)) == (6.6, 27.7), (min(slow), max(slow))

    t = list(range(1, 61))
    fig, ax = figure(height_in=2.5)
    ax.plot(t, slow, color="black", linestyle=DASHES[1])
    ax.plot(t, fast, color="black", linestyle=DASHES[0])
    ax.axhline(10.0, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 31)
    ax.set_yticks([0, 10, 20, 30])
    ax.set_xlabel("period")
    ax.set_ylabel("staff (clinicians)")
    peak = max(range(len(slow)), key=lambda i: slow[i])
    ax.text(peak + 1.5, slow[peak], f"exchange every 8 periods:\nvolatility "
            f"{statistics.pstdev(slow):.2f}, range {min(slow):.1f} to {max(slow):.1f}",
            fontsize=6.3, ha="left", va="center")
    ax.text(30, 15.2, f"every period: volatility {statistics.pstdev(fast):.2f}, "
            f"range {min(fast):.1f} to {max(fast):.1f}", fontsize=6.3, ha="left", va="bottom")
    ax.text(59, 9.5, "baseline 10", fontsize=6.0, ha="right", va="top", style="italic")

    fig.tight_layout()
    save(fig, "exchange-frequency")


if __name__ == "__main__":
    main()
