#!/usr/bin/env python3
"""Chapter 31, "The local check sequence": six stages in order, and a failure stopping them.

The chapter prints `ci_sequence()`: schema, semantics, compile, tests, provenance, replay, cheapest
and most specific first, and shows `run_ci` reporting the first failure with the note that later
stages were not evaluated as evidence. This figure draws the six stages in that order with the
chapter's example failure at compile: the stages after it are drawn dashed, because a pass there
would not count.

    uv run --group figures python build/figures/fig_check_sequence.py

Data: chapters.chapter_31_repository.code.permissions.ci_sequence() and run_ci with compile
failing. The drawn stage list is asserted equal to the sequence's stage names before anything is
drawn. Placement is a layout choice; the stage names, their order, the one-line descriptions,
and the failure note are the pack's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from sdvocab import link, stock  # noqa: E402

from chapters.chapter_31_repository.code.permissions import ci_sequence, run_ci  # noqa: E402

# The stage descriptions from ci_sequence(), wrapped by hand for a narrow column.
WRAPPED = {
    "schema": ("every document", "validates against", "its schema"),
    "semantics": ("references resolve,", "flows name stocks,", "units carry time"),
    "compile": ("no algebraic loops,", "an evaluation", "order exists"),
    "tests": ("chapter packs and", "the runtime", "suite pass"),
    "provenance": ("every observed", "parameter names", "a source"),
    "replay": ("recorded scenarios", "reproduce their", "stored outputs"),
}


def main():
    stages = [step.split(":")[0] for step in ci_sequence()]
    assert stages == list(WRAPPED), stages
    assert stages == ["schema", "semantics", "compile", "tests", "provenance", "replay"]
    verdict = run_ci({"schema": True, "semantics": True, "compile": False, "tests": True,
                      "provenance": True, "replay": True})
    assert verdict == {"passed": False, "failed_at": "compile",
                       "note": "later stages were not evaluated as evidence"}, verdict
    failed_at = stages.index(verdict["failed_at"])

    fig, ax = figure(height_in=2.3)
    ax.set_xlim(-0.2, 10.4)
    ax.set_ylim(-2.7, 1.05)
    ax.set_aspect("equal")
    ax.axis("off")

    w, h, step = 1.3, 0.6, 1.72
    xs = [0.75 + i * step for i in range(6)]
    for i, (x, name) in enumerate(zip(xs, stages)):
        if i > failed_at:
            ax.add_patch(Rectangle((x - w / 2, 0.5 - h / 2), w, h, facecolor="white",
                                   edgecolor="black", linewidth=0.9,
                                   linestyle=(0, (2.5, 1.8)), zorder=3))
            ax.text(x, 0.5, name, ha="center", va="center", fontsize=7.0, zorder=4)
        else:
            stock(ax, x, 0.5, name, w=w, h=h)
        for j, line in enumerate(WRAPPED[name]):
            ax.text(x, -0.1 - 0.24 * j, line, ha="center", va="center", fontsize=5.6)
    for i, (a, b) in enumerate(zip(xs, xs[1:])):
        link(ax, (a + w / 2, 0.5), (b - w / 2, 0.5), polarity="", curve=0.0, shrinkA=1.5,
             shrinkB=1.5, linestyle="solid" if i < failed_at else (0, (2.5, 1.8)))

    # The failure: compile fails, the sequence stops, later passes are not evidence.
    fx = xs[failed_at]
    ax.annotate("", xy=(fx, -1.55), xytext=(fx, -0.85),
                arrowprops=dict(arrowstyle="-|>", linewidth=0.9, color="black",
                                mutation_scale=8))
    ax.text(fx, -1.75, "fails: stop here", ha="center", va="top", fontsize=6.4)
    ax.text((xs[failed_at + 1] + xs[-1]) / 2, -1.85, "not evaluated as evidence",
            ha="center", va="center", fontsize=6.4, style="italic")
    ax.text(5.1, -2.45, "cheapest and most specific first; each stage answers to a chapter",
            ha="center", va="center", fontsize=6.2)

    fig.tight_layout()
    save(fig, "check-sequence")


if __name__ == "__main__":
    main()
