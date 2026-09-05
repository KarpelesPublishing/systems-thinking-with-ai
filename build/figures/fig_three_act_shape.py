#!/usr/bin/env python3
"""Chapter 33, "The three-act shape": cumulative features under push hard and push with repayment.

The chapter's opening table runs two policies for sixty periods at the pack's default capacity of
ten: push hard, which is Policy(feature_pressure=1.0, repayment_share=0.0), and push with twenty
percent repaid, Policy(feature_pressure=1.0, repayment_share=0.2). It prints 100.1 features by
period twelve and 230.1 in total for push hard, 87.2 and 319.0 for the repaying policy, and says
the two paths cross at period twenty-six. This figure plots both cumulative paths from the pack
and marks the crossover and the period-twelve review.

    uv run --group figures python build/figures/fig_three_act_shape.py

Data: chapters.chapter_33_technical_debt.code.debt.run(policy, periods=60) for the two policies
above. The act boundaries are not drawn, since the chapter gives them as a narrative rather than
as periods. The asserts pin the printed numbers before anything is drawn.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_33_technical_debt.code.debt import Policy, run  # noqa: E402


def main():
    push = [s.features_done for s in run(Policy(feature_pressure=1.0, repayment_share=0.0), 60)]
    repay = [s.features_done for s in run(Policy(feature_pressure=1.0, repayment_share=0.2), 60)]
    crossover = next(t for t in range(1, 61) if repay[t] >= push[t])

    # The numbers the chapter prints.
    assert round(push[12], 1) == 100.1 and round(push[60], 1) == 230.1, (push[12], push[60])
    assert round(repay[12], 1) == 87.2 and round(repay[60], 1) == 319.0, (repay[12], repay[60])
    assert crossover == 26, crossover

    fig, ax = figure(height_in=2.4)
    t = list(range(61))
    ax.plot(t, push, color="black", linestyle=DASHES[0])
    ax.plot(t, repay, color="black", linestyle=DASHES[1])
    ax.axvline(crossover, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.axvline(12, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(0, 60)
    ax.set_ylim(0, 340)
    ax.set_yticks([0, 100, 200, 300])
    ax.set_xlabel("period")
    ax.set_ylabel("features delivered, cumulative")
    ax.text(12.8, 325, "review at 12", fontsize=6.5, ha="left", va="top")
    ax.text(26.8, 325, f"crossover at {crossover}", fontsize=6.5, ha="left", va="top")
    ax.text(45, push[45] - 14, "push hard", fontsize=6.8, ha="left", va="top")
    ax.text(40, repay[40] + 24, "push, repay 20%", fontsize=6.8, ha="right", va="bottom")
    ax.annotate(f"{push[60]:.1f}", xy=(60, push[60]), xytext=(60.8, push[60]), fontsize=6.5,
                ha="left", va="center", annotation_clip=False)
    ax.annotate(f"{repay[60]:.1f}", xy=(60, repay[60]), xytext=(60.8, repay[60]), fontsize=6.5,
                ha="left", va="center", annotation_clip=False)

    save(fig, "three-act-shape")


if __name__ == "__main__":
    main()
