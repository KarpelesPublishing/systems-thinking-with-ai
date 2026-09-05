#!/usr/bin/env python3
"""Chapter 22, "The step": one step of the runtime as a four-stage cycle.

The chapter's runtime does one thing per step and does it in a fixed order: it reads the stocks
as the state carried in from the previous step, evaluates every computed quantity from that state
in the compiler's order, forms the net rate of change of every stock from the flows attached to
it, and writes every stock from rates computed before any of them moved. This figure draws those
four stages as a cycle, each box carrying the corresponding code from
chapters/chapter_22_runtime/code/runtime.py that performs it: `state = dict(self.stocks)`,
`_environment(state)`, `derivatives(state)`, `_advance(state, dt)`. The closing arrow is
`t += dt`, after the step's environment has been recorded into the Result.

    uv run --group figures python build/figures/fig_runtime_step.py

No numeric data. Placement is a layout choice; the stages, their order, and the code labels are
the pack's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import link, stock  # noqa: E402


def main():
    fig, ax = figure(height_in=2.35)
    ax.set_xlim(-0.3, 8.7)
    ax.set_ylim(-2.2, 1.85)
    ax.set_aspect("equal")
    ax.axis("off")

    w, h = 2.6, 0.9
    boxes = [
        ((1.6, 1.25), "read stocks", "state = dict(self.stocks)"),
        ((6.8, 1.25), "evaluate environment", "_environment(state)"),
        ((6.8, -1.25), "form derivatives", "derivatives(state)"),
        ((1.6, -1.25), "write stocks", "_advance(state, dt)"),
    ]
    for (x, y), name, method in boxes:
        stock(ax, x, y, name, w=w, h=h, sublabel=method)

    # Clockwise: read, evaluate, derive, write, and back to read for the next step.
    link(ax, (1.6 + w / 2, 1.25), (6.8 - w / 2, 1.25), polarity="", curve=0.0,
         shrinkA=2.0, shrinkB=2.0, label="in evaluation order")
    link(ax, (6.8, 1.25 - h / 2), (6.8, -1.25 + h / 2), polarity="", curve=0.0,
         shrinkA=2.0, shrinkB=2.0)
    ax.text(6.6, 0.0, "flows, by target and sign", ha="right", va="center", fontsize=6.6,
            style="italic")
    link(ax, (6.8 - w / 2, -1.25), (1.6 + w / 2, -1.25), polarity="", curve=0.0,
         shrinkA=2.0, shrinkB=2.0)
    ax.text(4.2, -1.95, "every stock from rates formed before any moved", ha="center",
            va="center", fontsize=6.6, style="italic")
    link(ax, (1.6, -1.25 + h / 2), (1.6, 1.25 - h / 2), polarity="", curve=0.0,
         shrinkA=2.0, shrinkB=2.0)
    ax.text(1.8, 0.0, "record, then t += dt", ha="left", va="center", fontsize=6.6,
            style="italic")

    fig.tight_layout()
    save(fig, "runtime-step")


if __name__ == "__main__":
    main()
