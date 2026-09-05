"""Chapter 37: the hiring pipeline fitted to the JOLTS record. Offline; the CSV is committed."""
import math

from chapters.chapter_20_model_document.code.document import validate
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from chapters.chapter_37_hiring_pipeline.code import calibrate as pipeline
from chapters.chapter_37_hiring_pipeline.code.model import (
    FILL_TIME_2015_2019,
    LAYOFF_RATE_2015_2019,
    capability_share,
    document,
    effective_capability,
)

# ---------- Chapter 37 ----------


def test_the_unfitted_document_validates_and_runs() -> None:
    doc = document()
    assert validate(doc) == []
    result = Runtime(doc, RunSettings(dt=1.0, horizon=24.0)).run()
    assert len(effective_capability(result)) == 25
    assert all(0 < s <= 1 for s in capability_share(result))


def test_heads_and_capability_are_different_stocks() -> None:
    """A hiring surge raises headcount and lowers the capability share at the same time."""
    base = pipeline.run(0.0, 12)
    surge = pipeline.run(0.10, 12)
    assert surge.series["headcount"][-1] > base.series["headcount"][-1]
    assert capability_share(surge)[-1] < capability_share(base)[-1]


def test_the_record_constants_match_the_committed_csv() -> None:
    rows = [r for r in pipeline.record_rows() if "2015-01" <= str(r["period"])[:7] <= "2019-12"]
    fill = sum(float(r["openings"]) / float(r["hires"]) for r in rows) / len(rows)
    layoff = sum((float(r["separations"]) - float(r["quits"])) / float(r["employment"])
                 for r in rows) / len(rows)
    assert round(fill, 3) == round(FILL_TIME_2015_2019, 3) == 1.152
    assert round(layoff, 5) == round(LAYOFF_RATE_2015_2019, 5) == 0.01472


def test_the_fit_lands_within_tolerance_on_both_targets() -> None:
    fit = pipeline.fit()
    assert fit.within_tolerance(pipeline.targets())
    assert fit.per_target["hires"] <= 0.08
    assert fit.per_target["quits"] <= 0.12
    assert set(fit.fitted) == {"target_growth", "base_quit_rate", "ramp_time"}
    assert len(pipeline.knobs()) <= 3


def test_fitted_values_are_inferred_and_record_values_are_observed() -> None:
    doc = pipeline.fitted_document()
    for name in ("target_growth", "base_quit_rate", "ramp_time"):
        variable = doc.by_id(name)
        assert variable.evidence == "inferred"
        assert "fitted to" in variable.note and "sha256" in variable.note
    for name in ("headcount", "vacancies", "fill_time", "layoff_rate", "target_base"):
        assert doc.by_id(name).evidence == "observed"
    for name in ("experience", "initial_capability", "quit_sensitivity", "gap_closing_time",
                 "normal_capability_share"):
        assert doc.by_id(name).evidence == "assumed"
    assert doc.by_id("experience").note.endswith("no observed counterpart")


def test_the_conservation_identity_holds_in_the_model_and_uses_matching_record_intervals() -> None:
    """The record flow window begins after the opening employment stock is observed."""
    assert abs(pipeline.model_identity_residual(60)) < 1e-6
    gap = pipeline.identity_gap()
    assert gap["net_hires"] == 11253.0
    assert gap["employment_change"] == 11226.0
    assert gap["gap"] == 27.0
    assert round(gap["gap_share"], 3) == 0.002
    # The critic's structural pass finds exactly one thing: the clock, a counter by design.
    defects = pipeline.defects()
    assert list(defects) == ["structural"]
    assert defects["structural"] == [
        "clock: no outflow: it can only grow, which is right only for a cumulative counter "
        "and a defect otherwise"]


def test_the_holdout_is_reported_and_misses() -> None:
    """The fit never saw 2022 to 2024. Hires miss by more than the fit tolerance."""
    fit = pipeline.fit()
    assert set(fit.holdout_error) == {"hires", "quits"}
    assert fit.holdout_error["hires"] > 0.08
    assert fit.holdout_error["quits"] <= 0.12


def test_the_ramp_is_not_pinned_by_the_record() -> None:
    profile = pipeline.ramp_profile()
    assert max(profile.values()) - min(profile.values()) < 0.02
    assert all(err < 0.08 + 0.12 for err in profile.values())


