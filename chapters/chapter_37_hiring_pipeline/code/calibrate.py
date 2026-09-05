"""Fit the hiring pipeline to the JOLTS record, test it, and compare three hiring rules.

The fit window is January 2015 to December 2019 on hires and quits. The holdout is January 2022 to
December 2024, and the model runs through the pandemic years to get there with nothing in it that
knows they happened; the holdout number is reported as it comes out. Fitted values are marked
inferred. A fit within tolerance says the structure is consistent with the record and nothing
more (Chapter 35).
"""

import csv
from functools import lru_cache
from pathlib import Path

from chapters.chapter_22_runtime.code.runtime import Result, RunSettings, Runtime
from chapters.chapter_28_critic.code.critic import (
    conservation_findings,
    defect_report,
    dimensional_findings,
    extreme_condition_findings,
    structural_findings,
)
from chapters.chapter_29_experiments.code.sensitivity import (
    Uncertainty,
    metric,
    ranked,
    sample,
)
from chapters.chapter_30_policy_search.code.policies import (
    Bound,
    Evaluation,
    Policy,
    compare,
    recommend,
)
from chapters.chapter_35_calibration.code.calibrate import (
    Fit,
    Knob,
    Series,
    Target,
    fit_report,
    grid_fit,
    holdout,
    read_series,
    with_fitted,
    with_values,
)
from chapters.chapter_37_hiring_pipeline.code.model import document as unfitted_document

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "data" / "bls_jolts" / "jolts_monthly.csv"
SOURCE = "BLS JOLTS and CES via the BLS public API v2, retrieved 2026-09-03"
ORIGIN = "2015-01"
FIT_WINDOW = (0.0, 59.0)        # 2015-01 to 2019-12, months since origin
HOLDOUT_WINDOW = (84.0, 119.0)  # 2022-01 to 2024-12
TARGET_STEP = 0.10              # the policy scenario: a target ten percent above the record
HEADLINE_MONTH = 24
COMPARISON_MONTH = 20           # Chapter 30's compare reads its objective at this fixed horizon
DRAWS = 200                     # for the envelope
COMPARE_DRAWS = 40              # for the policy comparison
SEED = 11


# ---------------------------------------------------------------- the record


@lru_cache(maxsize=None)
def record() -> dict[str, Series]:
    """Every column of the committed CSV as a Series, time in months since January 2015."""
    out = {}
    for column, unit in (("openings", "thousand openings"), ("hires", "thousand persons/month"),
                         ("quits", "thousand persons/month"),
                         ("layoffs", "thousand persons/month"),
                         ("separations", "thousand persons/month"),
                         ("employment", "thousand persons")):
        out[column] = read_series(RECORD, "period", column, name=column, unit=unit,
                                  source=SOURCE, time_origin=ORIGIN)
    return out


def record_rows() -> list[dict[str, float | str]]:
    with RECORD.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    return [{k: (v if k == "period" else float(v)) for k, v in row.items()} for row in rows]


def identity_gap(start: str = "2015-01", end: str = "2019-12") -> dict[str, float]:
    """Cumulative flows after the opening stock against the CES employment change.

    Two surveys, one identity. JOLTS counts hires and separations at establishments; CES counts
    jobs. The identity holds in the model exactly and in the record only approximately, and the
    size of the miss is the number to know before trusting either as the other.
    """
    rows = [r for r in record_rows() if start <= str(r["period"])[:7] <= end]
    flow_rows = rows[1:]
    net = sum(float(r["hires"]) - float(r["separations"]) for r in flow_rows)
    change = float(rows[-1]["employment"]) - float(rows[0]["employment"])
    return {"net_hires": net, "employment_change": change, "gap": net - change,
            "gap_share": (net - change) / change}


# ---------------------------------------------------------------- fit


def document(target_step: float = 0.0):
    return unfitted_document(target_step)


def knobs() -> list[Knob]:
    return [
        Knob("target_growth", 0.0004, 0.0020, steps=7),
        Knob("base_quit_rate", 0.014, 0.028, steps=7),
        Knob("ramp_time", 2.0, 18.0, steps=5),
    ]


def targets(window: tuple[float, float] = FIT_WINDOW) -> list[Target]:
    series = record()
    return [
        Target("hires", series["hires"].window(*window), tolerance=0.08),
        Target("quits", series["quits"].window(*window), tolerance=0.12),
    ]


def holdout_targets() -> list[Target]:
    return targets(HOLDOUT_WINDOW)


@lru_cache(maxsize=None)
def fit() -> Fit:
    """Grid fit on the fit window, then the holdout error recorded in the same Fit."""
    result = grid_fit(document(), knobs(), targets(), refinements=1)
    holdout(document(), result, holdout_targets())
    return result


