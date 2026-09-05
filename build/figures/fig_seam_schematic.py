#!/usr/bin/env python3
"""Chapter 18, "One boundary, declared": the seam between the aggregate side and the queue.

The chapter makes the interface an object: one variable, servers, goes down into the queue, and
two, mean_wait and queue_length, come back, each with a unit, at a stated exchange frequency.
This figure draws the two sides as boundaries with the crossing payloads between them. The
drawn keys and units are read from the pack's Interface and asserted equal to its declaration.

    uv run --group figures python build/figures/fig_seam_schematic.py

No numeric data. Placement is a layout choice; the payload keys, directions, and units are
the pack's Interface, which the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import boundary, link, stock, text_node  # noqa: E402

from chapters.chapter_18_hybrid.code.coupling import Interface  # noqa: E402

WHITE = dict(facecolor="white", edgecolor="none", pad=0.8)


def main():
    face = Interface(
        to_queue=("servers",),
        to_aggregate=("mean_wait", "queue_length"),
        units=(("servers", "clinicians"), ("mean_wait", "hours"),
               ("queue_length", "patients")),
        exchange_every=1,
    )
    down = [(k, face.unit_of(k)) for k in face.to_queue]
    up = [(k, face.unit_of(k)) for k in face.to_aggregate]
    assert tuple(k for k, _ in down) == face.to_queue == ("servers",)
    assert tuple(k for k, _ in up) == face.to_aggregate == ("mean_wait", "queue_length")
    assert dict(face.units) == {"servers": "clinicians", "mean_wait": "hours",
                                "queue_length": "patients"}

    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.9, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")

    boundary(ax, 0.0, -1.7, 2.9, 1.3, "aggregate side")
    stock(ax, 1.45, 0.05, "staff", w=1.6, h=0.7, sublabel="a continuous stock")
    text_node(ax, 1.45, -1.0, "steps in weeks,\nsees no patient", fontsize=6.0, style="italic")

    boundary(ax, 5.5, -1.7, 8.4, 1.3, "queue side")
    stock(ax, 6.95, 0.05, "waiting patients", w=1.9, h=0.7, sublabel="individuals, in order")
    text_node(ax, 6.95, -1.0, "resolves in hours,\nsees no policy", fontsize=6.0, style="italic")

    # the seam
    ax.plot([4.2, 4.2], [-1.75, 1.35], color="black", linewidth=0.9)
    text_node(ax, 4.2, 1.42, "the seam", fontsize=6.6)
    link(ax, (2.9, 0.65), (5.5, 0.65), polarity="", curve=0.0, shrinkA=2, shrinkB=2)
    ax.text(4.2, 0.85, ", ".join(f"{k} [{u}]" for k, u in down), ha="center", va="bottom",
            fontsize=6.3, family="monospace", bbox=WHITE)
    link(ax, (5.5, -0.55), (2.9, -0.55), polarity="", curve=0.0, shrinkA=2, shrinkB=2)
    ax.text(4.2, -0.75, "\n".join(f"{k} [{u}]" for k, u in up), ha="center", va="top",
            fontsize=6.3, family="monospace", bbox=WHITE)
    ax.text(4.2, 0.05, f"exchange every {face.exchange_every} period", ha="center", va="center",
            fontsize=6.0, style="italic", bbox=WHITE)

    fig.tight_layout()
    save(fig, "seam-schematic")


if __name__ == "__main__":
    main()
