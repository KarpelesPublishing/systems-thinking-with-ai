#!/usr/bin/env python3
"""Chapter 3, "Six shapes worth recognizing": the six reference modes as small multiples.

The chapter names growth, decay, goal seeking, oscillation, S-shaped growth, and overshoot and
collapse, and its "Generating the six shapes" section builds them from the pack's reference-mode
library. This figure draws one path per shape, two rows of three, in the order the chapter's table
lists them:

    uv run --group figures python build/figures/fig_six_shapes.py

Data: chapters.chapter_03_reference_modes.code.modes. The S-shaped and overshoot parameters are the
ones the chapter prints (s_shaped_growth(initial=1.0, capacity=100.0, rate=0.3, steps=120) and
overshoot_and_collapse(initial=1.0, capacity=100.0, rate=0.4, erosion_rate=0.02, steps=200)), and
goal_seeking(initial=0.0, goal=100.0, adjustment_time=4.0, steps=60) is the chapter's noise
exercise. Growth, decay, and oscillation parameters are a layout choice, picked so each panel shows
its shape at a readable scale. Axis ticks are left off: the shapes, not the magnitudes, are the
subject. The asserts pin the first and last value of every path.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import grid_figure, save  # noqa: E402

from chapters.chapter_03_reference_modes.code.modes import (  # noqa: E402
    exponential_decay,
    exponential_growth,
    goal_seeking,
    oscillation,
    overshoot_and_collapse,
    s_shaped_growth,
)


def main():
    shapes = [
        ("growth", exponential_growth(initial=1.0, rate=0.05, steps=60)),
        ("decay", exponential_decay(initial=100.0, rate=0.05, steps=60)),
        ("goal seeking", goal_seeking(initial=0.0, goal=100.0, adjustment_time=4.0, steps=60)),
        ("oscillation", oscillation(level=50.0, amplitude=20.0, period=20.0, steps=60)),
        ("S-shaped growth", s_shaped_growth(initial=1.0, capacity=100.0, rate=0.3, steps=120)),
        ("overshoot and collapse",
         overshoot_and_collapse(initial=1.0, capacity=100.0, rate=0.4, erosion_rate=0.02,
                                steps=200)),
    ]
    ends = {name: (round(p[0], 3), round(p[-1], 3)) for name, p in shapes}
    assert ends["growth"] == (1.0, 18.679), ends["growth"]
    assert ends["decay"] == (100.0, 4.607), ends["decay"]
    assert ends["goal seeking"] == (0.0, 100.0), ends["goal seeking"]
    assert ends["oscillation"] == (50.0, 50.0), ends["oscillation"]
    assert ends["S-shaped growth"] == (1.0, 100.0), ends["S-shaped growth"]
    assert ends["overshoot and collapse"] == (1.0, 1.986), ends["overshoot and collapse"]
    assert round(max(shapes[5][1]), 1) == 87.6

    fig, axes = grid_figure(2, 3, height_in=2.7)
    for ax, (name, path) in zip(axes.flat, shapes, strict=True):
        ax.plot(range(len(path)), path, color="black")
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylim(-0.05 * max(path), 1.18 * max(path))
        ax.set_title(name, fontsize=7.5, pad=2)
        ax.set_xlabel("time", fontsize=6.5, labelpad=1)
    fig.tight_layout(pad=0.3, w_pad=0.6, h_pad=0.5)
    save(fig, "six-shapes")


if __name__ == "__main__":
    main()