def fitted_document(target_step: float = 0.0):
    """The document with fitted values in place, each marked inferred."""
    base = with_fitted(document(), fit(), targets())
    if target_step:
        return with_values(base, {"target_step": target_step})
    return base


@lru_cache(maxsize=None)
def fitted_path() -> Result:
    """The fitted document run from January 2015 through December 2024, no scenario."""
    return Runtime(fitted_document(), RunSettings(dt=1.0, horizon=HOLDOUT_WINDOW[1])).run()


def against_record(variable: str, months: tuple[int, ...]) -> list[dict[str, float]]:
    """Model against record for one variable at named months since January 2015."""
    path, series = fitted_path(), record()[variable]
    return [{"month": m, "model": path.series[variable][m], "record": series.values[m],
             "error": path.series[variable][m] / series.values[m] - 1} for m in months]


def report() -> list[dict[str, object]]:
    return fit_report(fit(), targets())


@lru_cache(maxsize=None)
def ramp_profile(values: tuple[float, ...] = (2.0, 6.0, 12.0, 18.0)) -> dict[float, float]:
    """Best fit-window error at each ramp value, refitting the other two knobs each time.

    A flat profile means the record does not pin the ramp: the grid picked a value because a
    grid has to pick one, and every value in the row fits within tolerance.
    """
    out = {}
    others = [k for k in knobs() if k.variable != "ramp_time"]
    for value in values:
        doc = with_values(document(), {"ramp_time": value})
        out[value] = grid_fit(doc, others, targets(), refinements=1).error
    return out


# ---------------------------------------------------------------- critic


def findings():
    doc = fitted_document()
    found = conservation_findings(doc) + structural_findings(doc) + dimensional_findings(doc)
    for stock in ("headcount", "vacancies", "experience"):
        found += extreme_condition_findings(doc, stock)
    return found


def defects() -> dict[str, list[str]]:
    return defect_report(findings())


def model_identity_residual(months: int = 60) -> float:
    """Headcount change minus cumulative hires less quits and layoffs. Zero by construction."""
    result = Runtime(fitted_document(), RunSettings(dt=1.0, horizon=float(months))).run()
    net = sum(result.series["hires"][i] - result.series["quits"][i] - result.series["layoffs"][i]
              for i in range(months))
    return (result.series["headcount"][-1] - result.series["headcount"][0]) - net


# ---------------------------------------------------------------- policies


def run(target_step: float = TARGET_STEP, months: int = HEADLINE_MONTH,
        overrides: dict[str, float] | None = None) -> Result:
    doc = fitted_document(target_step)
    if overrides:
        doc = with_values(doc, overrides)
    return Runtime(doc, RunSettings(dt=1.0, horizon=float(months))).run()


def policies() -> list[Policy]:
    fitted = fit().fitted
    return [
        Policy("baseline", {"target_step": TARGET_STEP}, owner="the plan",
               reversible=True, note="the target rises ten percent; nothing else changes"),
        Policy("hire_harder", {"gap_closing_time": 1.5}, owner="recruiting",
               reversible=True, note="turn the gap into requisitions twice as fast"),
        Policy("retain", {"base_quit_rate": 0.8 * fitted["base_quit_rate"]}, owner="line managers",
               reversible=False, note="cut the base quit rate by a fifth"),
        Policy("shorten_ramp", {"ramp_time": 0.5 * fitted["ramp_time"]}, owner="onboarding",
               reversible=True, note="halve the months a hire needs to reach full contribution"),
    ]


def uncertainties() -> list[Uncertainty]:
    return [
        Uncertainty("ramp_time", 2.0, 12.0, cost_to_reduce=1.0),
        Uncertainty("initial_capability", 0.25, 0.60, cost_to_reduce=1.0),
        Uncertainty("quit_sensitivity", 0.5, 3.0, cost_to_reduce=3.0),
        Uncertainty("gap_closing_time", 1.5, 6.0, cost_to_reduce=0.5),
        Uncertainty("fill_time", 1.0, 1.5, cost_to_reduce=0.5),
    ]


def bounds() -> list[Bound]:
    base = run(0.0, HEADLINE_MONTH)
    ceiling = 1.15 * base.series["headcount"][0]
    return [
        Bound("headcount", high=ceiling,
              reason="payroll ceiling: fifteen percent over January 2015"),
        Bound("effective_capability", low=base.series["effective_capability"][0],
              reason="no policy may end with less capability than it started with"),
    ]


