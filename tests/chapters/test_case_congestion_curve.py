"""Chapter 39: the first lookup in the book fitted from a real record. Offline."""
import pytest

from chapters.chapter_15_lookups.code.lookup import Lookup, OutsideDomain
from chapters.chapter_20_model_document.code.document import validate
from chapters.chapter_39_congestion_curve.code import calibrate as cal
from chapters.chapter_39_congestion_curve.code.model import free_knobs


@pytest.fixture(scope="module")
def case() -> dict:
    return cal.run_case()


# ---------- Chapter 39 ----------

def test_the_fitted_lookup_is_monotone_and_convex_above_its_knee(case) -> None:
    points = case["points"]
    knee = case["fit"]["fitted"]["knee"]
    assert Lookup(list(points)).is_monotonic()
    assert cal.convex_above_knee(points, knee)
    assert not cal.convex_above_knee(((0.8, 10.0), (0.9, 14.0), (1.0, 15.0)), 0.8)


def test_the_bin_error_is_within_two_minutes(case) -> None:
    assert case["fit"]["error"] <= cal.MAE_BOUND_MINUTES


def test_the_lookup_refuses_a_load_outside_the_fitted_domain(case) -> None:
    """The chapter's point about extrapolation: a fit answers everything, a lookup does not."""
    lookup = Lookup(list(case["points"]), name="congestion_delay")
    low, high = lookup.domain
    assert lookup(low) == case["points"][0][1]
    with pytest.raises(OutsideDomain):
        lookup(high + 0.1)
    with pytest.raises(OutsideDomain):
        lookup(low - 0.1)


def test_every_fitted_value_is_inferred_never_observed(case) -> None:
    document = cal.fitted_document()
    assert document.by_id("congestion_delay").evidence == "inferred"
    assert document.by_id("cancel_per_minute").evidence == "inferred"
    assert "not evidence for one" in document.by_id("congestion_delay").note
    assert case["fit"]["evidence"] == "inferred"
    assert validate(document) == []
    assert len(free_knobs()) == 3


def test_the_lowest_load_taxi_out_is_an_inferred_baseline() -> None:
    document = cal.fitted_document()
    assert "baseline_taxi_out" in {variable.id for variable in document.variables}
    baseline = document.by_id("baseline_taxi_out")
    assert baseline.evidence == "inferred"
    assert "not a measurement of zero queueing" in baseline.note


def test_the_peak_hour_is_an_assumed_daily_representation() -> None:
    document = cal.fitted_document()
    assert "representative_peak_departures" in {variable.id for variable in document.variables}
    peak = document.by_id("representative_peak_departures")
    assert peak.unit == "departure/day"
    assert peak.evidence == "assumed"


def test_the_bins_travel_as_a_series_with_the_record_checksum(case) -> None:
    series = cal.bins_as_series(case["bins"])
    assert series.unit == "minute/departure"
    assert len(series.checksum) == 64
    assert series.times == tuple(b[0] for b in case["bins"])


def test_the_document_refuses_to_run_past_the_record(case) -> None:
    from chapters.chapter_29_experiments.code.sensitivity import metric
    top = case["points"][-1][0]
    metric(cal.fitted_document(), {"scheduled_load": top}, "realized_delay")
    with pytest.raises(RuntimeError):
        metric(cal.fitted_document(), {"scheduled_load": top + 0.2}, "realized_delay")


def test_the_monthly_average_does_not_move_with_monthly_load(case) -> None:
    """Why an average delay per flight cannot price a schedule change."""
    assert round(case["month_correlation"], 2) == -0.10
    delay_bins = {b[0]: round(b[1], 2) for b in case["delay_bins"]}
    assert delay_bins[0.05] == 19.23 and delay_bins[1.15] == 12.54


def test_the_critic_finds_only_the_two_reporting_outputs(case) -> None:
    assert list(case["critic"]) == ["structural"]
    assert sorted(case["critic"]["structural"]) == [
        "movements_lost_share: nothing reads this variable",
        "reported_delay: nothing reads this variable",
    ]


