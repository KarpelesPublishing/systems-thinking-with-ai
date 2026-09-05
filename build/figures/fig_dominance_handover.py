#!/usr/bin/env python3
"""Chapter 14, "The handover": each loop's knockout contribution over a forty-step run.

The chapter runs Diffusion(total_market=1000.0, innovation=0.01, imitation=0.30) for forty
steps and reports that word of mouth dominates first, saturation dominates last, and dominance
changes hands at step twelve. This figure plots the two contributions from `contributions` and
marks the crossover at `handover_step`.

    uv run --group figures python build/figures/fig_dominance_handover.py

Data: chapters.chapter_14_dominance.code.dominance.run(model, steps=40) with that model, then
contributions(model, path) and handover_step(model, path). The asserts pin the chapter's numbers.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_14_dominance.code.dominance import (  # noqa: E402
    BALANCING,
    REINFORCING,
    Diffusion,
    contributions,
    dominant_loop,
    handover_step,
    run,
)


def main():
    model = Diffusion(total_market=1000.0, innovation=0.01, imitation=0.30)
    path = run(model, steps=40)
    contrib = contributions(model, path)
    labels = dominant_loop(model, path)
    step = handover_step(model, path)
    assert labels[0] == REINFORCING and labels[-1] == BALANCING, (labels[0], labels[-1])
    assert step == 12, step

    r, b = contrib[REINFORCING], contrib[BALANCING]
    t = list(range(len(path)))
    fig, ax = figure(height_in=2.5)
    ax.plot(t, r, color="black", linestyle=DASHES[0])
    ax.plot(t, b, color="black", linestyle=DASHES[1])
    ax.axvline(step, color="black", linewidth=0.5, linestyle=DASHES[2])
    ax.set_xlim(0, 40)
    ax.set_ylim(0, 340)
    ax.set_xlabel("step")
    ax.set_ylabel("loop contribution (adopters per step)")
    ax.text(step + 0.7, 320, f"handover, step {step}", fontsize=6.5, ha="left", va="top")
    ax.text(9.0, r[9] + 14, REINFORCING, fontsize=6.8, ha="right", va="bottom")
    ax.text(20.5, b[20] - 6, BALANCING, fontsize=6.8, ha="left", va="top")

    fig.tight_layout()
    save(fig, "dominance-handover")


if __name__ == "__main__":
    main()
