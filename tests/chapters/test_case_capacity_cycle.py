"""Chapter 38: every number the chapter prints, produced by this run, offline."""
import csv
from pathlib import Path

from chapters.chapter_38_capacity_cycle.code import calibrate as c
from chapters.chapter_38_capacity_cycle.code import model as capacity

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "data/fred_capacity/capacity_monthly.csv"


# ---------- Chapter 38 ----------

def rows() -> dict[str, dict[str, str]]:
    with RECORD.open(encoding="utf-8", newline="") as handle:
        return {r["period"][:7]: r for r in csv.DictReader(handle)}


def growth(table: dict[str, dict[str, str]], column: str, start: str, end: str) -> float:
    return round(100 * (float(table[end][column]) / float(table[start][column]) - 1), 1)


def test_chapter_38_prints_the_numbers_this_run_produces() -> None:
    """Record, fit at the pinned values, holdout, checks, policies. All pinned here."""
    summary = c.summary()
    assert summary["record_period"] == 90
    assert summary["record_amplitude"] == 18.0
    assert summary["record_mean"] == 77.5
    assert summary["holdout_period"] == 64
    assert summary["holdout_amplitude"] == 18.7
    assert summary["model_period"] == 93
    assert summary["model_amplitude"] == 18.1
    assert summary["fitted"] == {"investment_gain": 0.25, "margin_sensitivity": 0.8333,
                                 "construction_delay": 18.0}
    assert summary["fit_errors"] == {"utilization": 0.033, "utilization_level": 0.011}
    assert summary["holdout_errors"] == {"utilization": 0.375, "utilization_level": 0.048}

    # the fit is within tolerance on the window it saw, and outside it on the period it did not
    fit = c.pinned_fit()
    assert fit.within_tolerance(c.targets())
    assert c.holdout_errors()["utilization"] > c.PERIOD_TOLERANCE
    assert c.holdout_errors()["utilization_level"] < c.AMPLITUDE_TOLERANCE

    # the record itself
    record = list(c.record().values)
    assert len(record) == 360 and len(c.holdout_record().values) == 216
    assert (round(max(record), 1), round(min(record), 1)) == (84.7, 63.5)
    acf = c.autocorrelation(record)
    assert next(k for k in range(1, len(acf)) if acf[k] <= 0) == 33
    assert round(acf[90], 3) == 0.083
    table = rows()
    assert table["1994-12"]["utilization"] == "84.7029"
    assert table["2009-06"]["utilization"] == "63.5164"
    assert growth(table, "capacity_index", "1990-01", "2001-12") == 59.2
    assert growth(table, "capacity_index", "2009-06", "2019-12") == 3.6
    assert growth(table, "production_index", "1994-12", "2000-12") == 34.1
    assert growth(table, "capacity_index", "1994-12", "2000-12") == 37.7
    assert growth(table, "production_index", "2007-12", "2009-06") == -20.8
    assert growth(table, "capacity_index", "2007-12", "2009-06") == 1.0
    assert (table["1990-01"]["utilization"], table["2019-12"]["utilization"]) == \
        ("81.2891", "77.2053")
    assert (table["2001-12"]["utilization"], table["2007-12"]["utilization"]) == \
        ("71.2844", "79.2943")

    # the fitted model's path
    path = c.model_path()
    assert (round(max(path), 1), round(min(path), 1)) == (81.9, 64.5)
    assert round(sum(path) / len(path), 1) == 72.8

    # construction delay sweep
    sweep = {int(r["construction_delay"]): (r["period"], r["amplitude"])
             for r in c.construction_delay_sweep()}
    assert sweep == {12: (76, 17.18), 18: (93, 18.14), 24: (105, 19.42), 30: (114, 19.16),
                     36: (123, 18.68), 48: (127, 16.66)}

    # phase envelope
    envelope = c.phase_envelope()
    assert envelope["band_at_120"] == 15.8 and envelope["widest_band"] == 26.5
    assert envelope["first_trough_months"] == (78, 64, 29, 36, 42)
    assert envelope["trough_spread_months"] == 49

    # policies at the fitted values
    stats = {r["policy"]: (r["period"], r["amplitude"], r["mean_utilization"], r["steadiness"])
             for r in c.policy_statistics()}
    assert stats == {
        "build_when_margins_good": (93, 18.1, 72.8, 93.74),
        "utilisation_trigger": (33, 5.1, 77.8, 99.41),
        "smoothed_margin_trigger": (None, 2.0, 78.0, 99.66),
        "fixed_replacement": (None, 0.0, 80.0, 98.0),
    }
    assert c.policies()[1].settings == {"investment_gain": 0.0, "rule_gain_utilization": 1.458}
    # the dead band damps at demand 80 and cycles at demand 84
    from chapters.chapter_22_runtime.code.runtime import Runtime
    from chapters.chapter_35_calibration.code.calibrate import with_values
    high = Runtime(with_values(c.fitted_document(), {"margin_dead_band": 0.1, "demand": 84.0}),
                   c.SETTINGS).run().series["utilization"]
    assert (c.cycle_period(high), round(c.amplitude(high), 1)) == (88, 19.6)
    assert [round(b.high, 2) for b in c.bounds() if b.high is not None] == [17.96]

    # policies across twelve draws
    evaluations = {e.policy: e for e in c.compare_policies()}
    base = evaluations["build_when_margins_good"]
    assert len(base.violations) == 19
    assert sum("mean_utilization" in v for v in base.violations) == 11
    assert sum("amplitude" in v for v in base.violations) == 8
    assert round(base.worst(), 2) == 90.58
    trigger = evaluations["utilisation_trigger"]
    assert trigger.violations == []
    assert (round(trigger.worst(), 2), round(trigger.mean(), 2)) == (98.24, 99.36)
    smoothed = evaluations["smoothed_margin_trigger"]
    assert len(smoothed.violations) == 1 and "amplitude" in smoothed.violations[0]
    assert round(smoothed.worst(), 2) == 94.71
    fixed = evaluations["fixed_replacement"]
    assert len(fixed.violations) == 1 and "mean_utilization" in fixed.violations[0]
    assert round(fixed.worst(), 2) == 93.37
    recommendation = c.recommendation()
    assert recommendation["recommended"] == "utilisation_trigger"
    assert sorted(recommendation["excluded"]) == ["build_when_margins_good", "fixed_replacement",
                                                  "smoothed_margin_trigger"]

    # Chapter 29's ranking
    ranking = [(name, round(swing, 2)) for name, swing in c.sensitivity_ranking()]
    assert ranking == [("demand", 3.12), ("margin_sensitivity", 2.3), ("capital_lifetime", 2.06)]


