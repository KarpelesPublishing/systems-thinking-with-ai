"""Fit the capacity-cycle document to the manufacturing utilization record, and test it.

The record is monthly manufacturing capacity utilization (Federal Reserve G.17, retrieved through
FRED). The fit window is 1990-01 to 2019-12. The fit does not score the path. An oscillator
scored month by month against a record is rewarded for landing its peaks on the record's peaks,
which is phase luck. With a sufficiently large phase mismatch, a model with the right period can
score worse than a flat line; a small phase error need not do so. The two targets chosen here are
its dominant period and peak-to-trough amplitude, each as a relative error with its own tolerance.

Three knobs. Two are parameters the runtime can move, investment gain and margin sensitivity, and
Chapter 35's grid search moves them. The third is the construction delay, which lives in a delay
variable's delay_time and not in a value, so the fit rebuilds the document for each candidate
delay and runs the grid inside. Everything fitted is marked inferred.
"""

import statistics
from dataclasses import replace
from functools import lru_cache
from pathlib import Path

from chapters.chapter_19_integration.code.solvers import converged
from chapters.chapter_20_model_document.code.document import ModelDocument
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from chapters.chapter_28_critic.code.critic import (
    conservation_findings,
    defect_report,
    dimensional_findings,
    extreme_condition_findings,
    structural_findings,
)
from chapters.chapter_29_experiments.code.sensitivity import Uncertainty, ranked
from chapters.chapter_30_policy_search.code.policies import (
    Bound,
    Evaluation,
    Policy,
    recommend,
)
from chapters.chapter_35_calibration.code.calibrate import (
    Fit,
    Knob,
    Series,
    Target,
    error_of,
    fit_report,
    grid_fit,
    holdout,
    read_series,
    with_fitted,
    with_values,
)
from chapters.chapter_38_capacity_cycle.code import model as capacity

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "data/fred_capacity/capacity_monthly.csv"
SOURCE = ("Federal Reserve Board G.17 manufacturing capacity utilization (MCUMFN), "
          "retrieved through FRED 2026-09-03")
FIT_WINDOW = ("1990-01", "2019-12")
HOLDOUT_WINDOW = ("1972-01", "1989-12")
CONSTRUCTION_GRID = (12.0, 18.0, 24.0, 30.0)
PERIOD_TOLERANCE = 0.20
AMPLITUDE_TOLERANCE = 0.25
SETTINGS = RunSettings(dt=1.0, horizon=360.0)


# ---------------------------------------------------------------- the two statistics


def _detrended(values: list[float]) -> list[float]:
    """The series minus its least-squares straight line. The model has no trend; the record does."""
    n = len(values)
    if n < 3:
        raise ValueError("a cycle statistic needs at least three points")
    xm = (n - 1) / 2
    ym = sum(values) / n
    sxx = sum((i - xm) ** 2 for i in range(n))
    slope = sum((i - xm) * (y - ym) for i, y in enumerate(values)) / sxx
    return [y - (ym + slope * (i - xm)) for i, y in enumerate(values)]


