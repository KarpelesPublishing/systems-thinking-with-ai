"""Fit the backlog model to the NHS England RTT record, test it out of window, compare policies.

Every number the chapter prints comes from a function here, and
`tests/chapters/test_case_elective_backlog.py` pins each one. The fit follows Chapter 35's rules:
a grid over three declared knobs, an error with a tolerance stated before the search, fitted
values marked `inferred`, and a holdout window the fit never saw, reported whether or not it
passes.
"""

import functools
from dataclasses import dataclass

from chapters.chapter_20_model_document.code.document import ModelDocument
from chapters.chapter_22_runtime.code.runtime import Result, RunSettings, Runtime
from chapters.chapter_28_critic.code.critic import (
    conservation_findings,
    defect_report,
    dimensional_findings,
    extreme_condition_findings,
    structural_findings,
)
from chapters.chapter_29_experiments.code.sensitivity import Uncertainty, ranked, sample
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
    months_between,
    read_series,
    with_fitted,
)
from chapters.chapter_36_elective_backlog.code.model import (
    FREE_KNOBS,
    RECORD,
    SOURCE,
    build,
    month_index,
    read_record,
)

FIT_START, FIT_END = "2016-04", "2019-12"
HOLDOUT_START = "2021-04"
POLICY_START = "2022-06"
TOLERANCE = 0.05
DT = 0.5

# Chapter 30's comparison runs every policy for the horizon its `metric` fixes, twenty months at
# a step of one. The headline table runs longer, and says so.
COMPARE_HORIZON = 20


# The record.


def record() -> list[Series]:
    """The two series the fit and the holdout read, in months since April 2016."""
    total = read_series(RECORD, "period", "total_incomplete", name="total_incomplete",
                        unit="pathways", source=SOURCE, time_origin=FIT_START)
    rows = read_record()
    over = Series(
        name="over_52_weeks",
        times=tuple(months_between(FIT_START, r["period"]) for r in rows if r["over_52_weeks"]),
        values=tuple(float(r["over_52_weeks"]) for r in rows if r["over_52_weeks"]),
        unit="pathways", source=SOURCE, checksum=total.checksum)
    return [total, over]


def last_period() -> str:
    return read_record()[-1]["period"]


# The fit.


def document(start: str = FIT_START) -> ModelDocument:
    """The unfitted model, stocks set from the record at `start`, run to the end of the record."""
    horizon = int(months_between(start, last_period()))
    return build(start, horizon=max(horizon, 1))


def knobs() -> list[Knob]:
    return [Knob("validation_rate", 0.02, 0.10, steps=5),
            Knob("system_growth", 0.0, 0.008, steps=5),
            Knob("tail_steepness", 0.5, 4.5, steps=5)]


def targets() -> list[Target]:
    end = months_between(FIT_START, FIT_END)
    total, over = record()
    return [Target("total_incomplete", total.window(0, end), tolerance=TOLERANCE, error="mape"),
            Target("long_waiters", over.window(0, end), tolerance=0.5, error="shape",
                   weight=0.2)]


def holdout_targets() -> list[Target]:
    start = months_between(FIT_START, HOLDOUT_START)
    total, over = record()
    return [Target("total_incomplete", total.window(start, 1e9), tolerance=TOLERANCE,
                   error="mape"),
            Target("long_waiters", over.window(start, 1e9), tolerance=0.5, error="shape",
                   weight=0.2)]


def settings(horizon: float) -> RunSettings:
    return RunSettings(dt=DT, horizon=horizon)


@functools.lru_cache(maxsize=1)
def fit() -> Fit:
    """Grid fit on 2016-04 to 2019-12, then the holdout from 2021-04, recorded in the Fit."""
    doc = document()
    result = grid_fit(doc, knobs(), targets(), settings(months_between(FIT_START, FIT_END)))
    holdout(doc, result, holdout_targets(), settings(float(doc.horizon)))
    return result


