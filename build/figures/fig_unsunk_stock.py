#!/usr/bin/env python3
"""Chapter 12, "The failure worth engineering for": a stock with an inflow and no outflow.

The chapter removes the bathtub's drain and runs check(), which returns the message
"stock 'tub' has no outflow: it can only grow". This figure draws the structure the validator
refuses and prints the validator's own message under it. The message is asserted against the
pack before the figure is saved.

    uv run --group figures python build/figures/fig_unsunk_stock.py

No numeric data. Placement is a layout choice; the structure and the message are the pack's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, flow, stock  # noqa: E402

from chapters.chapter_12_stocks_flows.code.system import SOURCE, Flow, System  # noqa: E402

MESSAGE = "stock 'tub' has no outflow: it can only grow"


def main():
    unsunk = System(stocks={"tub": 50.0},
                    flows=[Flow("tap", SOURCE, "tub", "litres/minute")],
                    unit="litres")
    assert unsunk.check() == [MESSAGE], unsunk.check()
    assert unsunk.unsunk_stocks() == ["tub"]

    fig, ax = figure(height_in=1.7)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.1, 1.0)
    ax.set_aspect("equal")
    ax.axis("off")

    cloud(ax, 0.55, 0.0)
    stock(ax, 4.2, 0.0, "tub", w=2.4, h=0.8, sublabel="litres, 50 at start")
    flow(ax, (0.9, 0.0), (2.95, 0.0), label="tap")
    ax.text(0.55, -0.55, "source", ha="center", va="center", fontsize=6.2)
    ax.text(1.92, -0.42, "litres per minute", ha="center", va="center", fontsize=6.2,
            style="italic")
    ax.text(6.9, 0.0, "no drain", ha="center", va="center", fontsize=6.6, style="italic")
    ax.text(4.2, -0.9, f"check()  returns  [{MESSAGE!r}]", ha="center", va="center",
            fontsize=6.2, family="monospace")

    fig.tight_layout()
    save(fig, "unsunk-stock")


if __name__ == "__main__":
    main()
