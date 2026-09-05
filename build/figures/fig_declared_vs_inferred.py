#!/usr/bin/env python3
"""Chapter 21, "Two cycles, opposite treatment": feedback through a stock beside an algebraic loop.

The chapter puts two cycles side by side. In the factory document, gap feeds production,
production changes inventory through its target, and inventory feeds gap: a cycle that passes
through a stock, so it closes over a time step and `algebraic_loops(factory)` returns []. In the
broken document, p reads q and q reads p with nothing stateful between them:
`algebraic_loops(broken)` returns [['p', 'q']] and the compiler refuses to order it. The chapter
also compares a declared edge list with the derived one on the factory,
`declared_versus_inferred(document, declared={"gap": {"order_rate"}})`, and this script pins
that report too, because the left-hand cycle is drawn from the derived edges, not from anything
anyone declared.

    uv run --group figures python build/figures/fig_declared_vs_inferred.py

Data: chapters.chapter_21_compiler.code.compiler.algebraic_loops on the factory and the looped
documents as tests/chapters/test_dependency_compiler.py builds them, and
declared_versus_inferred on the factory. Placement is a layout choice; the node names, the
edges, and the two results are the pack's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import link, loop_id, stock, text_node  # noqa: E402

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable  # noqa: E402
from chapters.chapter_21_compiler.code.compiler import (  # noqa: E402
    algebraic_loops,
    declared_versus_inferred,
    edges,
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


def looped() -> ModelDocument:
    return ModelDocument("bad", "0.1.0", [
        Variable("a", "stock", "x", value=1.0),
        Variable("p", "auxiliary", "x", "q + 1"),
        Variable("q", "auxiliary", "x", "p * 2"),
    ])


def main():
    good, broken = factory(), looped()
    assert algebraic_loops(good) == []
    assert algebraic_loops(broken) == [["p", "q"]]
    report = declared_versus_inferred(good, declared={"gap": {"order_rate"}})
    assert {k: sorted(v) for k, v in report.items()} == {
        "desired_inventory": ["coverage", "order_rate"],
        "gap": ["desired_inventory", "inventory", "order_rate"],
        "production": ["coverage", "gap", "order_rate"],
    }, report
    # The two edges the left-hand cycle draws from equations, and the target link.
    assert "gap" in edges(good)["production"] and "inventory" in edges(good)["gap"]
    assert good.by_id("production").target == "inventory"
    # Both edges of the right-hand cycle.
    assert edges(broken)["p"] == {"q"} and edges(broken)["q"] == {"p"}

    fig, ax = figure(height_in=1.95)
    ax.set_xlim(-0.4, 9.9)
    ax.set_ylim(-2.15, 1.55)
    ax.set_aspect("equal")
    ax.axis("off")

    # Left: feedback through a stock.
    text_node(ax, 0.7, 0.9, "gap")
    text_node(ax, 3.4, 0.9, "production")
    stock(ax, 2.05, -0.75, "inventory", w=1.5, h=0.6)
    link(ax, (0.95, 0.9), (2.75, 0.9), polarity="", curve=0.0, shrinkA=2.0, shrinkB=2.0)
    link(ax, (3.25, 0.72), (2.6, -0.45), polarity="", curve=0.0, shrinkA=2.0, shrinkB=2.0,
         lw=1.4)
    ax.text(3.15, 0.1, "target", ha="left", va="center", fontsize=6.6, style="italic")
    link(ax, (1.45, -0.45), (0.8, 0.72), polarity="", curve=0.0, shrinkA=2.0, shrinkB=2.0)
    loop_id(ax, 2.05, 0.2, "B", direction="ccw", r=0.24)
    ax.text(2.05, -1.45, "closes over a time step", ha="center", va="center", fontsize=6.6,
            style="italic")
    ax.text(2.05, -1.85, "algebraic_loops(factory) = []", ha="center", va="center",
            fontsize=5.8, family="monospace")

    ax.plot([4.85, 4.85], [-2.0, 1.4], color="black", linewidth=0.5, linestyle=(0, (3.0, 2.0)))

    # Right: an algebraic loop, nothing stateful in it.
    text_node(ax, 6.4, 0.1, "p")
    text_node(ax, 8.4, 0.1, "q")
    link(ax, (6.55, 0.2), (8.25, 0.2), polarity="", curve=-0.5, shrinkA=2.0, shrinkB=2.0)
    link(ax, (8.25, 0.0), (6.55, 0.0), polarity="", curve=-0.5, shrinkA=2.0, shrinkB=2.0)
    ax.text(7.4, 0.95, "q = p * 2", ha="center", va="center", fontsize=6.6, style="italic")
    ax.text(7.4, -0.75, "p = q + 1", ha="center", va="center", fontsize=6.6, style="italic")
    ax.text(7.4, -1.45, "no state between them: refused", ha="center", va="center",
            fontsize=6.6, style="italic")
    ax.text(7.4, -1.85, "algebraic_loops(broken) = [['p', 'q']]", ha="center", va="center",
            fontsize=5.8, family="monospace")

    fig.tight_layout()
    save(fig, "declared-vs-inferred")


if __name__ == "__main__":
    main()