def autocorrelation(values: list[float]) -> list[float]:
    """Autocorrelation of the detrended series at lags 0 to half the length."""
    d = _detrended(values)
    n = len(d)
    var = sum(x * x for x in d)
    if var == 0:
        return [1.0] + [0.0] * (n // 2)
    return [sum(d[i] * d[i + k] for i in range(n - k)) / var for k in range(n // 2 + 1)]


def cycle_period(values: list[float]) -> int | None:
    """Dominant period in months: the first local maximum of the autocorrelation after it first
    crosses zero. None when the series never returns to positive correlation inside half its
    length, which is what a flat or a one-way series produces."""
    ac = autocorrelation(values)
    k = 1
    while k < len(ac) and ac[k] > 0:
        k += 1
    for j in range(k + 1, len(ac) - 1):
        if ac[j] > ac[j - 1] and ac[j] >= ac[j + 1]:
            return j
    return None


def amplitude(values: list[float]) -> float:
    """Peak-to-trough range of the detrended series, in the series' own unit."""
    d = _detrended(values)
    return max(d) - min(d)


def period_error(model: list[float], observed: list[float]) -> float:
    """Relative error of the dominant period. A model with no cycle scores the whole record."""
    target = cycle_period(observed)
    if target is None:
        raise ValueError("the observed window has no dominant period to fit")
    got = cycle_period(model)
    if got is None:
        return 1.0
    return abs(got - target) / target


def amplitude_error(model: list[float], observed: list[float]) -> float:
    """Relative error of the peak-to-trough amplitude."""
    target = amplitude(observed)
    if target == 0:
        raise ValueError("the observed window is flat")
    return abs(amplitude(model) - target) / target


# ---------------------------------------------------------------- record, targets, knobs


def _window(start: str, end: str) -> Series:
    """The utilization record between two months, with time counted from the first of them."""
    full = read_series(RECORD, "period", "utilization", name="utilization", unit="percent",
                       source=SOURCE, time_origin=start)
    months = (int(end[:4]) - int(start[:4])) * 12 + int(end[5:7]) - int(start[5:7])
    return full.window(0.0, float(months))


def record() -> Series:
    return _window(*FIT_WINDOW)


def holdout_record() -> Series:
    return _window(*HOLDOUT_WINDOW)


def document(construction_delay: float = capacity.DEFAULT_CONSTRUCTION_DELAY) -> ModelDocument:
    return capacity.document(construction_delay=construction_delay)


def knobs() -> list[Knob]:
    return [
        Knob("investment_gain", 0.05, 0.35, steps=4),
        Knob("margin_sensitivity", 0.5, 2.0, steps=4),
    ]


def _targets_for(series: Series) -> list[Target]:
    return [
        Target("utilization", series, PERIOD_TOLERANCE, custom=period_error),
        Target("utilization_level", series, AMPLITUDE_TOLERANCE, custom=amplitude_error),
    ]


def targets() -> list[Target]:
    return _targets_for(record())


def holdout_targets() -> list[Target]:
    return _targets_for(holdout_record())


# ---------------------------------------------------------------- the fit

# The values fit() last produced, written down so the figures and the policy comparison do not
# each repeat a search that takes a minute. tests/chapters/test_case_capacity_cycle.py runs the
# search and fails if it no longer lands here.
PINNED_FIT = {"investment_gain": 0.25, "margin_sensitivity": 0.8333, "construction_delay": 18.0}


@lru_cache(maxsize=1)
def fit() -> Fit:
    """Grid over the two parameter knobs inside a loop over the construction delay. Slow."""
    best: Fit | None = None
    best_delay = None
    evaluations = 0
    for delay in CONSTRUCTION_GRID:
        candidate = grid_fit(document(delay), knobs(), targets(), SETTINGS, refinements=1)
        evaluations += candidate.evaluations
        if best is None or candidate.error < best.error:
            best, best_delay = candidate, delay
    assert best is not None and best_delay is not None
    best.fitted["construction_delay"] = best_delay
    best.searched["construction_delay"] = (CONSTRUCTION_GRID[0], CONSTRUCTION_GRID[-1])
    best.evaluations = evaluations
    best.method += f", construction delay looped over {CONSTRUCTION_GRID}"
    return best


@lru_cache(maxsize=1)
def pinned_fit() -> Fit:
    """A Fit object at the pinned values, scored on the fit window, without searching."""
    values = {k: v for k, v in PINNED_FIT.items() if k != "construction_delay"}
    doc = with_values(document(PINNED_FIT["construction_delay"]), values)
    total, per_target, residuals = error_of(doc, targets(), SETTINGS)
    searched = {k.variable: (k.low, k.high) for k in knobs()}
    searched["construction_delay"] = (CONSTRUCTION_GRID[0], CONSTRUCTION_GRID[-1])
    return Fit(document_hash=doc.hash(), fitted=dict(PINNED_FIT), error=total,
               per_target=per_target, residuals=residuals,
               method=f"grid search, 2 knobs, 1 refinement, construction delay looped over "
                      f"{CONSTRUCTION_GRID}; values pinned from fit()",
               evaluations=0, searched=searched)


def fitted_construction_delay() -> float:
    return PINNED_FIT["construction_delay"]


def fitted_document() -> ModelDocument:
    """The document at the pinned fitted values, every fitted quantity marked inferred."""
    result = pinned_fit()
    base = with_fitted(document(fitted_construction_delay()), result, targets())
    low, high = result.searched["construction_delay"]
    note = (f"inferred: construction delay chosen from {low:g} to {high:g} months by the same "
            f"fit; a sector-wide average of thousands of plants, not a measured build time")
    variables = [replace(v, evidence="inferred", note=note) if v.id == "completions" else v
                 for v in base.variables]
    return ModelDocument(name=base.name, version=base.version, variables=variables,
                         horizon=base.horizon, horizon_unit=base.horizon_unit,
                         time_step=base.time_step)


def holdout_errors() -> dict[str, float]:
    """The fitted document against 1972 to 1989, which the fit never saw."""
    return holdout(document(fitted_construction_delay()), pinned_fit(), holdout_targets(),
                   SETTINGS)


def report() -> list[dict[str, object]]:
    holdout_errors()
    return fit_report(pinned_fit(), targets())


def model_path(doc: ModelDocument | None = None, dt: float = 1.0, solver: str = "euler"
               ) -> list[float]:
    """Monthly utilization from the fitted document, or from the one given."""
    return capacity.utilization_path(doc or fitted_document(), dt=dt, solver=solver)


# ---------------------------------------------------------------- checks


def critic_report() -> dict[str, list[str]]:
    doc = fitted_document()
    findings = (structural_findings(doc) + dimensional_findings(doc) + conservation_findings(doc)
                + extreme_condition_findings(doc, "capacity"))
    return defect_report(findings)


def endogenous_check() -> dict[str, float | None]:
    """Demand is constant already; this states it and reads the swing off the run."""
    doc = fitted_document()
    assert doc.by_id("demand").kind == "parameter"
    path = model_path(doc)
    return {"period": cycle_period(path), "amplitude": amplitude(path),
            "demand": float(doc.by_id("demand").value)}


def step_refinement(tolerance_months: float = 6.0) -> dict[str, object]:
    """Chapter 19's check: the period at dt 1, 1/2 and 1/4 months, and whether it has settled."""
    periods = [cycle_period(model_path(dt=dt)) for dt in (1.0, 0.5, 0.25)]
    if any(p is None for p in periods):
        raise RuntimeError("the fitted model lost its cycle at a finer step")
    values = [float(p) for p in periods if p is not None]
    return {"dt": (1.0, 0.5, 0.25), "periods": tuple(periods),
            "converged": converged(values, tolerance_months),
            "largest_change": max(abs(a - b) for a, b in zip(values, values[1:]))}


def construction_delay_sweep(delays: tuple[float, ...] = (12.0, 18.0, 24.0, 30.0, 36.0, 48.0)
                             ) -> list[dict[str, float | None]]:
    """Period and amplitude as the construction delay moves, other fitted values held."""
    result = pinned_fit()
    out = []
    for delay in delays:
        doc = with_values(document(delay), {k: v for k, v in result.fitted.items()
                                            if k != "construction_delay"})
        path = model_path(doc)
        out.append({"construction_delay": delay, "period": cycle_period(path),
                    "amplitude": round(amplitude(path), 2)})
    return out


def phase_envelope(starts: tuple[float, ...] = (70.0, 74.0, 78.0, 82.0, 86.0),
                   months: int = 240) -> dict[str, object]:
    """Run the fitted document from several starting utilizations and read the spread.

    The same structure started at a different point in its cycle puts its next trough in a
    different year. The envelope is what the model can say about a date: not much.
    """
    doc = fitted_document()
    paths = []
    for start in starts:
        variables = [replace(v, value=100.0 * 80.0 / start) if v.id == "capacity" else v
                     for v in doc.variables]
        probe = ModelDocument(name=doc.name, version=doc.version, variables=variables,
                              horizon=doc.horizon, horizon_unit=doc.horizon_unit,
                              time_step=doc.time_step)
        paths.append(model_path(probe)[:months + 1])
    band = [max(p[t] for p in paths) - min(p[t] for p in paths) for t in range(months + 1)]
    troughs = [first_trough(p) for p in paths]
    return {"starts": starts, "band_at_120": round(band[120], 1),
            "widest_band": round(max(band), 1),
            "first_trough_months": tuple(troughs),
            "trough_spread_months": max(troughs) - min(troughs)}


def first_trough(path: list[float], window: int = 12) -> int:
    """Month of the first point lower than every point within `window` months either side."""
    for t in range(window, len(path) - window):
        if all(path[t] <= path[s] for s in range(t - window, t + window + 1)):
            return t
    raise ValueError("no trough inside the path")


# ---------------------------------------------------------------- policies


def policies() -> list[Policy]:
    """The rule in the record, and three rules somebody might swap it for."""
    result = pinned_fit()
    gain = result.fitted["investment_gain"]
    sensitivity = result.fitted["margin_sensitivity"]
    # The lookup rises about 0.07 per utilization point near normal, so a rule reading current
    # utilization with this gain is as aggressive as the fitted margin rule, minus the
    # perception delay. Same appetite, shorter information path.
    equivalent = round(gain * sensitivity * 7.0, 3)
    return [
        Policy("build_when_margins_good", {"investment_gain": gain}, owner="sector, as fitted",
               reversible=True, note="the rule the fit found consistent with the record"),
        Policy("utilisation_trigger", {"investment_gain": 0.0, "rule_gain_utilization": equivalent},
               owner="capital planning", reversible=True,
               note="respond to measured utilization now, not to reported margins later"),
        Policy("smoothed_margin_trigger", {"investment_gain": gain, "margin_dead_band": 0.1},
               owner="capital planning", reversible=True,
               note="the fitted rule, but margins within a tenth of normal trigger nothing"),
        Policy("fixed_replacement", {"investment_gain": 0.0}, owner="capital planning",
               reversible=True, note="replace retirements only; ignore margins entirely"),
    ]


def uncertainties() -> list[Uncertainty]:
    sensitivity = pinned_fit().fitted["margin_sensitivity"]
    return [
        Uncertainty("demand", 74.0, 86.0, cost_to_reduce=1.0),
        Uncertainty("capital_lifetime", 144.0, 240.0, cost_to_reduce=2.0),
        Uncertainty("margin_sensitivity", sensitivity * 0.75, sensitivity * 1.25,
                    cost_to_reduce=3.0),
    ]


def bounds() -> list[Bound]:
    return [
        Bound("mean_utilization", low=74.0,
              reason="idle capital: more than three and a half points under the record mean"),
        Bound("amplitude", high=round(amplitude(list(record().values)), 2),
              reason="no worse a swing than the record"),
    ]


def _outcomes(doc: ModelDocument, overrides: dict[str, float]) -> dict[str, float]:
    result = Runtime(with_values(doc, overrides), SETTINGS).run()
    return {"steadiness": result.final("steadiness"),
            "mean_utilization": result.final("mean_utilization"),
            "amplitude": amplitude(result.series["utilization"])}


def policy_statistics() -> list[dict[str, object]]:
    """Each policy at the fitted values with no draws: period, amplitude, mean utilization."""
    doc = fitted_document()
    out = []
    for policy in policies():
        result = Runtime(with_values(doc, policy.settings), SETTINGS).run()
        path = result.series["utilization"]
        out.append({"policy": policy.name, "period": cycle_period(path),
                    "amplitude": round(amplitude(path), 1),
                    "mean_utilization": round(result.final("mean_utilization"), 1),
                    "steadiness": round(result.final("steadiness"), 2)})
    return out


def compare_policies(draws: int = 12, seed: int = 7) -> list[Evaluation]:
    """Chapter 30's comparison, run here so the horizon and the bounds can be stated.

    Chapter 30's `compare` reads one metric at its default horizon and applies bounds to that
    metric only. A capacity cycle needs thirty years and two bounds on quantities other than
    the objective, so this loop builds the same Evaluation objects and hands them to Chapter
    30's `recommend` unchanged.
    """
    import random

    doc = fitted_document()
    evaluations = []
    for policy in policies():
        rng = random.Random(seed)
        evaluation = Evaluation(policy=policy.name, reversible=policy.reversible)
        for _ in range(draws):
            overrides = {**{u.variable: rng.uniform(u.low, u.high) for u in uncertainties()},
                         **policy.settings}
            try:
                outcome = _outcomes(doc, overrides)
            except RuntimeError as exc:
                message = f"the model could not be run: {exc}"
                if message not in evaluation.violations:
                    evaluation.violations.append(message)
                continue
            evaluation.values.append(outcome["steadiness"])
            for bound in bounds():
                message = bound.violated_by(outcome[bound.metric_name])
                if message and message not in evaluation.violations:
                    evaluation.violations.append(message)
        evaluations.append(evaluation)
    return evaluations


def recommendation(draws: int = 12, seed: int = 7) -> dict[str, object]:
    return recommend(compare_policies(draws, seed))


def sensitivity_ranking() -> list[tuple[str, float]]:
    """Chapter 29: which uncertainty moves steadiness most, one at a time, over thirty years."""
    return ranked(fitted_document(), uncertainties(), "steadiness", SETTINGS)


def summary() -> dict[str, object]:
    """Every number the chapter prints, in one place."""
    rec = list(record().values)
    hold = list(holdout_record().values)
    path = model_path()
    return {
        "record_period": cycle_period(rec), "record_amplitude": round(amplitude(rec), 1),
        "record_mean": round(statistics.fmean(rec), 1),
        "holdout_period": cycle_period(hold), "holdout_amplitude": round(amplitude(hold), 1),
        "model_period": cycle_period(path), "model_amplitude": round(amplitude(path), 1),
        "fitted": {k: round(v, 4) for k, v in pinned_fit().fitted.items()},
        "fit_errors": {k: round(v, 3) for k, v in pinned_fit().per_target.items()},
        "holdout_errors": {k: round(v, 3) for k, v in holdout_errors().items()},
    }


if __name__ == "__main__":
    import json
    import sys

    if "--search" in sys.argv:
        searched = fit()
        print({k: round(v, 4) for k, v in searched.fitted.items()}, searched.evaluations)
    print(json.dumps(summary(), indent=1))
    print(json.dumps(report(), indent=1, default=str))
    print(json.dumps(critic_report(), indent=1))
    print(json.dumps(step_refinement(), indent=1))
    print(json.dumps(construction_delay_sweep(), indent=1))
    print(json.dumps(phase_envelope(), indent=1))
    print(json.dumps(policy_statistics(), indent=1))
    print(json.dumps([e.__dict__ for e in compare_policies()], indent=1))
    print(json.dumps(recommendation(), indent=1))
    print(sensitivity_ranking())
