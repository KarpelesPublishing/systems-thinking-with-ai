#!/usr/bin/env python3
"""Chapter 9, "Four templates and what each one warns about": the four archetypes at one scale.

The chapter presents limits to growth, shifting the burden, fixes that fail, and the tragedy of
the commons, each with the warning it carries. This figure draws the four as small causal loop
templates in a two by two grid at one scale, with the variables the chapter's sentences name:

    uv run --group figures python build/figures/fig_archetype_templates.py

Structure: template link lists written for this figure from the chapter's four paragraphs, each
audited with chapters.chapter_08_causal_graph.code.graph so the R and B labels come from
loop_polarity rather than by hand. The asserts pin each template's loop count and polarity mix
(limits: R and B; shifting the burden: two B and the R erosion loop the chapter says nobody draws;
fixes that fail: B and a delayed R; tragedy: two R on private gain and two B through the shared
resource). The chapter pack (chapters.chapter_09_archetypes.code.limits) implements only the
first template in code, so the names are the chapter's. Placement is layout.
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import grid_figure, save  # noqa: E402
from sdvocab import delay_mark, link, loop_id, text_node  # noqa: E402

from chapters.chapter_08_causal_graph.code.graph import (  # noqa: E402
    Link,
    find_loops,
    loop_polarity,
)

TEMPLATES = {
    "limits to growth": {
        "links": [Link("growth", "state", 1, "proposed", True),
                  Link("state", "growth", 1, "proposed", False),
                  Link("state", "gap to limit", -1, "proposed", False),
                  Link("gap to limit", "growth", 1, "proposed", True)],
        "pos": {"growth": (1.0, 1.2), "state": (3.0, 1.2), "gap to limit": (5.0, 1.2)},
        "curves": {("growth", "state"): -0.5, ("state", "growth"): -0.35,
                   ("state", "gap to limit"): -0.5, ("gap to limit", "growth"): -0.5},
        "ids": [(2.0, 1.2, "R", "cw"), (4.0, 1.2, "B", "cw")],
        "under": {("gap to limit", "growth")},
        "expect": (1, 1),
    },
    "shifting the burden": {
        "links": [Link("symptom", "quick fix", 1, "proposed", False),
                  Link("quick fix", "symptom", -1, "proposed", False),
                  Link("symptom", "fundamental fix", 1, "proposed", True),
                  Link("fundamental fix", "symptom", -1, "proposed", True),
                  Link("quick fix", "capability", -1, "proposed", True),
                  Link("capability", "fundamental fix", 1, "proposed", False)],
        "pos": {"quick fix": (0.9, 1.5), "symptom": (3.0, 1.5), "fundamental fix": (5.1, 1.5),
                "capability": (3.0, 0.2)},
        "curves": {("symptom", "quick fix"): 0.5, ("quick fix", "symptom"): 0.5,
                   ("symptom", "fundamental fix"): -0.5, ("fundamental fix", "symptom"): -0.5,
                   ("quick fix", "capability"): 0.3, ("capability", "fundamental fix"): 0.3},
        "ids": [(1.95, 1.5, "B", "cw"), (4.05, 1.5, "B", "cw"), (3.0, 0.7, "R", "cw")],
        "expect": (1, 2),
    },
    "fixes that fail": {
        "links": [Link("problem", "fix", 1, "proposed", False),
                  Link("fix", "problem", -1, "proposed", False),
                  Link("fix", "later cost", 1, "proposed", True),
                  Link("later cost", "problem", 1, "proposed", True)],
        "pos": {"problem": (1.0, 1.2), "fix": (3.0, 1.2), "later cost": (5.0, 1.2)},
        "curves": {("problem", "fix"): -0.5, ("fix", "problem"): -0.35,
                   ("fix", "later cost"): -0.5, ("later cost", "problem"): -0.5},
        "ids": [(2.0, 1.2, "B", "cw"), (4.0, 1.2, "R", "cw")],
        "under": {("later cost", "problem")},
        "expect": (1, 1),
    },
    "tragedy of the commons": {
        "links": [Link("A's use", "A's gain", 1, "proposed", False),
                  Link("A's gain", "A's use", 1, "proposed", False),
                  Link("B's use", "B's gain", 1, "proposed", False),
                  Link("B's gain", "B's use", 1, "proposed", False),
                  Link("A's use", "resource", -1, "proposed", True),
                  Link("B's use", "resource", -1, "proposed", True),
                  Link("resource", "A's gain", 1, "proposed", True),
                  Link("resource", "B's gain", 1, "proposed", True)],
        "pos": {"A's gain": (0.8, 2.2), "A's use": (0.8, 0.2), "resource": (3.0, 1.2),
                "B's gain": (5.2, 2.2), "B's use": (5.2, 0.2)},
        "curves": {("A's use", "A's gain"): -0.5, ("A's gain", "A's use"): -0.5,
                   ("B's use", "B's gain"): 0.5, ("B's gain", "B's use"): 0.5,
                   ("A's use", "resource"): 0.0, ("B's use", "resource"): 0.0,
                   ("resource", "A's gain"): 0.0, ("resource", "B's gain"): 0.0},
        "sides": {("resource", "A's gain"): -1.0, ("B's use", "resource"): -1.0},
        "ids": [(0.8, 1.2, "R", "cw"), (5.2, 1.2, "R", "ccw"), (1.8, 1.2, "B", "cw"),
                (4.2, 1.2, "B", "ccw")],
        "expect": (2, 2),
    },
}


def causal(ax, a, b, sign, curve=0.0, delay=False, shrinkA=13, shrinkB=13, sign_gap=0.2,
           fontsize=7.2, sign_side=None):
    """Causal arrow with the polarity and any delay mark set on the arc matplotlib draws."""
    link(ax, a, b, polarity="", curve=curve, shrinkA=shrinkA, shrinkB=shrinkB)
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy)
    cx, cy = (x1 + x2) / 2 + curve * dy, (y1 + y2) / 2 - curve * dx
    if delay:
        mx, my = (x1 + x2) / 2 + curve * dy / 2, (y1 + y2) / 2 - curve * dx / 2
        delay_mark(ax, (mx, my), math.degrees(math.atan2(dy, dx)), size=0.11)
    t = 0.80
    px = (1 - t) ** 2 * x1 + 2 * (1 - t) * t * cx + t ** 2 * x2
    py = (1 - t) ** 2 * y1 + 2 * (1 - t) * t * cy + t ** 2 * y2
    side = sign_side if sign_side is not None else (1.0 if curve >= 0 else -1.0)
    ax.text(px + side * dy / n * sign_gap, py - side * dx / n * sign_gap, sign, ha="center",
            va="center", fontsize=fontsize, zorder=6)


def main():
    fig, axes = grid_figure(2, 2, height_in=3.2)
    for ax, (name, t) in zip(axes.flat, TEMPLATES.items(), strict=True):
        loops = find_loops(t["links"])
        kinds = [loop_polarity(loop, t["links"]) for loop in loops]
        reinforcing, balancing = kinds.count("reinforcing"), kinds.count("balancing")
        assert (reinforcing, balancing) == t["expect"], (name, kinds)
        assert sum(1 for i in t["ids"] if i[2] == "R") == reinforcing, name
        assert sum(1 for i in t["ids"] if i[2] == "B") == balancing, name

        ax.set_xlim(-0.3, 6.3)
        ax.set_ylim(-0.3, 2.7)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(name, fontsize=7.2, pad=1)
        for node, (x, y) in t["pos"].items():
            text_node(ax, x, y, node, fontsize=6.2)
        for item in t["links"]:
            key = (item.source, item.target)
            target = t["pos"][item.target]
            shrink_b = 13
            if key in t.get("under", set()):
                # land on the target's lower edge so the head clears the short pair's head
                target, shrink_b = (target[0] - 0.25, target[1] - 0.16), 5
            causal(ax, t["pos"][item.source], target,
                   "+" if item.polarity > 0 else "-", curve=t["curves"][key],
                   delay=bool(item.delayed), shrinkB=shrink_b,
                   sign_side=t.get("sides", {}).get(key))
        for x, y, tag, direction in t["ids"]:
            loop_id(ax, x, y, tag, direction=direction, r=0.2, fontsize=6.4)
    fig.tight_layout(pad=0.2, w_pad=0.4, h_pad=0.3)
    save(fig, "archetype-templates")


if __name__ == "__main__":
    main()
