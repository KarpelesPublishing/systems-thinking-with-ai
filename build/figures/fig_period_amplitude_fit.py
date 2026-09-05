#!/usr/bin/env python3
"""Chapter 38, "Capacity Arrives When the Price Has Gone": period and amplitude against the delay.

The chapter sweeps the construction delay from twelve to forty-eight months with the other fitted
values held, and reads the model's period off the sweep: 76, 93, 105, 114, 123, and 127 months at
delays of 12, 18, 24, 30, 36, and 48, with the amplitude staying between 16.7 and 19.4 points
throughout. The record's period is 90 and its amplitude 18.0; the fit's tolerances are twenty
percent on the period and twenty-five on the amplitude. This figure plots the sweep against those
bands:

    uv run --group figures python build/figures/fig_period_amplitude_fit.py

Data: chapters.chapter_38_capacity_cycle.code.calibrate.construction_delay_sweep. The asserts pin
the numbers the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib.pyplot as plt  # noqa: E402
from figstyle import DASHES, STYLE, save  # noqa: E402

from chapters.chapter_38_capacity_cycle.code import calibrate as c  # noqa: E402


def main():
    sweep = c.construction_delay_sweep()
    delays = [r["construction_delay"] for r in sweep]
    periods = [r["period"] for r in sweep]
    amplitudes = [r["amplitude"] for r in sweep]
    record = list(c.record().values)
    record_period, record_amplitude = c.cycle_period(record), c.amplitude(record)

    # The numbers the chapter prints.
    assert periods == [76, 93, 105, 114, 123, 127]
    assert [round(a, 1) for a in amplitudes] == [17.2, 18.1, 19.4, 19.2, 18.7, 16.7]
    assert (record_period, round(record_amplitude, 1)) == (90, 18.0)
    assert c.PINNED_FIT["construction_delay"] == 18.0

    plt.rcParams.update(STYLE)
    fig, (top, bottom) = plt.subplots(2, 1, figsize=(4.4, 3.2), sharex=True,
                                      gridspec_kw={"hspace": 0.14})
    for ax, values, target, tol, label, ticks in (
        (top, periods, record_period, c.PERIOD_TOLERANCE, "period, months", [60, 90, 120]),
        (bottom, amplitudes, record_amplitude, c.AMPLITUDE_TOLERANCE, "amplitude, points",
         [12, 15, 18, 21, 24]),
    ):
        ax.axhspan(target * (1 - tol), target * (1 + tol), facecolor="black", alpha=0.07,
                   linewidth=0)
        ax.axhline(target, color="black", linewidth=0.5, linestyle=DASHES[2])
        ax.plot(delays, values, color="black", linestyle=DASHES[0], marker="o", markersize=2.6)
        ax.plot([18.0], [values[1]], color="black", marker="s", markersize=4.5, linestyle="none")
        ax.set_ylabel(label)
        ax.set_yticks(ticks)
    top.set_ylim(55, 135)
    bottom.set_ylim(11, 25)
    top.text(48.5, record_period + 1.5, "record 90", fontsize=6.4, ha="right", va="bottom")
    top.text(48.5, record_period * (1 + c.PERIOD_TOLERANCE) + 1.0, "tolerance band",
             fontsize=6.0, ha="right", va="bottom", style="italic")
    bottom.text(48.5, record_amplitude + 0.4, "record 18.0", fontsize=6.4, ha="right",
                va="bottom")
    top.annotate("fitted, 18 months", xy=(18.0, periods[1]), xytext=(22.0, 70.0), fontsize=6.4,
                 ha="left", arrowprops=dict(arrowstyle="-", linewidth=0.5, color="black"))
    bottom.set_xlabel("construction delay, months")
    bottom.set_xticks([12, 18, 24, 30, 36, 48])
    bottom.set_xlim(9, 51)
    save(fig, "period-amplitude-fit")


if __name__ == "__main__":
    main()
