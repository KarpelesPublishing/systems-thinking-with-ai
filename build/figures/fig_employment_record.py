#!/usr/bin/env python3
"""Chapter 2, "The question inside the layoff": the employment pattern Forrester described.

The chapter reports Forrester's recollection of appliance facilities running seven days a week on
three shifts, and, three or four years later, half the people laid off. It supplies no dated
series and no numbers beyond "half" and "three or four years", and the chapter's factory pack
(run_factory_cycle) tracks inventory and work in process, not employment. So this figure is a
sketch of the described shape, not a data plot: a rise into sustained heavy operation, then a fall
to half. The axes carry no numeric ticks, only the two marks the chapter's wording supports:

    uv run --group figures python build/figures/fig_employment_record.py

No pack numbers. The curve is a smooth rise, plateau, and fall drawn to place the peak plateau at
twice the ending level; its exact shape, the interval marked as three or four years, and the label
positions are layout choices. The chapter's content is the sequence and the ratio of one half.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import DASHES, figure, save  # noqa: E402


def smooth_step(x):
    return 0.5 * (1.0 - math.cos(math.pi * min(max(x, 0.0), 1.0)))


def main():
    n = 200
    xs = [i / (n - 1) for i in range(n)]
    ys = []
    for x in xs:
        rise = smooth_step((x - 0.05) / 0.30)
        fall = smooth_step((x - 0.62) / 0.28)
        ys.append(0.5 + 0.5 * rise - 0.5 * fall)
    assert abs(ys[-1] / max(ys) - 0.5) < 1e-6

    fig, ax = figure(height_in=2.3)
    ax.plot(xs, ys, color="black", linestyle=DASHES[0])
    ax.axhline(1.0, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.axhline(0.5, color="black", linewidth=0.4, linestyle=DASHES[2])
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0.2, 1.25)
    ax.set_xticks([])
    ax.set_yticks([1.0, 0.5])
    ax.set_yticklabels(["seven days,\nthree shifts", "half laid off"], fontsize=6.6)
    ax.set_xlabel("time, in the order the account gives it")
    ax.set_ylabel("employment")
    ax.annotate("", xy=(0.62, 1.12), xytext=(0.35, 1.12),
                arrowprops=dict(arrowstyle="<->", linewidth=0.6, color="black",
                                mutation_scale=7))
    ax.text(0.485, 1.145, "three or four years of sustained pressure", fontsize=6.4,
            ha="center", va="bottom")
    ax.text(0.50, 0.36, "orders steady or swinging?\nthe record was not kept", fontsize=6.2,
            ha="center", va="center", style="italic")
    fig.tight_layout()
    save(fig, "employment-record")


if __name__ == "__main__":
    main()
