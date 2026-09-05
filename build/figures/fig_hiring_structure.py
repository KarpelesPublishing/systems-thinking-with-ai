#!/usr/bin/env python3
"""Chapter 37, "The loops": the hiring pipeline as stocks, flows, and two loops.

The chapter's model has three stocks: vacancies, drained by hires after a fill delay; headcount,
filled by hires and drained by quits and layoffs; and experience, a coflow on headcount that
hires add to at a fraction, learning raises toward headcount over a ramp, and leavers take from.
A target gap opens vacancies (B, balancing). Understaffing raises workload, workload raises
quits, and quits reopen the gap (R, reinforcing). This figure draws that structure:

    uv run --group figures python build/figures/fig_hiring_structure.py

No numeric data. Placement is a layout choice; the elements are the model document's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, cloud, flow, link, loop_id, stock  # noqa: E402

from chapters.chapter_37_hiring_pipeline.code.model import document  # noqa: E402

# The flow names are shortened for the drawing ("opened" for vacancies_opened), which is a
# layout choice. The three stocks are not: they are the document's own ids and are pinned.
STOCKS = {"vacancies", "headcount", "experience"}


def main():
    stocks = {v.id for v in document().variables if v.kind == "stock" and v.id != "clock"}
    assert stocks == STOCKS, f"model stocks changed: {stocks}"

    fig, ax = figure(height_in=3.1)
    ax.set_xlim(-0.3, 9.6)
    ax.set_ylim(-2.9, 2.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # top row: vacancies -> hires -> headcount -> quits, layoffs
    cloud(ax, 0.35, 1.0)
    stock(ax, 2.2, 1.0, "vacancies", w=1.5, h=0.7, sublabel="thousand openings")
    stock(ax, 5.6, 1.0, "headcount", w=1.6, h=0.7, sublabel="thousand persons")
    cloud(ax, 9.0, 1.0)
    opened = flow(ax, (0.7, 1.0), (1.45, 1.0), label="opened", valve=True)
    hires = flow(ax, (2.95, 1.0), (4.8, 1.0), label="hires", double=True)
    leavers = flow(ax, (6.4, 1.0), (8.65, 1.0), label="quits, layoffs")
    ax.text(0.35, 0.45, "source", ha="center", va="center", fontsize=6.2)
    ax.text(9.0, 0.45, "sink", ha="center", va="center", fontsize=6.2)

    # the target gap rule, a balancing loop
    gap = auxiliary(ax, 3.9, 2.15, "gap", r=0.28)
    target = auxiliary(ax, 7.6, 2.15, "target", r=0.30, dashed=True)
    link(ax, target, gap, polarity="+", curve=0.0, shrinkA=9, shrinkB=9)
    link(ax, (5.6, 1.35), gap, polarity="-", curve=0.12, shrinkA=6, shrinkB=9,
         sign_pos=0.95, sign_side=-0.18)
    link(ax, gap, opened, polarity="+", curve=0.0, shrinkA=9, shrinkB=6,
         sign_pos=0.85, sign_side=0.30)
    loop_id(ax, 2.35, 1.95, "B", direction="ccw", r=0.2)

    # bottom row: the experience coflow
    cloud(ax, 0.35, -1.6)
    stock(ax, 2.2, -1.6, "experience", w=1.5, h=0.7, sublabel="thousand effective")
    cloud(ax, 4.55, -1.6)
    hired = flow(ax, (0.7, -1.6), (1.45, -1.6), label="hired", label_side="below")
    flow(ax, (2.95, -1.6), (4.2, -1.6), label="lost", label_side="below")
    learning = flow(ax, (2.2, -2.65), (2.2, -1.95), label=None, valve=True)
    ax.text(2.5, -2.35, "learning, over the ramp", ha="left", va="center", fontsize=6.4,
            style="italic")
    ax.text(0.35, -2.15, "source", ha="center", va="center", fontsize=6.2)
    ax.text(4.55, -2.15, "sink", ha="center", va="center", fontsize=6.2)
    link(ax, hires, hired, polarity="+", curve=0.3, shrinkA=6, shrinkB=6)
    link(ax, (5.6, 0.65), learning, polarity="+", curve=-0.2, shrinkA=6, shrinkB=6)

    # workload and the reinforcing loop
    work = auxiliary(ax, 8.3, -0.7, "workload", r=0.46, fontsize=6.2)
    link(ax, (2.95, -1.25), work, polarity="-", curve=-0.15, shrinkA=4, shrinkB=15,
         sign_pos=0.75)
    link(ax, target, work, polarity="+", curve=-0.25, shrinkA=9, shrinkB=12)
    link(ax, work, leavers, polarity="+", curve=-0.2, shrinkA=12, shrinkB=6)
    loop_id(ax, 6.2, -0.75, "R", direction="cw", r=0.2)

    fig.tight_layout()
    save(fig, "hiring-structure")


if __name__ == "__main__":
    main()