def test_chapter_38_search_lands_on_the_pinned_values() -> None:
    """The grid search, run for real. Slow: about a minute of runs."""
    found = c.fit()
    assert {k: round(v, 4) for k, v in found.fitted.items()} == c.PINNED_FIT
    assert found.evaluations == 128
    assert found.within_tolerance(c.targets())


def test_chapter_38_oscillates_with_demand_held_constant() -> None:
    """No external driver: demand is a parameter, and utilization still cycles."""
    doc = c.fitted_document()
    demand = doc.by_id("demand")
    assert demand.kind == "parameter" and demand.value == 80.0
    assert not any(v.kind == "lookup" and "elapsed" in v.equation for v in doc.variables)
    check = c.endogenous_check()
    assert check["period"] == 93 and round(check["amplitude"], 1) == 18.1
    # and the swing does not die away: the last third is as wide as the middle third
    path = c.model_path()
    middle, last = path[120:240], path[240:]
    assert (max(last) - min(last)) > 0.9 * (max(middle) - min(middle))


def test_chapter_38_step_size_moves_the_period_by_less_than_ten_months() -> None:
    """Chapter 19: halve the step and see whether the answer moves. It moves, and settles."""
    check = c.step_refinement(tolerance_months=6.0)
    assert check["periods"] == (93, 84, 79)
    assert check["largest_change"] == 9.0
    assert check["converged"] is True
    assert abs(check["periods"][1] - check["periods"][2]) < 6


def test_chapter_38_critic_finds_only_the_counters_and_the_outputs() -> None:
    report = c.critic_report()
    assert set(report) == {"structural"}
    flagged = {line.split(":")[0] for line in report["structural"]}
    assert flagged == {"utilization_level", "steadiness", "mean_utilization",
                       "cumulative_deviation", "cumulative_utilization", "elapsed"}


def test_chapter_38_fitted_values_are_inferred_and_nothing_is_observed() -> None:
    doc = c.fitted_document()
    levels = {v.id: v.evidence for v in doc.variables}
    assert levels["investment_gain"] == "inferred"
    assert levels["margin_sensitivity"] == "inferred"
    assert levels["completions"] == "inferred"
    assert "observed" not in levels.values()
    assert "sha256 10d2dc560923" in doc.by_id("investment_gain").note
    assert doc.by_id("completions").delay_time == 18.0
    assert doc.by_id("perceived_margin").kind == "delay"
    assert doc.by_id("margin_shape").kind == "lookup"
    assert doc.by_id("capacity").kind == "stock"


def test_chapter_38_period_and_amplitude_on_known_shapes() -> None:
    import math
    wave = [80 + 5 * math.sin(2 * math.pi * t / 60) for t in range(361)]
    assert c.cycle_period(wave) == 60
    # a least-squares line through whole cycles of a sine is not flat, so the detrended range
    # sits a little above the raw ten points; a trend of eighteen points over the window is removed
    assert 10.0 <= c.amplitude(wave) <= 11.5
    trended = [v + 0.05 * t for t, v in enumerate(wave)]
    assert max(trended) - min(trended) > 20
    assert 10.0 <= c.amplitude(trended) <= 11.5
    assert c.cycle_period(trended) == 60
    assert c.cycle_period([1.0 + 0.01 * t for t in range(100)]) is None
    assert c.amplitude([3.0, 3.0, 3.0, 3.0]) == 0.0


def test_chapter_38_default_document_validates_and_runs() -> None:
    from chapters.chapter_20_model_document.code.document import validate
    doc = capacity.document()
    assert validate(doc) == []
    assert doc.horizon_unit == "month" and doc.time_step == 1.0
    assert len(capacity.utilization_path(doc, months=24)) == 25
