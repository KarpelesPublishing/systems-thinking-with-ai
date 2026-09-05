#!/usr/bin/env python3
"""Chapter 10, "Four boundaries, drawn separately": the four boundaries, nested, each excluding.

The chapter says a model boundary is at least four decisions that fail independently: the
temporal boundary (horizon and time step), the geographic or physical boundary (which locations
are inside), the organizational boundary (which functions and decision rights), and the
population boundary (which people are treated as one kind). This figure draws them as four nested
dashed boundaries, each labelled with what the chapter says it excludes:

    uv run --group figures python build/figures/fig_boundary_nesting.py

No numeric data. The nesting order, outermost temporal to innermost population, is a layout
choice; the four names and the exclusions written beside each are the chapter's own examples
(a weekly crisis invisible to a monthly step, the ward a hospital discharges into, the other
stations of Chapter 5's chain, and the kinds of customer aggregated into one).
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import boundary  # noqa: E402


def main():
    fig, ax = figure(height_in=3.0)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-0.2, 5.6)
    ax.set_aspect("equal")
    ax.axis("off")

    rings = [
        ("temporal boundary",
         "excludes: anything past the horizon,\nor resolving within one time step"),
        ("geographic or physical boundary",
         "excludes: the ward this ward\ndischarges into"),
        ("organizational boundary",
         "excludes: the other stations of the chain,\nso amplification cannot be seen"),
        ("population boundary",
         "excludes: the differences between\nkinds of customer, aggregated as one"),
    ]
    x0, y0, x1, y1 = 0.0, 0.0, 8.4, 5.4
    for i, (name, excludes) in enumerate(rings):
        left, bottom = x0 + i * 0.75, y0 + i * 0.8
        right, top = x1 - i * 0.2, y1 - i * 0.55
        boundary(ax, left, bottom, right, top, name)
        ax.text(right - 0.1, bottom + 0.08, excludes, ha="right", va="bottom", fontsize=5.9)

    fig.tight_layout()
    save(fig, "boundary-nesting")


if __name__ == "__main__":
    main()
