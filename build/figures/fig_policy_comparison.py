#!/usr/bin/env python3
"""Chapter 30, "Worst case, not average": three policies across the same twenty-five draws.

The chapter's table gives, for push, steady and hold, the mean final adopters (934.1, 911.9,
533.6) and the worst case (722.4, 705.5, 413.6), and says push and steady are excluded because
they breach a support capacity ceiling of 1100 in four of the twenty-five draws. This figure
draws each policy as a horizontal span from its worst draw to its best, a filled mark at the
mean and an open mark at the worst case, with the ceiling as a vertical dashed line the two
excluded policies cross.

    uv run --group figures python build/figures/fig_policy_comparison.py

Data: chapters.chapter_30_policy_search.code.policies.compare(bass, [push, steady, hold],
[Uncertainty("total_market", 700, 1300)], "adopters", [Bound("adopters", high=1100.0,
reason="support capacity ceiling")], draws=25, seed=7), the call tests/chapters/
test_agent_packs.py pins for the chapter, with push, steady and hold setting imitation to 0.55,
0.35 and 0.15. Means, worst cases, the ceiling, and the four breaches each of push and steady
are asserted before anything is drawn.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable  # noqa: E402
from chapters.chapter_29_experiments.code.sensitivity import Uncertainty  # noqa: E402
from chapters.chapter_30_policy_search.code.policies import Bound, Policy, compare  # noqa: E402

CEILING = 1100.0


def bass() -> ModelDocument:
    return ModelDocument("bass", "1.0.0", horizon=40, variables=[
        Variable("adopters", "stock", "people", value=1.0),
        Variable("total_market", "parameter", "people", value=1000.0),
        Variable("innovation", "parameter", "1/week", value=0.01),
        Variable("imitation", "parameter", "1/week", value=0.30),
        Variable("potential", "auxiliary", "people", "total_market - adopters"),
        Variable("adoption", "flow", "people/week",
                 "(innovation + imitation * adopters / total_market) * potential",
                 target="adopters", sign=1),
    ])


def main():
    policies = [
        Policy("push", {"imitation": 0.55}, "growth lead", reversible=True,
               note="referral program at full spend"),
        Policy("steady", {"imitation": 0.35}, "growth lead", reversible=True),
        Policy("hold", {"imitation": 0.15}, "growth lead", reversible=True),
    ]
    bounds = [Bound("adopters", high=CEILING, reason="support capacity ceiling")]
    evaluations = compare(bass(), policies, [Uncertainty("total_market", 700, 1300)],
                          "adopters", bounds, draws=25, seed=7)
    printed = {e.policy: (round(e.mean(), 1), round(e.worst(), 1)) for e in evaluations}
    assert printed == {"push": (934.1, 722.4), "steady": (911.9, 705.5),
                       "hold": (533.6, 413.6)}, printed
    assert [len(e.violations) for e in evaluations] == [4, 4, 0]
    assert [len(e.values) for e in evaluations] == [25, 25, 25]

    fig, ax = figure(height_in=2.0)
    ys = [2, 1, 0]
    for y, e in zip(ys, evaluations):
        ax.plot([e.worst(), max(e.values)], [y, y], color="black", linewidth=0.8)
        for x in (e.worst(), max(e.values)):
            ax.plot([x, x], [y - 0.1, y + 0.1], color="black", linewidth=0.8)
        ax.plot(e.mean(), y, marker="o", color="black", markersize=4.5, linestyle="none")
        ax.plot(e.worst(), y, marker="o", color="black", markerfacecolor="white",
                markersize=4.5, linestyle="none")
        ax.text(e.mean(), y + 0.2, f"mean {e.mean():.1f}", ha="center", va="bottom",
                fontsize=6.3)
        ax.text(e.worst() - 15, y - 0.2, f"worst {e.worst():.1f}", ha="right", va="top",
                fontsize=6.3) if e.policy != "hold" else ax.text(
            e.worst(), y - 0.2, f"worst {e.worst():.1f}", ha="left", va="top", fontsize=6.3)
        verdict = "admissible" if e.admissible() else f"excluded, {len(e.violations)} breaches"
        ax.text(1310, y, verdict, ha="left", va="center", fontsize=6.3, style="italic")
    ax.axvline(CEILING, color="black", linewidth=0.6, linestyle=DASHES[1])
    ax.text(CEILING - 8, 2.62, "ceiling 1100", ha="right", va="center", fontsize=6.5)

    ax.set_yticks(ys)
    ax.set_yticklabels([e.policy for e in evaluations])
    ax.set_ylim(-0.6, 2.8)
    ax.set_xlim(380, 1560)
    ax.set_xticks([400, 600, 800, 1000, 1200])
    ax.set_xlabel("final adopters across 25 shared draws")
    ax.tick_params(axis="y", length=0)

    fig.tight_layout()
    save(fig, "policy-comparison")


if __name__ == "__main__":
    main()