def test_chapter_39_prints_the_numbers_this_run_produces(case) -> None:
    """Every number the chapter quotes from code, pinned to the committed vintage."""
    facts, hold = case["facts"], case["holdout_facts"]
    assert facts["airports"] == 30 and facts["rows"] == 360 and hold["rows"] == 360
    assert facts["scheduled_departures"] == 4_473_085
    assert hold["scheduled_departures"] == 4_594_527
    assert round(facts["mean_delay"], 2) == 16.05
    assert round(facts["mean_taxi_out"], 2) == 18.85
    assert round(facts["cancellation_share"], 4) == 0.0130
    assert round(facts["mean_load"], 3) == 1.094
    assert (round(facts["load_p10"], 3), round(facts["load_p90"], 3)) == (0.996, 1.222)
    assert round(facts["load_max"], 3) == 1.348 and round(hold["load_max"], 3) == 1.520
    assert round(facts["peak_hour_capacity"], 1) == 36.9
    assert round(facts["retained_p95"], 4) == 0.9895
    assert round(facts["retained_p90"], 4) == 0.9734
    assert round(facts["cap_load_p90"], 3) == 0.899
    assert round(hold["mean_delay"], 2) == 16.59 and round(hold["mean_taxi_out"], 2) == 19.36

    bins = {b[0]: (round(b[1], 2), b[2]) for b in case["bins"]}
    assert len(bins) == 14 and min(bins) == 0.05 and max(bins) == 1.35
    assert bins[0.05] == (15.91, 22_576)
    assert bins[0.65] == (18.28, 692_353)
    assert bins[0.95] == (19.95, 575_668)
    assert bins[1.15] == (20.87, 138_754)
    assert bins[1.25] == (20.57, 56_517)
    assert bins[1.35] == (19.37, 21_233)

    fit = case["fit"]
    assert fit["fitted"] == {"base": 16.79, "knee": 0.0, "curvature": 3.09}
    assert round(fit["error"], 2) == 0.54
    assert fit["evaluations"] == 27_783
    points = dict(case["points"])
    assert points[0.05] == 16.798 and points[0.95] == 19.579
    assert points[1.05] == 20.197 and points[1.35] == 22.422

    holdout = case["holdout"]
    assert round(holdout["mae"], 2) == 0.64
    assert holdout["bins_inside"] == 14 and holdout["bins_refused"] == 0
    hold_bins = {b[0]: round(b[1], 2) for b in holdout["bins"]}
    assert hold_bins[1.25] == 22.15 and hold_bins[1.35] == 20.76

    clock = {h: (round(d, 1), round(t, 1)) for h, d, t, _ in case["clock"]}
    assert clock[5] == (7.1, 15.2) and clock[8] == (9.4, 20.1)
    assert clock[12] == (13.7, 17.9) and clock[20] == (24.3, 19.2)

    base, slope = case["cancellation"]
    assert round(slope * 1000, 2) == 1.48
    assert round(case["padding"]["realized_delay"], 2) == 4.59
    assert round(case["padding"]["padding"], 2) == 4.51
    assert round(case["padding"]["reported_delay"], 2) == 0.08
    assert round(case["padding"]["padding_at_90"], 2) == 2.87

    table = case["policies"]
    assert round(table["no_cap"]["realized_delay"]["mean"], 2) == 4.62
    assert round(table["no_cap"]["realized_delay"]["best"], 2) == 5.29
    assert round(table["no_cap"]["realized_delay"]["worst"], 2) == 3.98
    assert round(table["no_cap"]["cancellation_share"]["mean"], 4) == 0.0131
    assert round(table["no_cap"]["cancellation_share"]["best"], 4) == 0.0141
    assert len(table["no_cap"]["violations"]) == 19
    assert all("cancellation_share" in v for v in table["no_cap"]["violations"])
    assert round(table["cap_at_p95"]["realized_delay"]["mean"], 2) == 3.97
    assert round(table["cap_at_p95"]["realized_delay"]["best"], 2) == 3.97
    assert round(table["cap_at_p95"]["realized_delay"]["worst"], 2) == 3.96
    assert round(table["cap_at_p90"]["realized_delay"]["best"], 2) == 3.38
    assert round(table["cap_at_p90"]["realized_delay"]["worst"], 2) == 3.37
    assert round(table["cap_at_p95"]["cancellation_share"]["mean"], 4) == 0.0121
    assert round(table["cap_at_p95"]["movements_lost_share"]["mean"], 4) == 0.0226
    assert round(table["cap_at_p90"]["realized_delay"]["mean"], 2) == 3.38
    assert round(table["cap_at_p90"]["cancellation_share"]["mean"], 4) == 0.0113
    assert round(table["cap_at_p90"]["movements_lost_share"]["mean"], 4) == 0.0376
    assert table["cap_at_p95"]["violations"] == [] and table["cap_at_p90"]["violations"] == []

    # Hand arithmetic the prose does on the numbers above.
    assert round(facts["mean_taxi_out"] - case["bins"][0][1], 2) == 2.94
    f = fit["fitted"]
    excess = lambda load: cal.curve(load, **f) - case["bins"][0][1]  # noqa: E731
    assert round(excess(facts["mean_load"]), 2) == 4.58
    assert round(excess(1.0), 2) == 3.97 and round(excess(facts["cap_load_p90"]), 2) == 3.37
    assert round(bins[0.85][1] / bins[1.25][1]) == 13 and round(bins[0.85][1] / bins[1.35][1]) == 34
    document = cal.fitted_document()
    assert document.by_id("record_queue_delay").value == 4.578
    assert document.by_id("baseline_taxi_out").value == 15.913
    assert document.by_id("representative_peak_departures").value == 36.9


def test_the_season_moves_delay_and_the_manifest_counts_the_rows() -> None:
    """The July and November means the prose quotes, and the row count from the manifest."""
    import json
    import statistics
    months = cal.rows_for_year(cal.read_months(), cal.FIT_YEAR)
    by_month = {}
    for row in months:
        by_month.setdefault(row["period"][5:7], []).append(row["mean_dep_delay_minutes"])
    assert round(statistics.fmean(by_month["07"]), 1) == 25.6
    assert round(statistics.fmean(by_month["11"]), 1) == 9.7
    manifest = json.loads((cal.DATA_DIR / "MANIFEST.json").read_text(encoding="utf-8"))
    assert "13,926,960 flight rows" in manifest["vintage"]
    assert manifest["months_missing"] == []
    assert max(int(f["bytes"]) for f in manifest["files"]) < 60_000
