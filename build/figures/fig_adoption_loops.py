#!/usr/bin/env python3
"""Chapter 14, "Adoption, with two loops": word of mouth and saturation through one stock.

The chapter's Bass structure has adoption from outside influence (the innovation parameter,
proportional to the remaining potential) and adoption from contact with existing adopters (the
imitation parameter times the adopter pool). The reinforcing loop runs through the adopter
stock; the balancing loop runs through the depleting potential. This figure draws that structure
with loop names taken from the pack's REINFORCING and BALANCING constants and parameter names
from the Diffusion dataclass.

    uv run --group figures python build/figures/fig_adoption_loops.py

No numeric data. Placement is a layout choice; the stocks, the parameters, and the two loops are
the chapter's.
"""
import sys
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, flow, link, loop_id, stock  # noqa: E402

from chapters.chapter_14_dominance.code.dominance import (  # noqa: E402
    BALANCING,
    REINFORCING,
    Diffusion,
)


def main():
    names = {f.name for f in fields(Diffusion)}
    assert {"total_market", "innovation", "imitation"} <= names, names
    assert REINFORCING == "word of mouth" and BALANCING == "saturation"

    fig, ax = figure(height_in=2.55)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.7, 1.75)
    ax.set_aspect("equal")
    ax.axis("off")

    left, right = (1.55, 0.0), (6.85, 0.0)
    stock(ax, *left, "potential adopters", w=2.3, h=0.75, sublabel="total_market minus adopters")
    stock(ax, *right, "adopters", w=2.3, h=0.75, sublabel="people")
    valve = flow(ax, (2.7, 0.0), (5.7, 0.0))
    ax.text(4.2, 0.42, "adoption rate", ha="center", va="center", fontsize=6.8, zorder=6)

    auxiliary(ax, 2.0, 1.3, "innovation", r=0.36, dashed=True)
    auxiliary(ax, 6.4, 1.3, "imitation", r=0.36, dashed=True)
    link(ax, (2.0, 1.3), valve, polarity="", curve=0.0, shrinkA=11, shrinkB=8)
    link(ax, (6.4, 1.3), valve, polarity="", curve=0.0, shrinkA=11, shrinkB=8)

    # reinforcing: adopters feed contact, contact feeds adoption
    link(ax, (6.85, -0.38), (4.2, -0.12), polarity="+", curve=-0.35, shrinkA=4, shrinkB=8)
    loop_id(ax, 5.55, -1.0, "R", direction="cw")
    ax.text(5.55, -1.45, REINFORCING, ha="center", va="center", fontsize=6.2, style="italic")

    # balancing: adoption drains potential, less potential means less adoption
    link(ax, (1.55, -0.38), (4.2, -0.12), polarity="+", curve=0.35, shrinkA=4, shrinkB=8)
    loop_id(ax, 2.85, -1.0, "B", direction="ccw")
    ax.text(2.85, -1.45, BALANCING, ha="center", va="center", fontsize=6.2, style="italic")

    fig.tight_layout()
    save(fig, "adoption-loops")


if __name__ == "__main__":
    main()
