#!/usr/bin/env python3
"""Chapter 38, "Capacity Arrives When the Price Has Gone": the record against the fitted model.

The chapter fits the capacity-cycle document to the 1990-01 to 2019-12 utilization record on two
statistics only, period and amplitude, and reports a model period of ninety-three months against
the record's ninety and a model amplitude of 18.1 points against the record's 18.0. This figure
overlays the two paths over the same 360 months. The model was never asked to land its peaks on
the record's peaks, and the overlay shows that it does not:

    uv run --group figures python build/figures/fig_record_vs_model_overlay.py

Data: chapters.chapter_38_capacity_cycle.code.calibrate.record and model_path at the pinned fit.
The asserts pin the numbers the chapter prints.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_38_capacity_cycle.code import calibrate as c  # noqa: E402


def main():
    record = list(c.record().values)
    model = c.model_path()
    months = list(range(len(record)))

    # The numbers the chapter prints.
    assert (c.cycle_period(record), round(c.amplitude(record), 1)) == (90, 18.0)
    assert (c.cycle_period(model), round(c.amplitude(model), 1)) == (93, 18.1)
    assert c.PINNED_FIT == {"investment_gain": 0.25, "margin_sensitivity": 0.8333,
                            "construction_delay": 18.0}
    assert round(sum(model) / len(model), 1) == 72.8

    fig, ax = figure(height_in=2.4)
    years = [1990 + m / 12 for m in months]
    ax.plot(years, record, color="black", linestyle=DASHES[0], linewidth=0.9)
    ax.plot(years, model[:len(record)], color="black", linestyle=DASHES[1], linewidth=0.9)
    ax.set_xlim(1990, 2020)
    ax.set_ylim(60, 90)
    ax.set_yticks([60, 70, 80, 90])
    ax.set_xticks([1990, 1995, 2000, 2005, 2010, 2015, 2020])
    ax.set_ylabel("utilization, percent")
    ax.set_xlabel("year")
    ax.text(1995.3, 86.2, "record, period 90, amplitude 18.0", fontsize=6.6, ha="left")
    ax.text(2010.3, 61.0, "model, period 93, amplitude 18.1", fontsize=6.6, ha="left")
    fig.tight_layout()
    save(fig, "record-vs-model-overlay")


if __name__ == "__main__":
    main()
