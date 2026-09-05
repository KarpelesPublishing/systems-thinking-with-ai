#!/usr/bin/env python3
"""Chapter 29, "Ranking by what it costs to find out": the same three uncertainties ranked twice.

The chapter ranks three uncertain parameters of the Bass model by their one-at-a-time swing in
final adopters, total_market 572.1, imitation 526.3, innovation 127.2, then divides each swing by
what it would cost to reduce it and the ranking reverses: innovation 127.2, imitation 105.3,
total_market 28.6. This figure draws the two rankings as two panels of horizontal bars, largest
at the top of each, so the reversal is visible.

    uv run --group figures python build/figures/fig_sensitivity_ranking.py

Data: chapters.chapter_29_experiments.code.sensitivity.ranked(document, uncertainties,
"adopters") and value_per_cost(document, uncertainties, "adopters") on Chapter 22's Bass
document, with Uncertainty("total_market", 700, 1300, cost_to_reduce=20.0),
Uncertainty("imitation", 0.10, 0.50, cost_to_reduce=5.0) and Uncertainty("innovation", 0.005,
0.02, cost_to_reduce=1.0). The chapter does not print the ranges and costs; these are the ones
in the pack's tests, with imitation's range and cost being the values that reproduce the printed
numbers exactly. Both rankings are asserted to one decimal before anything is drawn.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import grid_figure, save  # noqa: E402

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable  # noqa: E402
from chapters.chapter_29_experiments.code.sensitivity import (  # noqa: E402
    Uncertainty,
    ranked,
    value_per_cost,
)


def bass() -> ModelDocument:
    return ModelDocument("bass", "1.0.0", horizon=40, variables=[
        Variable("adopters", "stock", "people", value=1.0),
        Variable("total_market", "parameter", "people", value=1000.0),
        Variable("innovation", "parameter", "1/week", value=0.01),
        Variable("imitation", "parameter", "1/week", value=0.30),
        Variable("potential", "auxiliary", "people", "total_market - adopters"),
        Variable("adoption", "flow", "people/week",
                 "(innovation + imitation * adopters / total_market) * potential",
                 target="adopters", sign=1),
    ])


def main():
    uncertainties = [
        Uncertainty("total_market", 700, 1300, cost_to_reduce=20.0),
        Uncertainty("imitation", 0.10, 0.50, cost_to_reduce=5.0),
        Uncertainty("innovation", 0.005, 0.02, cost_to_reduce=1.0),
    ]
    by_effect = ranked(bass(), uncertainties, "adopters")
    by_value = value_per_cost(bass(), uncertainties, "adopters")
    assert [(n, round(v, 1)) for n, v in by_effect] == [
        ("total_market", 572.1), ("imitation", 526.3), ("innovation", 127.2)], by_effect
    assert [(n, round(v, 1)) for n, v in by_value] == [
        ("innovation", 127.2), ("imitation", 105.3), ("total_market", 28.6)], by_value

    fig, (left, right) = grid_figure(1, 2, height_in=2.0)
    panels = (
        (left, by_effect, "swing in final adopters", 700),
        (right, by_value, "swing per unit of cost to reduce", 160),
    )
    for ax, rows, xlabel, xmax in panels:
        names = [n for n, _ in rows][::-1]
        values = [v for _, v in rows][::-1]
        ax.barh(names, values, color="black", height=0.55)
        for i, v in enumerate(values):
            ax.text(v + xmax * 0.02, i, f"{v:.1f}", va="center", ha="left", fontsize=6.5)
        ax.set_xlim(0, xmax)
        ax.set_xlabel(xlabel)
        ax.tick_params(axis="y", length=0)
    left.set_title("ranked by effect", fontsize=7.5, loc="left")
    right.set_title("ranked by value per cost", fontsize=7.5, loc="left")

    fig.tight_layout(w_pad=1.6)
    save(fig, "sensitivity-ranking")


if __name__ == "__main__":
    main()