def fitted_document(start: str = FIT_START) -> ModelDocument:
    """The model with fitted values in place, marked inferred, stocks from the record at start."""
    return with_fitted(document(start), fit(), targets())


def report() -> list[dict[str, object]]:
    return fit_report(fit(), targets())


def critic_report(doc: ModelDocument | None = None) -> dict[str, list[str]]:
    """What Chapter 28's critic says about the fitted document."""
    doc = doc or fitted_document()
    findings = (structural_findings(doc) + dimensional_findings(doc)
                + conservation_findings(doc) + extreme_condition_findings(doc, "waiting_list")
                + extreme_condition_findings(doc, "long_waiters"))
    return defect_report(findings)


# Reading a run.


def run(doc: ModelDocument, horizon: float) -> Result:
    return Runtime(doc, settings(horizon)).run()


def at_month(result: Result, name: str, month: float) -> float:
    return result.series[name][int(round(month / result.settings.dt))]


def record_at(period: str) -> dict[str, float]:
    row = read_record()[month_index(read_record(), period)]
    return {"total_incomplete": float(row["total_incomplete"]),
            "over_52_weeks": float(row["over_52_weeks"])}


def period_after(start: str, months: int) -> str:
    y, m = int(start[:4]), int(start[5:7]) + months
    return f"{y + (m - 1) // 12:04d}-{(m - 1) % 12 + 1:02d}"


def recovery_date(result: Result, threshold: float, variable: str = "total_incomplete",
                  start: str = POLICY_START) -> str | None:
    """The first month at which `variable` is at or below `threshold`, or None if never.

    The exported artifact. It answers one question a manager asks, and a None is an answer
    too: within this horizon, under these settings, the list does not get there.
    """
    for index, value in enumerate(result.series[variable]):
        if value <= threshold:
            return period_after(start, int(round(result.times[index])))
    return None


# Policies.


POLICIES = [
    Policy("uniform_uplift", {"capacity_uplift": 0.10}, owner="operations director",
           reversible=True, note="ten percent more capacity, spread across the whole list"),
    Policy("longest_first", {"long_share": 0.25}, owner="operations director", reversible=True,
           note="a quarter of capacity directed at pathways already over 52 weeks"),
    Policy("validation_push", {"validation_rate": 0.09}, owner="information governance lead",
           reversible=False,
           note="a validation drive that removes nine percent of the list a month; a removed "
                "pathway does not come back as the same record"),
]

BOUNDS = [
    Bound("long_waiters", high=357_577.0,
          reason="long waiters at the end of the run must not exceed the 357,577 the record "
                 "shows at the start of the run"),
    Bound("mean_wait_weeks", high=18.0,
          reason="the mean wait implied by the list and the throughput must sit inside the "
                 "18-week standard"),
    Bound("capacity", high=1_800_000.0,
          reason="the capacity budget: completed pathways per month must stay under 1.8 million"),
]

UNCERTAINTIES = [
    Uncertainty("suppression_strength", 0.0, 0.5),
    Uncertainty("complexity_penalty", 0.0, 1.0),
    Uncertainty("long_share", 0.02, 0.15),
    Uncertainty("tail_steepness", 0.5, 4.5),
    Uncertainty("system_growth", 0.0, 0.008),
]


def policy_document() -> ModelDocument:
    """The fitted structure with stocks and referrals reset to the record at POLICY_START."""
    return fitted_document(POLICY_START)


def baseline_policy() -> Policy:
    return Policy("baseline", {"capacity_uplift": 0.0}, owner="nobody", reversible=True,
                  note="the fitted document unchanged")


def with_policy(doc: ModelDocument, policy: Policy) -> ModelDocument:
    from chapters.chapter_35_calibration.code.calibrate import with_values
    return with_values(doc, policy.settings)


