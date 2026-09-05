#!/usr/bin/env python3
"""Chapter 33, "The repayment share, chosen": features delivered against the repayment share.

The chapter says sweeping the repayment share is one line and produces a curve with a broad
optimum: zero performs badly, ten percent captures under a third of what is available, and
anything from about twenty-five to forty percent lands within a tenth of the best value. This
figure runs that sweep from the pack, zero to fifty percent in steps of five, sixty periods,
otherwise the default Policy, and marks the peak and the twenty percent the chapter's table uses.

    uv run --group figures python build/figures/fig_repayment_sweep.py

Data: chapters.chapter_33_technical_debt.code.debt.run(Policy(repayment_share=s), periods=60)
with s in 0.00, 0.05, ..., 0.50, reading features_done at period sixty. The asserts pin the
sweep's values, including the table's 230.1 at zero and 319.0 at twenty percent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_33_technical_debt.code.debt import Policy, run  # noqa: E402

EXPECTED = [230.1, 250.3, 271.8, 294.7, 319.0, 345.0, 372.8, 377.1, 348.4, 319.6, 290.8]


def main():
    shares = [i / 20 for i in range(11)]
    totals = [run(Policy(repayment_share=s), periods=60)[-1].features_done for s in shares]
    assert [round(v, 1) for v in totals] == EXPECTED, totals
    peak = max(range(len(shares)), key=lambda i: totals[i])
    assert shares[peak] == 0.35 and round(totals[peak], 1) == 377.1, (shares[peak], totals[peak])
    assert round(totals[4], 1) == 319.0

    fig, ax = figure(height_in=2.3)
    ax.plot(shares, totals, color="black", linestyle=DASHES[0], marker="o", markersize=2.6,
            markerfacecolor="white", markeredgewidth=0.7)
    ax.plot([shares[peak]], [totals[peak]], color="black", marker="o", markersize=3.2)
    ax.axhline(totals[peak] * 0.9, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(-0.01, 0.51)
    ax.set_ylim(200, 400)
    ax.set_yticks([200, 250, 300, 350, 400])
    ax.set_xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5])
    ax.set_xticklabels(["0%", "10%", "20%", "30%", "40%", "50%"])
    ax.set_xlabel("repayment share of capacity")
    ax.set_ylabel("features by period 60")
    ax.annotate(f"peak {totals[peak]:.1f} at 35%", xy=(shares[peak], totals[peak]),
                xytext=(0.36, 392), fontsize=6.5, ha="left", va="center")
    ax.annotate(f"{totals[4]:.1f} at 20%, the table's row", xy=(0.2, totals[4]),
                xytext=(0.245, 290), fontsize=6.5, ha="left", va="center",
                arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    ax.annotate(f"{totals[0]:.1f} at zero", xy=(0.0, totals[0]), xytext=(0.03, 218),
                fontsize=6.5, ha="left", va="center")
    ax.text(0.01, totals[peak] * 0.9 + 3, "within a tenth of the peak", fontsize=6.2, ha="left",
            va="bottom", style="italic")

    save(fig, "repayment-sweep")


if __name__ == "__main__":
    main()
