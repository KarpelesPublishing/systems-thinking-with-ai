"""Chapter 36: the numbers the prose quotes, the fit rules, and the evidence marks. Offline."""

import pytest

from chapters.chapter_20_model_document.code.document import validate
from chapters.chapter_36_elective_backlog.code import calibrate as c
from chapters.chapter_36_elective_backlog.code.model import (
    FREE_KNOBS,
    build,
    first_year_mean,
    window_mean,
    window_ratio,
)

# ---------- Chapter 36 ----------


@pytest.fixture(scope="module")
def fit():
    return c.fit()


def test_chapter_36_prints_the_numbers_this_run_produces(fit) -> None:
    """Pins every number the chapter quotes from code: fit, holdout, tables, policies, ranking."""
    report = {r.get("parameter") or r.get("target"): r for r in c.report()}
    assert report["validation_rate"]["fitted"] == 0.06
    assert report["system_growth"]["fitted"] == 0.004
    assert report["tail_steepness"]["fitted"] == 4.5
    assert report["total_incomplete"]["fit_window"] == 0.0363
    assert report["total_incomplete"]["holdout"] == 0.3557
    assert report["long_waiters"]["fit_window"] == 0.3967
    assert report["long_waiters"]["holdout"] == 0.3472
    assert fit.evaluations == 375

    headline = {r["series"]: (r["0"], r["24"], r["48"]) for r in c.headline_table()}
    assert headline["record"] == (6760060, 7621297, 7147562)
    assert headline["model"] == (6760060, 5422413, 5435468)
    assert headline["uniform_uplift"] == (6760060, 3525786, 2943347)
    assert headline["longest_first"] == (6760060, 5401897, 5430712)
    assert headline["validation_push"] == (6760060, 3708932, 3650522)

    long = {r["series"]: (r["0"], r["24"], r["48"]) for r in c.long_waiter_table()}
    assert long["record"] == (357577, 302693, 103318)
    assert long["model"] == (357577, 4481, 243)
    assert long["uniform_uplift"] == (357577, 178, 3)
    assert long["longest_first"] == (357577, 4524, 239)
    assert long["validation_push"] == (357577, 826, 13)

    comparison = c.compare_policies()
    means = {e.policy: (round(e.mean()), round(e.worst()), len(e.violations))
             for e in comparison.evaluations}
    assert means["baseline"] == (1290420, 907230, 0)
    assert means["uniform_uplift"] == (3016665, 2867539, 0)
    assert means["longest_first"] == (1309142, 1119114, 0)
    assert means["validation_push"] == (2957739, 2751705, 0)
    assert comparison.recommendation["recommended"] == "uniform_uplift"

    ranking = [(name, round(swing)) for name, swing in c.sensitivity_ranking()]
    assert ranking == [("long_share", 126362), ("tail_steepness", 43996),
                       ("system_growth", 9658), ("complexity_penalty", 6252),
                       ("suppression_strength", 0)]

    envelope = c.uncertainty_envelope()
    assert envelope["draws"] == 200
    assert (round(envelope["p05"]), round(envelope["median"]), round(envelope["p95"])) == (
        5343107, 5527479, 5730771)

    doc = c.policy_document()
    dates = {}
    waits = {}
    for policy in [c.baseline_policy()] + c.POLICIES:
        result = c.run(c.with_policy(doc, policy), 48)
        dates[policy.name] = (c.recovery_date(result, 6.0e6), c.recovery_date(result, 4.0e6))
        waits[policy.name] = round(c.at_month(result, "mean_wait_weeks", 48), 1)
    assert dates == {"baseline": ("2023-04", None), "uniform_uplift": ("2022-10", "2023-12"),
                     "longest_first": ("2023-02", None),
                     "validation_push": ("2022-09", "2023-12")}
    assert waits == {"baseline": 14.2, "uniform_uplift": 7.0, "longest_first": 14.2,
                     "validation_push": 9.6}

    fitted = c.fitted_document()
    path = c.run(fitted, fitted.horizon)
    assert round(c.at_month(path, "total_incomplete", 44)) == 4206670
    assert round(c.at_month(path, "total_incomplete", 122)) == 4676007
    assert round(c.at_month(path, "long_waiters", 60)) == 626

    critic = c.critic_report(fitted)
    assert set(critic) == {"structural"}
    assert critic["structural"] == [
        "mean_wait_weeks: nothing reads this variable",
        "list_reduction: nothing reads this variable",
        "capacity: no outflow: it can only grow, which is right only for a cumulative counter "
        "and a defect otherwise",
    ]