def headline_table(months: tuple[int, ...] = (0, 24, 48)) -> list[dict[str, object]]:
    """Record, fitted model, and each policy from POLICY_START at the named months."""
    doc = policy_document()
    rows: list[dict[str, object]] = []
    record_row: dict[str, object] = {"series": "record"}
    for m in months:
        period = period_after(POLICY_START, m)
        try:
            record_row[str(m)] = round(record_at(period)["total_incomplete"])
        except KeyError:
            record_row[str(m)] = None
    rows.append(record_row)
    for policy in [baseline_policy()] + POLICIES:
        result = run(with_policy(doc, policy), max(months))
        row: dict[str, object] = {"series": "model" if policy.name == "baseline"
                                  else policy.name}
        for m in months:
            row[str(m)] = round(at_month(result, "total_incomplete", m))
        rows.append(row)
    return rows


def long_waiter_table(months: tuple[int, ...] = (0, 24, 48)) -> list[dict[str, object]]:
    """The same table for the over-52-week stock."""
    doc = policy_document()
    rows: list[dict[str, object]] = []
    record_row: dict[str, object] = {"series": "record"}
    for m in months:
        try:
            record_row[str(m)] = round(record_at(period_after(POLICY_START, m))["over_52_weeks"])
        except KeyError:
            record_row[str(m)] = None
    rows.append(record_row)
    for policy in [baseline_policy()] + POLICIES:
        result = run(with_policy(doc, policy), max(months))
        row: dict[str, object] = {"series": "model" if policy.name == "baseline"
                                  else policy.name}
        for m in months:
            row[str(m)] = round(at_month(result, "long_waiters", m))
        rows.append(row)
    return rows


@dataclass
class PolicyComparison:
    """Chapter 30's evaluations on the objective, with every bound checked on its own metric."""

    evaluations: list[Evaluation]
    recommendation: dict[str, object]


def compare_policies(draws: int = 40, seed: int = 7) -> PolicyComparison:
    """Every policy against the same draws, ranked on list reduction with three bounds.

    Chapter 30's `compare` checks a bound only when it names the objective, so each bound is
    evaluated as its own objective and the violations are folded back into the ranking.
    """
    doc = policy_document()
    policies = [baseline_policy()] + POLICIES
    evaluations = compare(doc, policies, UNCERTAINTIES, "list_reduction", [], draws, seed)
    for bound in BOUNDS:
        checks = compare(doc, policies, UNCERTAINTIES, bound.metric_name, [bound], draws, seed)
        for evaluation, check in zip(evaluations, checks):
            for message in check.violations:
                if message not in evaluation.violations:
                    evaluation.violations.append(message)
    return PolicyComparison(evaluations, recommend(evaluations))


def sensitivity_ranking(metric: str = "long_waiters") -> list[tuple[str, float]]:
    """Which uncertainty moves the long-wait stock most at Chapter 30's horizon."""
    return ranked(policy_document(), UNCERTAINTIES, metric)


def uncertainty_envelope(draws: int = 200, seed: int = 11, metric: str = "total_incomplete"
                         ) -> dict[str, float]:
    """Two hundred draws across the five uncertainty ranges, as low, median, and high."""
    values = sorted(sample(policy_document(), UNCERTAINTIES, metric, draws, seed))
    n = len(values)
    return {"draws": float(n), "p05": values[int(0.05 * (n - 1))],
            "median": values[n // 2], "p95": values[int(0.95 * (n - 1))]}


def knob_guard(doc: ModelDocument | None = None) -> int:
    """The number of free knobs in the document; the chapter's rule is at most three."""
    doc = doc or document()
    return sum(1 for v in doc.variables if v.kind == "parameter" and v.id in FREE_KNOBS)


def evidence_summary(doc: ModelDocument | None = None) -> dict[str, list[str]]:
    doc = doc or fitted_document()
    out: dict[str, list[str]] = {}
    for v in doc.variables:
        if v.kind in ("stock", "parameter"):
            out.setdefault(v.evidence, []).append(v.id)
    return out
