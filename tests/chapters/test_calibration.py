# ---------- Chapter 35 ----------
import pytest

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from chapters.chapter_35_calibration.code.calibrate import (
    Knob,
    Series,
    Target,
    error_of,
    fit_report,
    grid_fit,
    holdout,
    mape,
    read_series,
    shape,
    with_fitted,
)


def decay(rate: float = 0.1, inflow: float = 5.0) -> ModelDocument:
    """A tank with a constant inflow and proportional outflow. One knob nobody measured."""
    return ModelDocument(
        name="tank", version="1.0.0", horizon=36, horizon_unit="month", time_step=1.0,
        variables=[
            Variable("level", "stock", "units", value=100.0, evidence="observed", note="ledger"),
            Variable("inflow", "flow", "units/month", equation="arrivals", target="level"),
            Variable("outflow", "flow", "units/month", equation="rate * level",
                     target="level", sign=-1),
            Variable("arrivals", "parameter", "units/month", value=inflow, evidence="observed",
                     note="ledger"),
            Variable("rate", "parameter", "per month", value=rate),
        ],
    )


def record(rate: float) -> Series:
    result = Runtime(decay(rate), RunSettings(dt=1.0, horizon=36.0)).run()
    return Series("level", tuple(result.times), tuple(result.series["level"]), "units",
                  source="synthetic record", checksum="abc123def456")


def test_chapter_35_grid_fit_recovers_a_hidden_rate():
    target = Target("level", record(0.07), tolerance=0.01)
    fit = grid_fit(decay(0.1), [Knob("rate", 0.01, 0.2, steps=9)], [target])
    assert abs(fit.fitted["rate"] - 0.07) < 0.003
    assert fit.per_target["level"] < 0.01
    assert fit.within_tolerance([target])
    assert fit.evaluations == 27
    assert fit.document_hash == decay(0.1).hash()


def test_chapter_35_refuses_more_knobs_than_the_record_can_hold():
    short = Series("level", (0.0, 1.0, 2.0, 3.0, 4.0), (100, 95, 91, 87, 84), "units", "x")
    with pytest.raises(ValueError, match="too short"):
        grid_fit(decay(), [Knob("rate", 0.0, 1.0), Knob("arrivals", 0.0, 10.0)],
                 [Target("level", short, 0.1)])


def test_chapter_35_fitted_values_are_inferred_not_observed():
    target = Target("level", record(0.07), tolerance=0.01)
    fit = grid_fit(decay(0.1), [Knob("rate", 0.01, 0.2)], [target])
    fitted = with_fitted(decay(0.1), fit, [target])
    rate = fitted.by_id("rate")
    assert rate.evidence == "inferred"
    assert "synthetic record" in rate.note and "abc123def456" in rate.note
    assert fitted.by_id("arrivals").evidence == "observed"
    assert fitted.hash() != decay(0.1).hash()


def test_chapter_35_holdout_is_a_separate_number():
    full = record(0.07)
    fit_window = full.window(0, 24)
    hold_window = full.window(25, 36)
    target = Target("level", fit_window, tolerance=0.01)
    fit = grid_fit(decay(0.1), [Knob("rate", 0.01, 0.2)], [target])
    out = holdout(decay(0.1), fit, [Target("level", hold_window, 0.02)])
    assert out["level"] < 0.02
    rows = fit_report(fit, [target])
    assert rows[0]["evidence"] == "inferred"
    assert rows[1]["holdout"] is not None


def test_chapter_35_error_functions_behave():
    assert mape([110.0, 90.0], [100.0, 100.0]) == pytest.approx(0.1)
    assert shape([1, 2, 3], [2, 4, 6]) == pytest.approx(0.0)
    assert shape([1, 2, 3], [3, 2, 1]) == pytest.approx(2.0)
    total, per, res = error_of(decay(0.07), [Target("level", record(0.07), 0.01)])
    assert total == pytest.approx(0.0) and res["level"] == tuple([0.0] * 37)


def test_chapter_35_read_series_turns_dates_into_months(tmp_path):
    path = tmp_path / "r.csv"
    path.write_text("period,total\n2016-04-01,10\n2016-05-01,11\n2016-07-01,13\n")
    s = read_series(path, "period", "total", name="total", unit="pathways", source="test")
    assert s.times == (0.0, 1.0, 3.0) and s.values == (10.0, 11.0, 13.0)
    assert len(s.checksum) == 64
