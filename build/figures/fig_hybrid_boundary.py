#!/usr/bin/env python3
"""Chapter 34, "Which statistic crosses the boundary": the seam between staffing and the queue.

The chapter describes continuous-valued staffing updated each period against observed waiting,
joined to a discrete queue served in batches. The interface sends a per-period service limit
one way and the served-patient mean wait back. The complex group's ninetieth percentile is
shown as a proposed alternative statistic, not an implemented feedback option.
This figure draws the two sides with the pack's names and the two crossings on the seam.

    uv run --group figures python build/figures/fig_hybrid_boundary.py

No numeric data. Placement is a layout choice. The node names are hospital.py's: staff,
target_wait, adjustment_time, max_staff, capacity, the queue of (arrival, group) pairs, the
routine and complex groups in DEFAULT_GROUPS with their shares and service multipliers, and
mean_by_group and p90_by_group from run()'s outcome. The script asserts the group names and
shares it draws are the pack's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import auxiliary, boundary, cloud, flow, link, stock, text_node  # noqa: E402

from chapters.chapter_34_hospital_hybrid.code.hospital import (  # noqa: E402
    DEFAULT_GROUPS,
    StaffingPolicy,
)


def main():
    groups = {g.name: g for g in DEFAULT_GROUPS}
    assert set(groups) == {"routine", "complex"}
    assert groups["routine"].share == 0.75 and groups["complex"].share == 0.25
    policy = StaffingPolicy()

    fig, ax = figure(height_in=2.7)
    ax.set_xlim(-0.1, 9.9)
    ax.set_ylim(-0.2, 4.45)
    ax.set_aspect("equal")
    ax.axis("off")

    # Left: aggregate staffing, continuous.
    boundary(ax, 0.05, 0.05, 4.05, 4.2, "aggregate staffing, continuous")
    stock(ax, 2.05, 2.9, "staff", w=1.5,
          sublabel=f"{policy.min_staff:.0f} to {policy.max_staff:.0f}")
    cloud(ax, 0.55, 2.9)
    flow(ax, (0.85, 2.9), (1.3, 2.9), valve=True)
    ax.text(0.55, 2.5, "adjust", ha="center", va="top", fontsize=5.8, style="italic")
    auxiliary(ax, 1.4, 1.35, "target\nwait", r=0.36, fontsize=6.0)
    auxiliary(ax, 2.9, 1.35, "adjust\ntime", r=0.36, fontsize=6.0)
    ax.text(1.4, 0.75, f"{policy.target_wait:.0f} period", ha="center", va="center", fontsize=6.0)
    ax.text(2.9, 0.75, f"{policy.adjustment_time:.0f} periods", ha="center", va="center",
            fontsize=6.0)
    link(ax, (1.4, 1.35), (1.07, 2.9), None, curve=0.0, shrinkA=13, shrinkB=5)
    link(ax, (2.9, 1.35), (1.07, 2.9), None, curve=-0.35, shrinkA=13, shrinkB=5)

    # Right: discrete patients, a queue of individuals in two groups.
    boundary(ax, 5.85, 0.05, 9.85, 4.2, "patient queue, discrete")
    cloud(ax, 6.35, 2.9)
    flow(ax, (6.65, 2.9), (7.1, 2.9), valve=False)
    stock(ax, 7.85, 2.9, "queue", w=1.5, sublabel="arrival, group")
    flow(ax, (8.6, 2.9), (9.05, 2.9), valve=True)
    cloud(ax, 9.35, 2.9)
    ax.text(6.85, 2.45, "arrivals", ha="center", va="top", fontsize=5.8, style="italic")
    ax.text(8.85, 2.45, "served", ha="center", va="top", fontsize=5.8, style="italic")
    for i, name in enumerate(("routine", "complex")):
        g = groups[name]
        text_node(ax, 6.9 + 1.9 * i, 1.35,
                  f"{name}\n{g.share:.0%} of arrivals\nservice x{g.service_multiplier:g}",
                  fontsize=5.8)
    ax.text(7.85, 0.5, "one wait per patient", ha="center", va="center", fontsize=6.0,
            style="italic")

    # The seam: a per-period service limit goes right, one statistic comes back.
    ax.annotate("", xy=(5.85, 3.35), xytext=(4.05, 3.35),
                arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color="black",
                                mutation_scale=9))
    ax.text(4.95, 3.5, "capacity\n(service limit)", ha="center", va="bottom", fontsize=6.0)
    ax.annotate("", xy=(4.05, 2.1), xytext=(5.85, 2.1),
                arrowprops=dict(arrowstyle="-|>", linewidth=1.0, color="black",
                                mutation_scale=9))
    ax.text(4.95, 1.95, "served mean wait\n(alternative:\ncomplex p90)",
            ha="center", va="top", fontsize=6.0)
    ax.text(4.95, 4.3, "the seam", ha="center", va="center", fontsize=6.4, style="italic")

    fig.tight_layout()
    save(fig, "hybrid-boundary")


if __name__ == "__main__":
    main()