def test_ramp_time_ranks_first_and_shorten_ramp_is_recommended() -> None:
    ranking = pipeline.ranking()
    assert ranking[0][0] == "ramp_time"
    assert ranking[1][0] == "initial_capability"
    evaluations, verdict = pipeline.comparison()
    assert verdict["recommended"] == "shorten_ramp"
    assert all(e.admissible() for e in evaluations)


def test_chapter_37_prints_the_numbers_this_run_produces() -> None:
    """Every number the prose quotes from code, pinned here."""
    record = pipeline.record()
    # The record, January 2015 and December 2019, then the pandemic and holdout months.
    first = {k: v.values[0] for k, v in record.items()}
    assert first == {"openings": 5344.0, "hires": 5061.0, "quits": 2764.0, "layoffs": 1789.0,
                     "separations": 4886.0, "employment": 140568.0}
    assert record["hires"].values[59] == 5951.0
    assert record["quits"].values[59] == 3487.0
    assert record["employment"].values[59] == 151794.0
    assert record["employment"].values[61] == 152293.0
    assert record["employment"].values[63] == 130426.0
    assert record["hires"].values[63] == 4029.0
    assert record["hires"].values[64] == 8133.0
    assert record["hires"].values[84] == 6431.0
    assert record["quits"].values[84] == 4413.0
    assert record["hires"].values[119] == 5292.0
    assert record["quits"].values[119] == 3085.0
    assert record["employment"].values[119] == 158316.0
    fit_rows = [r for r in pipeline.record_rows() if str(r["period"])[:4] <= "2019"]
    assert round(sum(float(r["hires"]) for r in fit_rows) / 60, 1) == 5508.3
    assert round(sum(float(r["quits"]) for r in fit_rows) / 60, 1) == 3162.1
    assert round(sum(float(r["openings"]) for r in fit_rows) / 60, 1) == 6360.2
    assert round(record["quits"].values[0] / record["employment"].values[0] * 100, 2) == 1.97
    assert round(record["quits"].values[59] / record["employment"].values[59] * 100, 2) == 2.30

    # The fit.
    fit = pipeline.fit()
    assert round(fit.fitted["target_growth"], 4) == 0.0016
    assert round(fit.fitted["base_quit_rate"], 4) == 0.0179
    assert fit.fitted["ramp_time"] == 12.0
    assert round(math.exp(fit.fitted["target_growth"] * 12) - 1, 3) == 0.019
    assert round(fit.per_target["hires"], 3) == 0.024
    assert round(fit.per_target["quits"], 3) == 0.031
    assert round(fit.holdout_error["hires"], 3) == 0.102
    assert round(fit.holdout_error["quits"], 3) == 0.107
    assert fit.evaluations == 490
    profile = pipeline.ramp_profile()
    assert {k: round(v, 3) for k, v in profile.items()} == {2.0: 0.067, 6.0: 0.067,
                                                            12.0: 0.062, 18.0: 0.065}
    # Model against record at named months.
    hires = {r["month"]: r for r in pipeline.against_record("hires", (0, 59, 84, 108, 119))}
    quits = {r["month"]: r for r in pipeline.against_record("quits", (0, 59, 84, 119))}
    assert round(hires[0]["model"]) == 4639 and round(hires[0]["error"], 3) == -0.083
    assert round(quits[0]["model"]) == 2515 and round(quits[0]["error"], 3) == -0.090
    assert round(hires[59]["model"]) == 5868 and round(hires[59]["error"], 3) == -0.014
    assert round(quits[59]["model"]) == 3372 and round(quits[59]["error"], 3) == -0.033
    assert round(hires[84]["model"]) == 6102 and round(hires[84]["error"], 3) == -0.051
    assert round(quits[84]["model"]) == 3507 and round(quits[84]["error"], 3) == -0.205
    assert round(hires[108]["error"], 3) == 0.133
    assert round(hires[119]["model"]) == 6443 and round(hires[119]["error"], 3) == 0.218
    assert round(quits[119]["model"]) == 3704 and round(quits[119]["error"], 3) == 0.201
    path = pipeline.fitted_path()
    assert round(path.series["headcount"][119]) == 168332
    share = capability_share(path)
    assert round(share[0], 2) == 0.90 and round(share[59], 3) == 0.811
    assert round(path.series["workload"][59], 3) == 1.115

    # The headline table at month 24 under a ten percent target step.
    table = {row["rule"]: row for row in pipeline.headline()}
    assert [round(table[k]["headcount"]) for k in ("baseline", "hire_harder", "retain",
                                                    "shorten_ramp")] == [159721, 159933,
                                                                         159730, 159736]
    assert [round(table[k]["effective_capability"]) for k in
            ("baseline", "hire_harder", "retain", "shorten_ramp")] == [129864, 130302, 132548,
                                                                       143217]
    assert [round(table[k]["capability_share"], 3) for k in
            ("baseline", "hire_harder", "retain", "shorten_ramp")] == [0.813, 0.815, 0.830,
                                                                       0.897]
    assert [round(table[k]["cumulative_hires"]) for k in
            ("baseline", "hire_harder", "retain", "shorten_ramp")] == [154441, 154486, 136703,
                                                                       144574]
    assert table["record (CES, JOLTS)"]["headcount"] == 145628.0
    assert table["record (CES, JOLTS)"]["cumulative_hires"] == 126354.0
    base = pipeline.run(pipeline.TARGET_STEP, 24)
    assert round(base.series["headcount"][24] / base.series["headcount"][0] - 1, 3) == 0.136
    assert round(base.series["effective_capability"][24]
                 / base.series["effective_capability"][0] - 1, 3) == 0.027
    assert round(base.series["hires"][2]) == 9935
    assert round(max(base.series["vacancies"][:25])) == 11445
    assert base.series["vacancies"].index(max(base.series["vacancies"][:25])) == 2
    assert round(base.series["workload"][24], 3) == 1.112
    assert round(base.series["quit_rate"][24] / fit.fitted["base_quit_rate"], 2) == 1.22
    assert round(table["shorten_ramp"]["effective_capability"]
                 - table["baseline"]["effective_capability"]) == 13353
    assert round(table["shorten_ramp"]["effective_capability"]
                 / table["baseline"]["effective_capability"] - 1, 3) == 0.103
    assert round(base.series["quits"][24]) == 3499 and round(base.series["quits"][0]) == 3018
    harder = pipeline.run(pipeline.TARGET_STEP, 24, {"gap_closing_time": 1.5})
    assert round(harder.series["hires"][2]) == 14738
    assert round(harder.series["hires"][6]) == 1590
    over = pipeline.overshoot()
    assert round(over["peak_hires"]) == 19542 and over["peak_month"] == 2.0
    assert round(over["trough_hires"]) == 23 and over["trough_month"] == 6.0
    assert round(over["headcount"]) == 164825 and round(over["ceiling"]) == 161653
    shorter = pipeline.run(pipeline.TARGET_STEP, 24, {"ramp_time": 6.0})
    assert round(shorter.series["quits"][24]) == 2907
    retained = pipeline.run(pipeline.TARGET_STEP, 24,
                            {"base_quit_rate": 0.8 * fit.fitted["base_quit_rate"]})
    assert round(retained.series["quits"][24]) == 2697

    # Chapter 30's comparison at its fixed horizon of twenty months, forty draws.
    evaluations, verdict = pipeline.comparison()
    worst = {e.policy: round(e.worst()) for e in evaluations}
    means = {e.policy: round(e.mean()) for e in evaluations}
    assert worst == {"baseline": 126978, "hire_harder": 127953, "retain": 130026,
                     "shorten_ramp": 137483}
    assert means == {"baseline": 141758, "hire_harder": 142599, "retain": 143255,
                     "shorten_ramp": 142182}
    assert verdict["recommended"] == "shorten_ramp" and verdict["excluded"] == {}
    assert round(pipeline.month20("baseline")) == 129221
    assert round(pipeline.month20("shorten_ramp")) == 142205
    bounds = {b.metric_name: b for b in pipeline.bounds()}
    assert round(bounds["headcount"].high) == 161653
    assert round(bounds["effective_capability"].low, 1) == 126511.2

    # Which parameter decides it, and the envelope.
    ranking = {name: round(swing) for name, swing in pipeline.ranking()}
    assert ranking == {"ramp_time": 22410, "initial_capability": 11959,
                       "gap_closing_time": 1363, "quit_sensitivity": 506, "fill_time": 15}
    envelope = pipeline.envelope()
    assert envelope["draws"] == 200
    assert {k: round(v) for k, v in envelope.items() if k != "draws"} == {
        "low": 121884, "p10": 130551, "median": 141338, "p90": 149559, "high": 154606}
