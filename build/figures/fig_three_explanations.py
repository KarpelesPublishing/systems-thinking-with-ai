#!/usr/bin/env python3
"""Chapter 2, "Hold several explanations open": three accounts pointing at one observed swing.

The chapter's comparison table lists three possible accounts of the reported employment pattern:
incoming orders rose and fell and the factory followed them; a supply disruption or measurement
error made a stable operation appear unstable; and internal production and employment policies
amplified a small disturbance. Each is paired with the observation that could weaken it. This
figure draws the three accounts as boxes with arrows into the one observed swing, and sets each
account's weakening observation beneath it:

    uv run --group figures python build/figures/fig_three_explanations.py

No numeric data. Box placement and the wrapping of the chapter's phrases are layout; the three
accounts, their weakening observations, and the single shared observation are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402


def box(ax, x, y, w, h, title, body, title_size=7.0, body_size=6.0, dashed=False):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor="black", linewidth=0.9,
                                linestyle=(0, (3.0, 2.0)) if dashed else "solid", zorder=3))
    ax.text(x, y + h / 2 - 0.16, title, ha="center", va="top", fontsize=title_size, zorder=4)
    ax.text(x, y - h / 2 + 0.13, body, ha="center", va="bottom", fontsize=body_size,
            style="italic", zorder=4)


def main():
    fig, ax = figure(height_in=2.6)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-0.3, 3.9)
    ax.set_aspect("equal")
    ax.axis("off")

    accounts = [
        (1.35, "external\ndemand cycle", "orders rose and fell,\nthe factory followed",
         "weakened if the order\nhistory lacks the swing"),
        (4.2, "disruption or\nmeasurement error", "a stable operation\nmade to look unstable",
         "weakened if dated records\nshow no error that large"),
        (7.05, "internal policy\namplification",
         "production and staffing\nrules amplified a\nsmall disturbance",
         "weakened if a reconstruction\ncannot produce the swing"),
    ]
    for x, title, body, weak in accounts:
        box(ax, x, 2.75, 2.5, 1.55, title, body)
        ax.text(x, 1.72, weak, ha="center", va="top", fontsize=5.8, zorder=4)
        ax.annotate("", xy=(4.2 + (x - 4.2) * 0.34, 0.86), xytext=(x, 1.15),
                    arrowprops=dict(arrowstyle="-|>", linewidth=0.8, color="black",
                                    shrinkA=0, shrinkB=2, mutation_scale=8), zorder=2)

    box(ax, 4.2, 0.35, 3.6, 0.95, "one observed swing", "heavy operation, then half laid off",
        dashed=True)

    fig.tight_layout()
    save(fig, "three-explanations")


if __name__ == "__main__":
    main()
