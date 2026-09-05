#!/usr/bin/env python3
"""Chapter 25, "The dashboard contract": what a policy-learning interface may show, must state, and
may never present as a prediction.

The chapter writes the contract as five rules: every display cites an artifact; uncertainty is
displayed, not resolved; controls expose policies, not outcomes; constraints are visible and
breaches are loud; the model's identity is on the screen. This figure sorts the content of those
rules into three columns. "May show" holds what the rules permit on a screen; "must state" holds
what each screen has to carry with it; "never as a prediction" holds the displays the rules rule
out, including the single confident forecast line the chapter says a compliant dashboard cannot
show.

    uv run --group figures python build/figures/fig_dashboard_contract.py

No numeric data. The grouping and placement are layout choices; every item is taken from the
chapter's five rules.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import boundary  # noqa: E402

COLUMNS = (
    ("may show", [
        ("scenarios as a range,", "or as several lines"),
        ("controls for what a", "decision maker can change:", "a hiring rate, a price,",
         "an intake cap"),
        ("a breach of a declared", "bound, marked on screen"),
    ]),
    ("must state", [
        ("the scenario record", "every number came from"),
        ("the model's version", "and hash, findable", "on the screen itself"),
        ("the declared constraints", "each scenario was", "checked against"),
    ]),
    ("never as a prediction", [
        ("a single confident", "forecast line"),
        ("an average of scenarios:", "a path no scenario produced"),
        ("a composite chart from runs", "with different settings"),
        ("an outcome set directly", "by a control"),
    ]),
)


def main():
    fig, ax = figure(height_in=2.55)
    ax.set_xlim(-0.15, 9.45)
    ax.set_ylim(-0.15, 4.05)
    ax.set_aspect("equal")
    ax.axis("off")

    col_w, gap = 2.95, 0.2
    for i, (title, lines) in enumerate(COLUMNS):
        x0 = i * (col_w + gap)
        boundary(ax, x0, 0.0, x0 + col_w, 3.9, "")
        ax.text(x0 + col_w / 2, 3.6, title, ha="center", va="center", fontsize=7.4,
                weight="bold")
        ax.plot([x0 + 0.25, x0 + col_w - 0.25], [3.32, 3.32], color="black", linewidth=0.5)
        y = 3.0
        for item in lines:
            for j, line in enumerate(item):
                ax.text(x0 + 0.22, y, ("• " if j == 0 else "   ") + line, ha="left",
                        va="center", fontsize=6.2)
                y -= 0.30
            y -= 0.08

    fig.tight_layout()
    save(fig, "dashboard-contract")


if __name__ == "__main__":
    main()
