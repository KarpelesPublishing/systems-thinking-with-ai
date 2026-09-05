#!/usr/bin/env python3
"""Chapter 12, "Two stocks, coupled": backlog and inventory joined by one shipment rate.

The chapter builds the warehouse pair from Chapter 5: orders arrive from a source into backlog,
production arrives from a source into inventory, and one shipment rate leaves inventory to a sink
while reducing backlog. This figure draws that structure with the pack's own System so the names
come from code, and asserts the pack's check() finds nothing wrong with it.

    uv run --group figures python build/figures/fig_two_stocks_coupled.py

No numeric data. Placement of the two rows and the dotted tie between the two shipment valves is a
layout choice; the stocks, flows, endpoints, and units are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, flow, stock  # noqa: E402

from chapters.chapter_12_stocks_flows.code.system import SINK, SOURCE, Flow, System  # noqa: E402


def main():
    warehouse = System(
        stocks={"backlog": 0.0, "inventory": 100.0},
        flows=[Flow("orders", SOURCE, "backlog", "units/week"),
               Flow("shipments", "backlog", SINK, "units/week"),
               Flow("production", SOURCE, "inventory", "units/week"),
               Flow("shipments", "inventory", SINK, "units/week")],
        unit="units",
    )
    assert warehouse.check() == [], warehouse.check()
    names = {f.name for f in warehouse.flows}
    assert names == {"orders", "shipments", "production"}

    fig, ax = figure(height_in=2.35)
    ax.set_xlim(-0.2, 8.6)
    ax.set_ylim(-1.55, 1.55)
    ax.set_aspect("equal")
    ax.axis("off")

    for y, name, inflow in ((0.95, "backlog", "orders"), (-0.95, "inventory", "production")):
        cloud(ax, 0.55, y)
        stock(ax, 4.2, y, name, w=2.0, h=0.7, sublabel="units")
        cloud(ax, 7.85, y)
        flow(ax, (0.9, y), (3.15, y), label=inflow)
        flow(ax, (5.25, y), (7.5, y), label="shipments")
    ax.plot([6.375, 6.375], [0.78, -0.78], color="black", linewidth=0.7,
            linestyle=(0, (1.2, 1.4)), zorder=1)
    ax.text(6.55, 0.0, "one rate,\ntwo endpoints", ha="left", va="center", fontsize=6.0,
            style="italic")
    ax.text(0.55, 0.42, "source", ha="center", va="center", fontsize=6.0)
    ax.text(0.55, -1.48, "source", ha="center", va="center", fontsize=6.0)
    ax.text(7.85, 0.42, "sink", ha="center", va="center", fontsize=6.0)
    ax.text(7.85, -1.48, "sink", ha="center", va="center", fontsize=6.0)

    fig.tight_layout()
    save(fig, "two-stocks-coupled")


if __name__ == "__main__":
    main()
