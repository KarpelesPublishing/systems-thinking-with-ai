#!/usr/bin/env python3
"""Chapter 21, "Edges from the equations": the factory document's derived dependency graph.

The chapter derives the graph from the equations with `edges(document)` on the factory model
Chapter 20 wrote down (inventory, order_rate, coverage, desired_inventory, gap, production), and
then orders it: ['coverage', 'order_rate', 'desired_inventory', 'gap', 'production'], with the
stock absent because it is state. This figure draws exactly that graph, one thin arrow per
derived edge from the variable read to the variable that reads it, nodes layered left to right
by their place in `evaluation_order`, the stock drawn as a rectangle below the layers, and the
flow's `target` link drawn as a thick flow arrow, which is where the model's one feedback loop
closes. The loop is marked B. There is no algebraic loop to mark: `algebraic_loops` returns [].

    uv run --group figures python build/figures/fig_dependency_graph.py

Data: chapters.chapter_21_compiler.code.compiler.edges, evaluation_order, feedback_loops and
algebraic_loops on the factory document, built as tests/chapters/test_dependency_compiler.py
builds it. Node positions and arc curvatures are layout choices; the node names, the edge set,
the order, and the loop are the pack's. The script asserts the drawn edge set equals
edges(document) before saving. Width is 5.0in rather than 4.4in so the long variable names do
not collide.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import flow, link, loop_id, stock, text_node  # noqa: E402

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable  # noqa: E402
from chapters.chapter_21_compiler.code.compiler import (  # noqa: E402
    algebraic_loops,
    edges,
    evaluation_order,
    feedback_loops,
)


def factory() -> ModelDocument:
    return ModelDocument("factory", "1.0.0", [
        Variable("inventory", "stock", "units", value=12.0),
        Variable("order_rate", "parameter", "units/week", value=10.0),
        Variable("coverage", "parameter", "week", value=2.0),
        Variable("desired_inventory", "auxiliary", "units", "order_rate * coverage"),
        Variable("gap", "auxiliary", "units", "desired_inventory - inventory"),
        Variable("production", "flow", "units/week", "order_rate + gap / coverage",
                 target="inventory", sign=1),
    ])


def main():
    document = factory()
    graph = edges(document)
    order = evaluation_order(document)
    assert order == ["coverage", "order_rate", "desired_inventory", "gap", "production"], order
    assert algebraic_loops(document) == [], algebraic_loops(document)
    assert feedback_loops(document) == [["gap", "production", "inventory"]]

    # (reader, read) pairs the figure draws, one per arrow, plus the curvature of each arc.
    drawn = {
        ("desired_inventory", "coverage"): 0.0,
        ("desired_inventory", "order_rate"): 0.0,
        ("gap", "desired_inventory"): 0.0,
        ("gap", "inventory"): 0.0,
        ("production", "gap"): 0.0,
        ("production", "order_rate"): 0.0,
        ("production", "coverage"): -0.38,
    }
    assert set(drawn) == {(reader, read) for reader, reads in graph.items() for read in reads}

    fig, ax = figure(height_in=2.5, width_in=5.0)
    ax.set_xlim(-0.6, 9.0)
    ax.set_ylim(-2.35, 2.6)
    ax.set_aspect("equal")
    ax.axis("off")

    pos = {
        "coverage": (0.5, 1.0),
        "order_rate": (0.5, -0.6),
        "desired_inventory": (2.9, 1.0),
        "gap": (5.1, 1.0),
        "production": (7.5, 0.2),
        "inventory": (5.1, -1.35),
    }
    for name, (x, y) in pos.items():
        if name == "inventory":
            stock(ax, x, y, name, w=1.5, h=0.6)
        else:
            text_node(ax, x, y, name)

    # Half extents of each label, so an arrow starts and ends at the text's edge.
    half = {"coverage": (0.55, 0.16), "order_rate": (0.62, 0.16), "desired_inventory": (1.0, 0.16),
            "gap": (0.25, 0.16), "production": (0.62, 0.16), "inventory": (0.75, 0.30)}

    def edge_point(name, toward):
        (x, y), (hw, hh) = pos[name], half[name]
        dx, dy = toward[0] - x, toward[1] - y
        scale = min(hw / abs(dx) if dx else 9e9, hh / abs(dy) if dy else 9e9)
        return (x + dx * scale, y + dy * scale)

    for (reader, read), curve in drawn.items():
        a = edge_point(read, pos[reader])
        b = edge_point(reader, pos[read])
        if (reader, read) == ("production", "coverage"):
            b = (pos["production"][0] - 0.2, pos["production"][1] + 0.16)  # arrive from above
        link(ax, a, b, polarity="", curve=curve, shrinkA=2.0, shrinkB=2.5)

    # The flow reaches its stock through the target field, not an equation.
    flow(ax, (7.3, -0.05), (5.95, -1.15), shrinkA=4.0)
    ax.text(7.35, -0.95, "target", ha="left", va="center", fontsize=6.8)
    loop_id(ax, 6.0, -0.5, "B", direction="ccw", r=0.26)

    ax.text(0.5, 1.75, "parameters", ha="center", va="center", fontsize=6.2, style="italic")
    ax.text(0.5, -1.35, "read nothing", ha="center", va="center", fontsize=6.2, style="italic")
    ax.text(5.1, -1.95, "state: read, not evaluated", ha="center", va="center", fontsize=6.2,
            style="italic")
    ax.text(4.2, 2.4, "evaluation order, left to right: " + ", ".join(order),
            ha="center", va="center", fontsize=6.2)

    fig.tight_layout()
    save(fig, "dependency-graph")


if __name__ == "__main__":
    main()
