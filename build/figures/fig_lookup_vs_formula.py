#!/usr/bin/env python3
"""Chapter 15, "Two ways to hold a bend": a lookup and a degree-five fit on six points.

Inside the observed domain the two agree (0.690 against 0.699 at a load of 2.5). Asked about a
load of twelve, the lookup raises OutsideDomain and the fit returns 47.76 for a quantity bounded
between zero and one. This figure plots both over the observed domain, extends the polynomial
past it dashed, and marks where the lookup refuses.

    uv run --group figures python build/figures/fig_lookup_vs_formula.py

Data: chapters.chapter_15_lookups.code.lookup with points
[(0, 0), (1, 0.35), (2, 0.6), (3, 0.78), (4, 0.88), (5, 0.93)]: Lookup(points, "saturation") and
evaluate_polynomial(fit_polynomial(points, 5), x). The inset showing the observed domain at its
own scale is a layout choice; the numbers are the chapter's.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_15_lookups.code.lookup import (  # noqa: E402
    Lookup,
    OutsideDomain,
    evaluate_polynomial,
    fit_polynomial,
)

POINTS = [(0, 0), (1, 0.35), (2, 0.6), (3, 0.78), (4, 0.88), (5, 0.93)]


def main():
    saturation = Lookup(POINTS, "saturation")
    coefficients = fit_polynomial(POINTS, 5)
    assert round(saturation(2.5), 3) == 0.690, saturation(2.5)
    assert round(evaluate_polynomial(coefficients, 2.5), 3) == 0.699
    at_twelve = evaluate_polynomial(coefficients, 12.0)
    assert round(at_twelve, 2) == 47.76, at_twelve
    refused = False
    try:
        saturation(12.0)
    except OutsideDomain:
        refused = True
    assert refused

    inside = [i / 50 for i in range(0, 251)]
    outside = [5 + i / 50 for i in range(0, 351)]
    fig, ax = figure(height_in=2.7)
    ax.plot(inside, [evaluate_polynomial(coefficients, x) for x in inside], color="black",
            linestyle=DASHES[0])
    ax.plot(outside, [evaluate_polynomial(coefficients, x) for x in outside], color="black",
            linestyle=DASHES[1])
    ax.plot(inside, [saturation(x) for x in inside], color="black", linestyle=DASHES[2])
    ax.axvline(5, color="black", linewidth=0.5, linestyle=DASHES[2])
    ax.plot([12], [at_twelve], marker="o", color="black", markersize=3)
    ax.set_xlim(0, 12.6)
    ax.set_ylim(-2, 52)
    ax.set_xlabel("load")
    ax.set_ylabel("effectiveness")
    ax.text(11.8, at_twelve, f"fit at 12.0: {at_twelve:.2f}", fontsize=6.5, ha="right",
            va="center")
    ax.text(5.2, 16, "lookup refuses\nbeyond 5: OutsideDomain", fontsize=6.5, ha="left",
            va="center")
    ax.text(8.6, 6.0, "degree-5 fit,\npast the data", fontsize=6.5, ha="left", va="bottom")
    ax.text(2.5, 4.5, "bounded between 0 and 1:\nsee inset", fontsize=6.2, ha="center",
            va="bottom", style="italic")

    inset = ax.inset_axes([0.13, 0.52, 0.32, 0.40])
    inset.plot(inside, [evaluate_polynomial(coefficients, x) for x in inside], color="black",
               linestyle=DASHES[0])
    inset.plot(inside, [saturation(x) for x in inside], color="black", linestyle=DASHES[2])
    inset.plot([x for x, _ in POINTS], [y for _, y in POINTS], linestyle="none", marker="o",
               color="black", markersize=2.2)
    inset.set_xlim(0, 5)
    inset.set_ylim(0, 1.05)
    inset.set_xticks([0, 5])
    inset.set_yticks([0, 1])
    inset.tick_params(labelsize=6)
    inset.set_title("observed domain: fit solid, lookup dotted", fontsize=6, pad=2)

    fig.tight_layout()
    save(fig, "lookup-vs-formula")


if __name__ == "__main__":
    main()