def headline() -> list[dict[str, float | str]]:
    """Headcount and effective capability at month 24 under each rule, and the record's row."""
    rows: list[dict[str, float | str]] = []
    for policy in policies():
        result = run(TARGET_STEP, HEADLINE_MONTH, policy.settings)
        rows.append({
            "rule": policy.name,
            "headcount": result.series["headcount"][-1],
            "effective_capability": result.series["effective_capability"][-1],
            "capability_share": (result.series["effective_capability"][-1]
                                 / result.series["headcount"][-1]),
            "cumulative_hires": sum(result.series["hires"][:HEADLINE_MONTH]),
        })
    employment = record()["employment"]
    hires = record()["hires"]
    rows.append({
        "rule": "record (CES, JOLTS)",
        "headcount": employment.values[HEADLINE_MONTH],
        "effective_capability": float("nan"),
        "capability_share": float("nan"),
        "cumulative_hires": sum(hires.values[:HEADLINE_MONTH]),
    })
    return rows


def overshoot(gap_closing_time: float = 1.0) -> dict[str, float]:
    """The hire-harder rule pushed to a one-month gap-closing time: boom, freeze, and overshoot."""
    result = run(TARGET_STEP, HEADLINE_MONTH, {"gap_closing_time": gap_closing_time})
    hires = result.series["hires"]
    return {"peak_hires": max(hires[:HEADLINE_MONTH]),
            "peak_month": float(hires.index(max(hires[:HEADLINE_MONTH]))),
            "trough_hires": min(hires[1:HEADLINE_MONTH]),
            "trough_month": float(hires.index(min(hires[1:HEADLINE_MONTH]))),
            "headcount": result.series["headcount"][-1],
            "ceiling": bounds()[0].high or 0.0}


def comparison(draws: int = COMPARE_DRAWS, seed: int = SEED
               ) -> tuple[list[Evaluation], dict[str, object]]:
    """Chapter 30's compare, run once per bounded metric and merged, then recommend.

    `compare` checks only the bounds on its objective, so the payroll ceiling is checked in a
    pass whose objective is headcount and its violations are carried into the capability pass.
    """
    doc = fitted_document(TARGET_STEP)
    capability = compare(doc, policies(), uncertainties(), "effective_capability", bounds(),
                         draws=draws, seed=seed)
    heads = compare(doc, policies(), uncertainties(), "headcount", bounds(), draws=draws,
                    seed=seed)
    for cap, head in zip(capability, heads):
        for violation in head.violations:
            if violation not in cap.violations:
                cap.violations.append(violation)
    return capability, recommend(capability)


def ranking() -> list[tuple[str, float]]:
    """Which uncertainty moves month 24 capability the most, one at a time."""
    return ranked(fitted_document(TARGET_STEP), uncertainties(), "effective_capability",
                  RunSettings(dt=1.0, horizon=float(HEADLINE_MONTH)))


def envelope(draws: int = DRAWS, seed: int = SEED) -> dict[str, float]:
    """Month 20 capability under the baseline rule across every uncertainty at once."""
    values = sorted(sample(fitted_document(TARGET_STEP), uncertainties(), "effective_capability",
                           draws, seed))
    return {"low": values[0], "p10": values[len(values) // 10],
            "median": values[len(values) // 2],
            "p90": values[(9 * len(values)) // 10], "high": values[-1], "draws": len(values)}


def month20(policy: str) -> float:
    """Deterministic month 20 capability under one rule at the fitted values."""
    settings = next(p.settings for p in policies() if p.name == policy)
    return metric(fitted_document(TARGET_STEP), settings, "effective_capability",
                  RunSettings(dt=1.0, horizon=float(COMPARISON_MONTH)))


if __name__ == "__main__":
    import json
    import time
    t0 = time.time()
    for row in report():
        print(row)
    print("holdout", fit().holdout_error, "evaluations", fit().evaluations,
          f"{time.time() - t0:.1f}s")
    print("ramp profile", ramp_profile())
    print("identity", identity_gap(), "model residual", model_identity_residual())
    print(json.dumps(defects(), indent=1))
    for row in headline():
        print(row)
    evaluations, verdict = comparison()
    for e in evaluations:
        print(e.policy, round(e.mean(), 1), round(e.worst(), 1), len(e.violations),
              e.violations[:1])
    print({k: v for k, v in verdict.items() if k != "excluded"},
          {k: len(v) for k, v in verdict["excluded"].items()})
    for name in ("baseline", "hire_harder", "retain", "shorten_ramp"):
        print("month20", name, month20(name))
    print("overshoot", overshoot())
    print("ranking", ranking())
    print("envelope", envelope())
    print(f"{time.time()-t0:.1f}s")
