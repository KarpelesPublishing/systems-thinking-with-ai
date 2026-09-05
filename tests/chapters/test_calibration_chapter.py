# ---------- Chapter 35 ----------
"""Pins every number the prose of Chapter 35 quotes, so a change to the pack cannot leave
the chapter behind. The fixtures are the chapter's own code blocks, verbatim."""

import pytest

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from chapters.chapter_28_critic.code.critic import (
    conservation_findings,
    extreme_condition_findings,
)
from chapters.chapter_35_calibration.code.calibrate import (
    Knob,
    Series,
    Target,
    error_of,
    fit_report,
    grid_fit,
    holdout,
    with_fitted,
)


def tank(rate: float = 0.1) -> ModelDocument:
    """The chapter's tank: constant inflow, proportional outflow, one rate nobody measured."""
    return ModelDocument(
        name="tank", version="1.0.0", horizon=36, horizon_unit="month", time_step=1.0,
        variables=[
            Variable("level", "stock", "units", value=100.0, evidence="observed", note="ledger"),
            Variable("inflow", "flow", "units/month", equation="arrivals", target="level"),
            Variable("outflow", "flow", "units/month", equation="rate * level",
                     target="level", sign=-1),
            Variable("arrivals", "parameter", "units/month", value=5.0,
                     evidence="observed", note="ledger"),
            Variable("rate", "parameter", "per month", value=rate),
        ],
    )


def synthetic_record() -> Series:
    result = Runtime(tank(0.07), RunSettings(dt=1.0, horizon=36.0)).run()
    return Series("level", tuple(result.times), tuple(result.series["level"]), "units",
                  source="synthetic record", checksum="abc123def456")


def test_chapter_35_prints_the_numbers_this_run_produces() -> None:
    record = synthetic_record()
    assert len(record.values) == 37
    assert record.values[0] == 100.0
    assert round(record.values[-1], 2) == 73.52

    fit_window = record.window(0, 24)
    hold_window = record.window(25, 36)
    assert (len(fit_window.values), len(hold_window.values)) == (25, 12)

    # the placeholder rate misses the fit window by 20 percent
    target = Target("level", fit_window, tolerance=0.01, error="mape")
    assert round(error_of(tank(0.1), [target])[0], 4) == 0.2013

    # one knob, nine steps, two refinements: 27 evaluations, rate 0.069375, error 0.5 percent
    knob = Knob("rate", 0.01, 0.2, steps=9)
    assert knob.grid()[1] - knob.grid()[0] == pytest.approx(0.02375)
    assert round(0.02375 / 16, 4) == 0.0015          # step of the finest grid
    fit = grid_fit(tank(0.1), [knob], [target])
    assert fit.fitted == {"rate": 0.069375}
    assert round(fit.per_target["level"], 4) == 0.005
    assert fit.evaluations == 27 == 3 * 9 ** 1
    assert fit.method == "grid search, 1 knobs, 2 refinements"
    assert 9 ** 3 == 729 and 3 * 729 == 2187 and 2187 / 60 > 30   # the three-knob cost

    # the fitted document: rate inferred with its note, arrivals still observed
    fitted = with_fitted(tank(0.1), fit, [target])
    assert fitted.by_id("rate").evidence == "inferred"
    assert fitted.by_id("arrivals").evidence == "observed"
    assert fitted.by_id("rate").note == (
        "inferred: fitted to synthetic record by grid search, 1 knobs, 2 refinements over "
        "0.01 to 0.2; level error 0.00503; data sha256 abc123def456"
    )

    # holdout is a separate number, under one percent against a tolerance of two
    out = holdout(tank(0.1), fit, [Target("level", hold_window, tolerance=0.02)])
    assert out == {"level": 0.008499140398033168}
    assert out["level"] > fit.per_target["level"]

    rows = fit_report(fit, [target])
    assert rows == [
        {"parameter": "rate", "fitted": 0.0694, "searched": (0.01, 0.2), "evidence": "inferred"},
        {"target": "level", "error": "mape", "fit_window": 0.005, "tolerance": 0.01,
         "holdout": 0.0085},
    ]

    # the critic on the fitted document finds nothing
    assert conservation_findings(fitted) == []
    assert extreme_condition_findings(fitted, "level") == []

    # the overfitting guard: five points cannot hold two knobs
    short = record.window(0, 4)
    assert len(short.values) == 5
    with pytest.raises(ValueError) as caught:
        grid_fit(tank(), [Knob("rate", 0.0, 1.0), Knob("arrivals", 0.0, 10.0)],
                 [Target("level", short, tolerance=0.1)])
    assert str(caught.value) == (
        "2 knobs against 5 observations: the record is too short to constrain that many free "
        "parameters (rule: at most one knob per three points)"
    )

    # the wrong knob fits the window and fails the holdout
    wrong = grid_fit(tank(0.1), [Knob("arrivals", 0.0, 10.0, steps=9)], [target])
    assert wrong.fitted == {"arrivals": 7.578125}
    assert round(wrong.per_target["level"], 4) == 0.0089
    assert wrong.within_tolerance([target])
    wrong_out = holdout(tank(0.1), wrong, [Target("level", hold_window, tolerance=0.02)])
    assert wrong_out == {"level": 0.029130466029184076}
    assert wrong_out["level"] > 0.02
