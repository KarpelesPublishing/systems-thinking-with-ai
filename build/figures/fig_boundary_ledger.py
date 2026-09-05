#!/usr/bin/env python3
"""Chapter 40, "What the boundary ledger holds": inside, outside, and what moved across, and when.

The chapter's contract puts intake, workforce, experience, quality, and churn inside the boundary
and price, competitors, product roadmap, and seasonality outside. The ledger holds six exclusions,
five of which the chapter reproduces with a reason and a direction of error, and a record of three
quantities that moved:
the training ramp from unstatable to observed once HR records were read, the churn sensitivity
from assumed toward inferred two quarters later, the training loop from excluded to inside after
the pilot's week-six divergence. Seasonality is not among them: it is on its second round without a
test, still outside, due to be reclassified from believed immaterial to an assumption if that round
brings none. This figure draws the three columns.

    uv run --group figures python build/figures/fig_boundary_ledger.py

No numeric data. Placement is a layout choice; every entry is transcribed from the chapter. The
asserts check the transcription against the contract's two lists.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from sdvocab import boundary  # noqa: E402

INSIDE = ["intake", "workforce", "experience", "quality", "churn"]
OUTSIDE = [
    ("price", "politically fixed"),
    ("competitors", "out of scope; error optimistic"),
    ("product roadmap", "out of scope"),
    ("seasonality", "believed immaterial, untested"),
    ("training load on seniors", "no data; error optimistic"),
    ("referral after churn", "structural; error pessimistic"),
]
MOVED = [
    ("training ramp", "unstatable to observed,\nHR records, first pass"),
    ("churn sensitivity", "assumed toward inferred,\ntwo quarters of paired data"),
    ("training loop", "excluded to inside,\nafter week six of the pilot"),
]


def main():
    assert INSIDE == ["intake", "workforce", "experience", "quality", "churn"]
    assert [name for name, _ in OUTSIDE[:4]] == ["price", "competitors", "product roadmap",
                                                 "seasonality"]
    # Seasonality is still outside: the chapter says it is believed immaterial and untested, on
    # its second round without a test. A quantity is in Moved only once it has actually crossed.
    moved = {name for name, _ in MOVED}
    assert "seasonality" not in moved and len(MOVED) == 3, moved

    fig, ax = figure(height_in=3.0)
    ax.set_xlim(-0.1, 10.1)
    ax.set_ylim(-0.2, 5.4)
    ax.set_aspect("equal")
    ax.axis("off")

    cols = [(0.0, 2.5, "inside the boundary"), (2.75, 6.35, "outside, with the reason"),
            (6.6, 10.0, "moved, and when")]
    for x0, x1, title in cols:
        boundary(ax, x0, 0.0, x1, 5.3, "")
        ax.text((x0 + x1) / 2, 5.0, title, ha="center", va="center", fontsize=7.0,
                weight="bold")
        ax.plot([x0 + 0.1, x1 - 0.1], [4.72, 4.72], color="black", linewidth=0.5)

    for i, name in enumerate(INSIDE):
        ax.text(1.25, 4.25 - i * 0.78, name, ha="center", va="center", fontsize=7.0)

    for i, (name, reason) in enumerate(OUTSIDE):
        y = 4.3 - i * 0.72
        ax.text(2.9, y, name, ha="left", va="center", fontsize=6.6)
        ax.text(2.9, y - 0.27, reason, ha="left", va="center", fontsize=5.4, style="italic")

    for i, (name, when) in enumerate(MOVED):
        y = 4.3 - i * 1.08
        ax.text(6.75, y, name, ha="left", va="center", fontsize=6.6)
        ax.text(6.75, y - 0.36, when, ha="left", va="center", fontsize=5.4, style="italic")

    fig.tight_layout()
    save(fig, "boundary-ledger")


if __name__ == "__main__":
    main()
