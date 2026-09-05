#!/usr/bin/env python3
"""Back matter BM3, "Selection table": the fourteen cases placed by what each rests on.

BM3 lists ten teaching cases and four cases fitted to a public record, and its evidential
strength table says what each rests on. This figure places every case on two axes the guide
uses in prose: how many stocks the case's structure carries (left to right, from one stock to
several coupled through delay), and what its numbers rest on (bottom to top: a teaching design,
a documented structure with illustrative numbers, a fit to a named public record). Positions
are a layout reading of BM3's tables, not measurements.

    uv run --group figures python build/figures/fig_case_portfolio_map.py

No numeric data. Both axes are ordinal and the labels are the guide's case names.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402

# (x: structural complexity 1..4, y: evidence band 1..3, label, marker)
CASES = [
    (1.0, 2.0, "Bathtub", "o"),
    (1.55, 2.0, "Workforce learning", "o"),
    (2.0, 2.0, "Bass diffusion", "o"),
    (2.35, 2.0, "GE employment swing", "o"),
    (2.55, 2.0, "Beer game", "o"),
    (3.1, 2.0, "Commodity cycle", "o"),
    (3.4, 2.0, "Hospital flow", "o"),
    (3.2, 1.0, "Service growth trap", "s"),
    (2.6, 1.0, "Technical debt", "s"),
    (1.4, 1.0, "AI operations", "s"),
    (1.5, 3.0, "Congestion curve", "^"),
    (2.0, 3.0, "Hiring pipeline", "^"),
    (2.5, 3.0, "Elective backlog", "^"),
    (3.0, 3.0, "Capacity cycle", "^"),
]
BANDS = {1: "teaching design", 2: "documented structure,\nillustrative numbers",
         3: "fitted to a public record"}
UP, DOWN = (0, 0.17, "center"), (0, -0.18, "center")
OFFSETS = {
    "Bathtub": UP, "Workforce learning": DOWN, "Bass diffusion": UP, "GE employment swing": DOWN,
    "Beer game": UP, "Commodity cycle": UP, "Hospital flow": DOWN,
    "Service growth trap": UP, "Technical debt": DOWN, "AI operations": UP,
    "Congestion curve": UP, "Hiring pipeline": DOWN, "Elective backlog": UP, "Capacity cycle": DOWN,
}


def main():
    assert len(CASES) == 14 and len({c[2] for c in CASES}) == 14
    fig, ax = figure(height_in=2.9)
    for x, y, label, marker in CASES:
        ax.plot([x], [y], marker=marker, markersize=4.5, color="black",
                markerfacecolor="white" if marker != "s" else "black", linestyle="none")
        dx, dy, ha = OFFSETS[label]
        ax.text(x + dx, y + dy, label, ha=ha, va="center", fontsize=6.2)
    for y in (1.5, 2.5):
        ax.axhline(y, color="black", linewidth=0.4, linestyle=(0, (1.2, 1.4)))
    ax.set_yticks([1, 2, 3])
    ax.set_yticklabels([BANDS[1], BANDS[2], BANDS[3]], fontsize=6.5)
    ax.set_xticks([1, 2, 3, 3.5])
    ax.set_xticklabels(["one stock", "two loops", "several stocks", "coupled\nthrough delay"],
                       fontsize=6.5)
    ax.set_xlim(0.6, 3.8)
    ax.set_ylim(0.55, 3.45)
    ax.set_xlabel("structure the case carries")
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    save(fig, "case-portfolio-map")


if __name__ == "__main__":
    main()
