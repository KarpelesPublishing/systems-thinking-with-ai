#!/usr/bin/env python3
"""Chapter 7, "The framing canvas": the eleven boxes with the decision at the centre.

The chapter's canvas has eleven boxes: decision, decider, purpose, audience, outcome, reference
behavior, levers, horizon, inside the boundary, outside the boundary, and affected parties and
prohibitions. This figure lays them out around the decision, which the chapter says every other
box must connect to, and writes the chapter's short description under each name:

    uv run --group figures python build/figures/fig_framing_canvas.py

No numeric data. The box names and the phrase in each are the chapter's table; the field names
match DecisionContract in chapters.chapter_07_decision_contract.code.contract (decision, decider,
horizon, outcomes, levers, inside_boundary, outside_boundary, prohibited_actions,
affected_parties), with purpose, audience, and reference behavior from the chapter's canvas.
The arrangement is layout.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

from chapters.chapter_07_decision_contract.code.contract import DecisionContract  # noqa: E402


def box(ax, x, y, w, h, title, body, bold=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02",
                                facecolor="white", edgecolor="black",
                                linewidth=1.2 if bold else 0.8, zorder=3))
    ax.text(x, y + h / 2 - 0.11, title, ha="center", va="top", fontsize=6.6, zorder=4,
            weight="bold" if bold else "normal")
    ax.text(x, y - h / 2 + 0.10, body, ha="center", va="bottom", fontsize=5.5, style="italic",
            zorder=4)


def main():
    fields = set(DecisionContract.__dataclass_fields__)
    for name in ("decision", "decider", "horizon_length", "outcomes", "levers",
                 "inside_boundary", "outside_boundary", "prohibited_actions",
                 "affected_parties"):
        assert name in fields, name

    fig, ax = figure(height_in=3.0)
    ax.set_xlim(-0.1, 8.7)
    ax.set_ylim(-0.1, 5.9)
    ax.set_aspect("equal")
    ax.axis("off")

    w, h = 2.55, 1.05
    cols = [1.3, 4.3, 7.3]
    rows = [5.3, 3.65, 2.0, 0.5]
    layout = {
        (0, 0): ("Decider", "a named role that\ncan take the action"),
        (0, 1): ("Purpose", "choosing between options,\nor understanding a mechanism"),
        (0, 2): ("Audience", "who reads the output\nand what they can check"),
        (1, 0): ("Outcome", "the quantity that defines\nbetter, with a unit"),
        (1, 2): ("Levers", "what the decider controls,\nwith units"),
        (2, 0): ("Reference behavior", "what the outcome has\ndone over time"),
        (2, 2): ("Horizon", "a number and a unit, long\nenough to hold the consequence"),
        (3, 0): ("Inside the boundary", "what the model represents"),
        (3, 1): ("Outside the boundary", "what is deliberately\nexcluded, not empty"),
        (3, 2): ("Affected parties, prohibitions",
                 "who bears the consequences,\nwhat is off the table"),
    }
    for (r, c), (title, body) in layout.items():
        box(ax, cols[c], rows[r], w, h, title, body)
    cx, cy = cols[1], (rows[1] + rows[2]) / 2
    box(ax, cx, cy, w, 1.7, "Decision",
        "actor, action, moment,\nalternative: answerable\nyes or no, or with a number", bold=True)

    def edge_point(bx, by, bw, bh, tx, ty):
        """Where the ray from box centre (bx, by) toward (tx, ty) leaves the box."""
        dx, dy = tx - bx, ty - by
        sx = (bw / 2) / abs(dx) if dx else float("inf")
        sy = (bh / 2) / abs(dy) if dy else float("inf")
        s = min(sx, sy)
        return bx + dx * s, by + dy * s

    for (r, c) in layout:
        x, y = cols[c], rows[r]
        start = edge_point(x, y, w, h, cx, cy)
        end = edge_point(cx, cy, w, 1.7, x, y)
        ax.annotate("", xy=end, xytext=start,
                    arrowprops=dict(arrowstyle="-|>", linewidth=0.6, color="black",
                                    shrinkA=1, shrinkB=1, mutation_scale=6), zorder=2)

    fig.tight_layout()
    save(fig, "framing-canvas")


if __name__ == "__main__":
    main()
