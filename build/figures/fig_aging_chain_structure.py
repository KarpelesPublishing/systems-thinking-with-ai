#!/usr/bin/env python3
"""Chapter 17, "A stock that is not homogeneous": a workforce as three tenure bands.

The chapter splits one stock into a junior band, a mid band, and a senior band. Hires enter the
first band, maturation moves people rightward, and attrition leaves from every band. Each band
holds two quantities, people and the experience those people carry, which is the pack's Band.
This figure draws that chain; the field names on the stocks are read from Band.

    uv run --group figures python build/figures/fig_aging_chain_structure.py

No numeric data. Placement is a layout choice; the bands, flows, and coflow fields are the
chapter's and the pack's.
"""
import sys
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, flow, stock  # noqa: E402

from chapters.chapter_17_cohorts.code.cohorts import Band  # noqa: E402


def main():
    names = [f.name for f in fields(Band)]
    assert names == ["people", "experience"], names
    sub = ", ".join(names)

    fig, ax = figure(height_in=2.2)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.7, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    xs = [2.2, 4.6, 7.0]
    cloud(ax, 0.45, 0.2)
    flow(ax, (0.8, 0.2), (1.45, 0.2), label="hires", valve=False)
    for x, name in zip(xs, ("junior", "mid", "senior"), strict=True):
        stock(ax, x, 0.2, name, w=1.5, h=0.7, sublabel=sub)
        cloud(ax, x, -1.35, r=0.2)
        flow(ax, (x, -0.15), (x, -1.0), label="attrition", valve=False, label_side="below",
             fontsize=6.0)
    for a, b in zip(xs, xs[1:], strict=False):
        flow(ax, (a + 0.75, 0.2), (b - 0.75, 0.2), label="maturation", fontsize=6.0)
    ax.text(4.6, 0.85, "only time moves anyone to the right", ha="center", va="center",
            fontsize=6.2, style="italic")

    fig.tight_layout()
    save(fig, "aging-chain-structure")


if __name__ == "__main__":
    main()