def test_chapter_36_record_flows_the_prose_quotes() -> None:
    """Yearly means of the record's own flows, in pathways per month."""
    rows = c.read_record()
    assert round(first_year_mean(rows, "new_periods", "2016-05")) == 1565044
    assert round(first_year_mean(rows, "completed_pathways", "2016-05")) == 1301014
    assert round(first_year_mean(rows, "unreported_removals", "2016-05")) == 249126
    assert round(first_year_mean(rows, "new_periods", "2018-05")) == 1682059
    assert round(first_year_mean(rows, "completed_pathways", "2018-05")) == 1373896
    assert round(first_year_mean(rows, "new_periods", "2025-07")) == 1777460
    assert round(first_year_mean(rows, "completed_pathways", "2025-07")) == 1531926
    assert round(first_year_mean(rows, "unreported_removals", "2025-07")) == 263890
    gap = window_mean(rows, "new_periods", "2016-05", "2019-12") - window_mean(
        rows, "total_removals", "2016-05", "2019-12")
    assert round(gap) == 18439
    assert round(window_ratio(rows, "unreported_removals", "total_incomplete", "2016-05",
                              "2017-04"), 4) == 0.0675
    assert round(window_ratio(rows, "unreported_removals", "total_incomplete", "2018-05",
                              "2019-04"), 4) == 0.0684
    assert round(window_ratio(rows, "unreported_removals", "total_incomplete", "2021-04",
                              "2026-06"), 4) == 0.0331
    assert round(window_mean(rows, "completed_pathways", "2019-01", "2019-12")) == 1383308
    assert round(window_mean(rows, "new_periods", "2019-01", "2019-12")) == 1681116
    assert round(window_mean(rows, "total_incomplete", "2025-07", "2026-06")) == 7188463
    assert c.record_at("2019-05") == {"total_incomplete": 4385693.0, "over_52_weeks": 1032.0}
    assert c.record_at("2022-06") == {"total_incomplete": 6760060.0, "over_52_weeks": 357577.0}
    assert c.record_at("2024-06") == {"total_incomplete": 7621297.0, "over_52_weeks": 302693.0}
    april = c.read_record()[c.month_index(rows, "2020-04")]
    assert (april["completed_pathways"], april["new_periods"]) == ("569514", "491101")
    over = [float(r["over_52_weeks"]) for r in rows if "2020-04" <= r["period"] <= "2021-03"]
    assert all(a < b for a, b in zip(over, over[1:])) and len(over) == 12
    assert c.record_at("2016-04") == {"total_incomplete": 3603606.0, "over_52_weeks": 886.0}
    assert c.record_at("2019-12") == {"total_incomplete": 4414911.0, "over_52_weeks": 1467.0}
    assert c.record_at("2020-04") == {"total_incomplete": 3947061.0, "over_52_weeks": 11179.0}
    assert c.record_at("2021-03") == {"total_incomplete": 4950297.0, "over_52_weeks": 436127.0}
    assert c.record_at("2023-09") == {"total_incomplete": 7744585.0, "over_52_weeks": 390320.0}
    assert c.record_at("2026-06") == {"total_incomplete": 7147562.0, "over_52_weeks": 103318.0}
    assert c.last_period() == "2026-06"


def test_chapter_36_fit_is_within_tolerance_in_window_and_fails_the_holdout(fit) -> None:
    assert fit.within_tolerance(c.targets())
    assert fit.per_target["total_incomplete"] <= c.TOLERANCE
    assert fit.holdout_error["total_incomplete"] > c.TOLERANCE


def test_chapter_36_a_fitted_value_at_the_edge_of_its_range_is_visible(fit) -> None:
    """tail_steepness lands on the top of the searched range; the chapter says so."""
    low, high = fit.searched["tail_steepness"]
    assert fit.fitted["tail_steepness"] == high
    assert fit.searched["system_growth"][0] < fit.fitted["system_growth"] < (
        fit.searched["system_growth"][1])


def test_chapter_36_knob_guard_holds_at_three() -> None:
    assert c.knob_guard() == 3
    assert len(c.knobs()) == 3
    assert {k.variable for k in c.knobs()} == set(FREE_KNOBS)
    shortest = min(len(t.series.values) for t in c.targets())
    assert 3 * len(c.knobs()) <= shortest


def test_chapter_36_evidence_levels_are_marked(fit) -> None:
    summary = c.evidence_summary()
    assert set(summary["inferred"]) == set(FREE_KNOBS)
    assert set(summary["observed"]) == {"waiting_list", "long_waiters", "capacity",
                                        "base_referrals", "reference_list", "initial_capacity",
                                        "reference_load"}
    assert set(summary["assumed"]) == {"tail_base", "suppression_strength",
                                       "complexity_penalty", "long_share", "capacity_uplift"}
    for v in c.fitted_document().variables:
        if v.evidence == "inferred":
            assert v.note.startswith("inferred: fitted to")
        if v.evidence == "observed":
            assert v.note.startswith("observed:")


def test_chapter_36_document_validates_and_stocks_read_the_record() -> None:
    doc = build("2016-04")
    assert validate(doc) == []
    assert doc.by_id("waiting_list").value + doc.by_id("long_waiters").value == 3603606.0
    assert doc.horizon_unit == "month"
    assert {v.id for v in doc.variables if v.kind == "stock"} == {"waiting_list",
                                                                   "long_waiters", "capacity"}


def test_chapter_36_recovery_date_returns_none_when_the_list_never_gets_there() -> None:
    result = c.run(build("2022-06", horizon=12), 12)
    assert c.recovery_date(result, 1.0) is None
    assert c.recovery_date(result, 1e9) == "2022-06"
