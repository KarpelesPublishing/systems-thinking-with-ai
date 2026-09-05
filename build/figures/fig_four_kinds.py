#!/usr/bin/env python3
"""Chapter 13, "Four things that look like one thing": auxiliary, parameter, perception, rule.

The chapter separates four kinds of quantity that share one notation: an auxiliary is algebra
over what the model already holds, a parameter is a number from outside the run, a perception has
state and a formation delay, and a decision rule has an owner and produces a flow. This figure
draws one node of each kind with what each may depend on.

    uv run --group figures python build/figures/fig_four_kinds.py

No numeric data. The glyphs and the column layout are a layout choice; the four kinds and
their dependencies are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, delay_mark, link, stock, text_node  # noqa: E402


def main():
    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.3, 8.9)
    ax.set_ylim(-1.8, 1.55)
    ax.set_aspect("equal")
    ax.axis("off")

    xs = [0.9, 3.1, 5.3, 7.6]
    y = 0.0

    # auxiliary: reads stocks and other auxiliaries, holds nothing
    auxiliary(ax, xs[0], y, "auxiliary", r=0.42)
    text_node(ax, xs[0] - 0.55, 1.15, "stock", fontsize=6.4)
    text_node(ax, xs[0] + 0.55, 1.15, "auxiliary", fontsize=6.4)
    link(ax, (xs[0] - 0.55, 1.15), (xs[0], y), polarity="", curve=0.0, shrinkA=6, shrinkB=13)
    link(ax, (xs[0] + 0.55, 1.15), (xs[0], y), polarity="", curve=0.0, shrinkA=6, shrinkB=13)

    # parameter: nothing inside the run feeds it
    auxiliary(ax, xs[1], y, "parameter", r=0.42, dashed=True)
    text_node(ax, xs[1], 1.15, "evidence bundle", fontsize=6.4, style="italic")
    link(ax, (xs[1], 1.15), (xs[1], y), polarity="", curve=0.0, shrinkA=6, shrinkB=13,
         linestyle=(0, (2.5, 1.5)))

    # perception: state, fed by a signal through a delay
    stock(ax, xs[2], y, "perception", w=1.25, h=0.62, sublabel="has state")
    text_node(ax, xs[2], 1.15, "true value", fontsize=6.4)
    link(ax, (xs[2], 1.15), (xs[2], y), polarity="", curve=0.0, shrinkA=6, shrinkB=10)
    delay_mark(ax, (xs[2], 0.72), -90)

    # decision rule: reads perceptions and parameters, writes a flow
    stock(ax, xs[3], y, "decision rule", w=1.35, h=0.62, sublabel="has an owner")
    text_node(ax, xs[3] - 0.55, 1.15, "perception", fontsize=6.4)
    text_node(ax, xs[3] + 0.55, 1.15, "parameter", fontsize=6.4)
    link(ax, (xs[3] - 0.55, 1.15), (xs[3], y), polarity="", curve=0.0, shrinkA=6, shrinkB=10)
    link(ax, (xs[3] + 0.55, 1.15), (xs[3], y), polarity="", curve=0.0, shrinkA=6, shrinkB=10)
    link(ax, (xs[3], y), (xs[3], -1.0), polarity="", curve=0.0, shrinkA=10, shrinkB=4)
    text_node(ax, xs[3], -1.15, "a flow", fontsize=6.4)

    notes = ["algebra, no state:\ndelete it and\nnothing changes",
             "fixed for the run,\nfrom outside:\nneeds a bundle",
             "a belief, formed\nfrom history,\nlagging the truth",
             "what somebody does,\nat a frequency,\nwithin limits"]
    for x, note in zip(xs[:3], notes[:3], strict=True):
        ax.text(x, -0.95, note, ha="center", va="top", fontsize=5.9, style="italic")
    ax.text(xs[3] + 0.05, -1.3, notes[3], ha="center", va="top", fontsize=5.9, style="italic")

    fig.tight_layout()
    save(fig, "four-kinds")


if __name__ == "__main__":
    main()
