#!/usr/bin/env python3
"""Chapter 28, "A better job for a machine": the four test categories, ordered by how early each
can fail a model.

The chapter builds four kinds of check and later orders them: structural first, because it reads
the document and its failures make the others meaningless; dimensional second, because a unit
defect changes what every later number means; extreme condition third, because it needs a running
model; regression last, because a baseline means something only once the first three pass. This
figure draws the four in that order, each with what it needs, and the rule that a failure at an
early stage makes the later results uninformative.

    uv run --group figures python build/figures/fig_four_test_categories.py

No numeric data. Placement is a layout choice; the names and their order are
chapters.chapter_28_critic.code.critic.CATEGORIES, asserted before drawing, and the one-line
descriptions are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import link, stock  # noqa: E402

from chapters.chapter_28_critic.code.critic import CATEGORIES  # noqa: E402

NEEDS = {
    "structural": ("reads the document", "loops, unread variables,", "stocks with no flow"),
    "dimensional": ("reads the units", "a flow with no time base,", "a stock that is a rate"),
    "extreme": ("runs the model", "from empty and from", "very large; limits or defects"),
    "regression": ("needs a baseline", "outputs against an", "accepted run"),
}


def main():
    assert CATEGORIES == ("structural", "dimensional", "extreme", "regression"), CATEGORIES
    assert tuple(NEEDS) == CATEGORIES

    fig, ax = figure(height_in=2.05)
    ax.set_xlim(-0.2, 9.6)
    ax.set_ylim(-1.95, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")

    w, h, step = 2.0, 0.7, 2.45
    xs = [0.9 + i * step for i in range(4)]
    for x, name in zip(xs, CATEGORIES):
        stock(ax, x, 0.5, name, w=w, h=h)
        first, second, third = NEEDS[name]
        ax.text(x, -0.1, first, ha="center", va="center", fontsize=6.3, style="italic")
        ax.text(x, -0.4, second, ha="center", va="center", fontsize=6.0)
        ax.text(x, -0.65, third, ha="center", va="center", fontsize=6.0)
    for a, b in zip(xs, xs[1:]):
        link(ax, (a + w / 2, 0.5), (b - w / 2, 0.5), polarity="", curve=0.0, shrinkA=2.0,
             shrinkB=2.0)

    ax.annotate("", xy=(xs[-1] + w / 2, -1.15), xytext=(xs[0] - w / 2, -1.15),
                arrowprops=dict(arrowstyle="-|>", linewidth=0.7, color="black",
                                mutation_scale=8))
    ax.text((xs[0] + xs[-1]) / 2, -1.5,
            "earlier and cheaper to fail; a failure here makes every later result uninformative",
            ha="center", va="center", fontsize=6.4)

    fig.tight_layout()
    save(fig, "four-test-categories")


if __name__ == "__main__":
    main()
