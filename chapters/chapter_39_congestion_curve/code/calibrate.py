"""Fit the taxi-out-versus-load curve to the BTS record, and say what the fit is worth.

The record has three derived files for the thirty busiest origin airports. Load for one airport
clock hour is that hour's scheduled departures divided by the airport's fit-year 95th percentile
hourly count, so load 1 means the hour is as full as the busiest one in twenty. Hours are binned
by load, and the flight-weighted mean taxi-out (gate pushback to wheels up, a proxy for runway
queueing) is taken per bin. A three-parameter convex curve is fitted by the same grid search
Chapter 35 uses:

    taxi_out(load) = base + curvature * max(0, load - knee) ** 2

The fitted curve is exported as lookup points on the bin centers, so the lookup's domain is the
range the record covers and nothing wider. Every fitted value is evidence level `inferred`: the
curve is consistent with a congestion structure, and is not evidence for one.

Departure delay against the schedule, the statistic most reports quote, is also read from the
record: it does not rise with hourly load, and it rises through the clock day instead.
"""

import csv
import statistics
from pathlib import Path

from chapters.chapter_15_lookups.code.lookup import Lookup
from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from chapters.chapter_28_critic.code.critic import (
    conservation_findings,
    defect_report,
    dimensional_findings,
    extreme_condition_findings,
    structural_findings,
)
from chapters.chapter_29_experiments.code.sensitivity import Uncertainty
from chapters.chapter_30_policy_search.code.policies import Bound, Policy, compare
from chapters.chapter_35_calibration.code.calibrate import Knob, Series, checksum_of, mae
from chapters.chapter_39_congestion_curve.code.model import build_document

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "bts_ontime"
MONTHS = DATA_DIR / "airport_month_delay.csv"
HOURS = DATA_DIR / "airport_hour_load.csv"
CLOCK = DATA_DIR / "airport_clock_hour.csv"
SOURCE = "BTS Reporting Carrier On-Time Performance, thirty busiest origins, retrieved 2026-09-03"
FIT_YEAR = 2023
HOLDOUT_YEAR = 2024
BIN_WIDTH = 0.1
MIN_BIN_FLIGHTS = 20_000
MAE_BOUND_MINUTES = 2.0


# ---------------------------------------------------------------- the record


def _read(path: Path, numeric: tuple[str, ...]) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        if any(row[k] == "" for k in numeric):
            continue
        out.append({**row, **{k: float(row[k]) for k in numeric}})
    return out


def read_months(path: Path = MONTHS) -> list[dict]:
    """Every airport-month row as floats, with the year split out."""
    rows = _read(path, ("scheduled_departures", "peak_hour_departures",
                        "mean_dep_delay_minutes", "cancellation_share", "mean_taxi_out",
                        "departures_above_p90", "departures_above_p95",
                        "p90_hourly_departures", "p95_hourly_departures", "load"))
    for row in rows:
        row["year"] = int(row["period"][:4])
    return rows


def read_hour_bins(path: Path = HOURS) -> list[dict]:
    """Every airport-year load bin as floats."""
    rows = _read(path, ("year", "load_bin_low", "flights", "mean_taxi_out",
                        "mean_dep_delay_minutes", "cancellation_share"))
    for row in rows:
        row["year"] = int(row["year"])
    return rows


def read_clock_hours(path: Path = CLOCK) -> list[dict]:
    """Every airport-year clock hour as floats."""
    rows = _read(path, ("year", "hour", "flights", "mean_dep_delay_minutes", "mean_taxi_out"))
    for row in rows:
        row["year"] = int(row["year"])
        row["hour"] = int(row["hour"])
    return rows


def rows_for_year(rows: list[dict], year: int) -> list[dict]:
    return [r for r in rows if r["year"] == year]


def pooled_bins(rows: list[dict], value: str = "mean_taxi_out",
                min_flights: int = MIN_BIN_FLIGHTS) -> list[tuple[float, float, int]]:
    """(bin center, flight-weighted mean of `value`, flights) per load bin across airports."""
    groups: dict[float, list[float]] = {}
    for row in rows:
        total = groups.setdefault(row["load_bin_low"], [0.0, 0.0])
        total[0] += row[value] * row["flights"]
        total[1] += row["flights"]
    out = []
    for low in sorted(groups):
        weighted, flights = groups[low]
        if flights >= min_flights:
            out.append((round(low + BIN_WIDTH / 2, 4), weighted / flights, int(flights)))
    return out


def bins_as_series(bins: list[tuple[float, float, int]], path: Path = HOURS) -> Series:
    """The bins as Chapter 35's Series: load as time, taxi-out as value, with checksum."""
    return Series(name="binned_taxi_out", times=tuple(b[0] for b in bins),
                  values=tuple(b[1] for b in bins), unit="minute/departure", source=SOURCE,
                  checksum=checksum_of(path) if path.exists() else "")


# ---------------------------------------------------------------- the curve


def curve(load: float, base: float, knee: float, curvature: float) -> float:
    return base + curvature * max(0.0, load - knee) ** 2


KNOBS = (Knob("base", 10.0, 20.0, 21), Knob("knee", 0.0, 1.0, 21), Knob("curvature", 0.0, 20.0, 21))


def fit_curve(bins: list[tuple[float, float, int]], knobs: tuple[Knob, ...] = KNOBS,
              refinements: int = 2) -> dict:
    """Grid search over the three knobs, re-gridded around the winner, scored by bin MAE.

    Chapter 35's grid_fit runs a document through time; this curve has no time in it, so the
    same grid, the same refinement rule, and the same error function are applied directly.
    """
    loads = [b[0] for b in bins]
    observed = [b[1] for b in bins]
    if 3 * len(knobs) > len(bins):
        raise ValueError(f"{len(knobs)} knobs against {len(bins)} bins: too few bins")
    current = list(knobs)
    best: tuple[float, dict[str, float]] = (float("inf"), {})
    evaluations = 0
    for _ in range(refinements + 1):
        for base in current[0].grid():
            for knee in current[1].grid():
                for curvature in current[2].grid():
                    model = [curve(x, base, knee, curvature) for x in loads]
                    err = mae(model, observed)
                    evaluations += 1
                    if err < best[0]:
                        best = (err, {"base": base, "knee": knee, "curvature": curvature})
        current = [
            Knob(k.variable,
                 max(k.low, best[1][k.variable] - (k.high - k.low) / (k.steps - 1)),
                 min(k.high, best[1][k.variable] + (k.high - k.low) / (k.steps - 1)),
                 k.steps)
            for k in current
        ]
    return {"fitted": best[1], "error": best[0], "evaluations": evaluations,
            "method": f"grid search, {len(knobs)} knobs, {refinements} refinements",
            "searched": {k.variable: (k.low, k.high) for k in knobs}, "evidence": "inferred"}


def fitted_congestion_lookup(hour_rows: list[dict] | None = None
                             ) -> tuple[tuple[float, float], ...]:
    """The exported artifact: the fitted curve sampled on the fit-year bin centers.

    The domain is the first bin center to the last, so a load the record never reached is a load
    the lookup refuses. Values are `inferred` wherever they are carried.
    """
    hour_rows = hour_rows if hour_rows is not None else read_hour_bins()
    bins = pooled_bins(rows_for_year(hour_rows, FIT_YEAR))
    fit = fit_curve(bins)
    f = fit["fitted"]
    return tuple((b[0], round(curve(b[0], f["base"], f["knee"], f["curvature"]), 3))
                 for b in bins)


def lookup_note(fit: dict, bins: list[tuple[float, float, int]], path: Path = HOURS) -> str:
    check = checksum_of(path)[:12] if path.exists() else "unknown"
    f = fit["fitted"]
    return (f"inferred: convex curve {f['base']:.3g} + {f['curvature']:.3g} * "
            f"max(0, load - {f['knee']:.3g})^2 fitted to {len(bins)} load bins of {SOURCE} by "
            f"{fit['method']}; bin MAE {fit['error']:.3g} minute; data sha256 {check}; "
            f"consistent with a congestion structure, not evidence for one")


def holdout_error(points: tuple[tuple[float, float], ...], holdout_rows: list[dict]) -> dict:
    """The fitted lookup against the other year's bins. Loads outside the domain are refused."""
    lookup = Lookup(list(points), name="congestion_delay")
    bins = pooled_bins(holdout_rows)
    inside = [b for b in bins if lookup.domain[0] <= b[0] <= lookup.domain[1]]
    refused = [b for b in bins if not lookup.domain[0] <= b[0] <= lookup.domain[1]]
    error = mae([lookup(x) for x, _, _ in inside], [y for _, y, _ in inside]) if inside else None
    return {"mae": error, "bins_inside": len(inside), "bins_refused": len(refused),
            "refused_loads": tuple(x for x, _, _ in refused),
            "flights_refused": sum(n for _, _, n in refused), "bins": bins}


def convex_above_knee(points: tuple[tuple[float, float], ...], knee: float) -> bool:
    """Non-decreasing everywhere, and second differences non-negative from the knee upward."""
    ys = [y for _, y in points]
    if any(b < a - 1e-9 for a, b in zip(ys, ys[1:])):
        return False
    above = [(x, y) for x, y in points if x >= knee - 1e-9]
    seconds = [above[i + 1][1] - 2 * above[i][1] + above[i - 1][1]
               for i in range(1, len(above) - 1)]
    return all(s >= -1e-9 for s in seconds)


# ---------------------------------------------------------------- the rest of the record


def cancellation_fit(month_rows: list[dict]) -> tuple[float, float]:
    """Departure-weighted least squares of cancellation share on mean delay: (base, slope)."""
    w = [r["scheduled_departures"] for r in month_rows]
    xs = [r["mean_dep_delay_minutes"] for r in month_rows]
    ys = [r["cancellation_share"] for r in month_rows]
    total = sum(w)
    mx = sum(wi * x for wi, x in zip(w, xs)) / total
    my = sum(wi * y for wi, y in zip(w, ys)) / total
    sxx = sum(wi * (x - mx) ** 2 for wi, x in zip(w, xs))
    slope = sum(wi * (x - mx) * (y - my) for wi, x, y in zip(w, xs, ys)) / sxx if sxx else 0.0
    return my - slope * mx, slope


def _days_in(period: str) -> int:
    year, month = int(period[:4]), int(period[5:7])
    return (31, 29 if year % 4 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)[month - 1]


def observed_summary(month_rows: list[dict]) -> dict:
    """Departure-weighted facts from the airport-month file the model is anchored to."""
    departures = sum(r["scheduled_departures"] for r in month_rows)
    loads = sorted(r["load"] for r in month_rows)
    airports = sorted({r["airport"] for r in month_rows})
    p95 = {r["airport"]: r["p95_hourly_departures"] for r in month_rows}
    p90 = {r["airport"]: r["p90_hourly_departures"] for r in month_rows}
    return {
        "airports": len(airports),
        "rows": len(month_rows),
        "scheduled_departures": departures,
        "departures_per_day": departures / sum(_days_in(r["period"]) for r in month_rows),
        "mean_delay": sum(r["mean_dep_delay_minutes"] * r["scheduled_departures"]
                          for r in month_rows) / departures,
        "mean_taxi_out": sum(r["mean_taxi_out"] * r["scheduled_departures"]
                             for r in month_rows) / departures,
        "cancellation_share": sum(r["cancellation_share"] * r["scheduled_departures"]
                                  for r in month_rows) / departures,
        "mean_load": statistics.fmean(r["load"] for r in month_rows),
        "load_p10": loads[int(0.10 * (len(loads) - 1))],
        "load_p90": loads[int(0.90 * (len(loads) - 1))],
        "load_min": loads[0],
        "load_max": loads[-1],
        "peak_hour_capacity": statistics.fmean(p95[a] for a in airports),
        "retained_p90": 1 - sum(r["departures_above_p90"] for r in month_rows) / departures,
        "retained_p95": 1 - sum(r["departures_above_p95"] for r in month_rows) / departures,
        "cap_load_p90": statistics.fmean(p90[a] / p95[a] for a in airports),
        "cap_load_p95": 1.0,
    }


def month_load_correlation(month_rows: list[dict]) -> float:
    """Correlation of monthly mean departure delay with monthly load, across airport-months."""
    xs = [r["load"] for r in month_rows]
    ys = [r["mean_dep_delay_minutes"] for r in month_rows]
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    return sxy / (sxx * syy) ** 0.5


def clock_profile(clock_rows: list[dict], min_flights: int = MIN_BIN_FLIGHTS
                  ) -> list[tuple[int, float, float, int]]:
    """(hour, mean departure delay, mean taxi-out, flights) pooled across airports."""
    groups: dict[int, list[float]] = {}
    for row in clock_rows:
        total = groups.setdefault(row["hour"], [0.0, 0.0, 0.0])
        total[0] += row["mean_dep_delay_minutes"] * row["flights"]
        total[1] += row["mean_taxi_out"] * row["flights"]
        total[2] += row["flights"]
    return [(h, d / n, t / n, int(n)) for h, (d, t, n) in sorted(groups.items())
            if n >= min_flights]


# ---------------------------------------------------------------- assembling the case


def fitted_document(month_rows: list[dict] | None = None, hour_rows: list[dict] | None = None,
                    **overrides) -> ModelDocument:
    """The airport document with the fitted lookup, cancellation slope, and observed anchors."""
    month_rows = month_rows if month_rows is not None else read_months()
    hour_rows = hour_rows if hour_rows is not None else read_hour_bins()
    fit_months = rows_for_year(month_rows, FIT_YEAR)
    bins = pooled_bins(rows_for_year(hour_rows, FIT_YEAR))
    fit = fit_curve(bins)
    points = fitted_congestion_lookup(hour_rows)
    facts = observed_summary(fit_months)
    _, slope = cancellation_fit(fit_months)
    f = fit["fitted"]
    record_queue = curve(facts["mean_load"], f["base"], f["knee"], f["curvature"]) - bins[0][1]
    settings = dict(scheduled_load=round(facts["mean_load"], 4),
                    departures_per_day=round(facts["departures_per_day"], 2),
                    cancel_at_record=round(facts["cancellation_share"], 5),
                    cancel_per_minute=round(slope, 6),
                    record_queue_delay=round(record_queue, 3),
                    representative_peak_departures=round(facts["peak_hour_capacity"], 2),
                    baseline_taxi_out=round(bins[0][1], 3),
                    lookup_note=lookup_note(fit, bins))
    settings.update(overrides)
    return build_document(points, **settings)


def policies(facts: dict) -> list[Policy]:
    return [
        Policy("no_cap", {"load_cap": 10.0, "movements_retained": 1.0}, owner="airport operator",
               reversible=True, note="schedule as filed"),
        Policy("cap_at_p95", {"load_cap": facts["cap_load_p95"],
                              "movements_retained": round(facts["retained_p95"], 5)},
               owner="airport operator", reversible=True,
               note="no clock hour above the fit-year p95 hourly count"),
        Policy("cap_at_p90", {"load_cap": round(facts["cap_load_p90"], 4),
                              "movements_retained": round(facts["retained_p90"], 5)},
               owner="airport operator", reversible=True,
               note="no clock hour above the fit-year p90 hourly count"),
    ]


def uncertainties(facts: dict, points: tuple[tuple[float, float], ...]) -> list[Uncertainty]:
    """Ranges somebody will defend, kept inside the lookup's domain so every draw can run."""
    low = max(facts["load_p10"], points[0][0])
    high = min(facts["load_p90"], points[-1][0])
    return [
        Uncertainty("scheduled_load", low, high, cost_to_reduce=1.0),
        Uncertainty("queue_clear_time", 1.0, 4.0, cost_to_reduce=3.0),
        Uncertainty("padding_adjustment_time", 30.0, 180.0, cost_to_reduce=5.0),
    ]


def bounds(facts: dict) -> list[Bound]:
    return [Bound("cancellation_share", high=round(facts["cancellation_share"], 5),
                  reason="no worse than the fit-year record"),
            Bound("movements_retained", low=0.92,
                  reason="the operator will not drop more than eight percent of movements")]


def policy_table(document: ModelDocument, facts: dict, points: tuple[tuple[float, float], ...],
                 draws: int = 40, seed: int = 7) -> dict[str, dict]:
    """Every policy on delay, cancellations, and movements, with the bounds that can veto."""
    us = uncertainties(facts, points)
    out: dict[str, dict] = {}
    for objective in ("realized_delay", "cancellation_share", "movements_retained",
                      "movements_lost_share"):
        for ev in compare(document, policies(facts), us, objective, bounds(facts), draws, seed):
            entry = out.setdefault(ev.policy, {"violations": []})
            entry[objective] = {"mean": ev.mean(), "worst": ev.worst(),
                                "best": max(ev.values) if ev.values else None}
            entry["violations"].extend(ev.violations)
    return out


def critic_report(document: ModelDocument) -> dict[str, list[str]]:
    findings = (structural_findings(document) + dimensional_findings(document)
                + conservation_findings(document)
                + extreme_condition_findings(document, "queue")
                + extreme_condition_findings(document, "padding"))
    return defect_report(findings)


def padding_run(document: ModelDocument, days: int = 365) -> dict[str, float]:
    """One year at the document's own load: how much of the realized delay padding hides."""
    result = Runtime(document, RunSettings("euler", 1.0, float(days))).run()
    return {"realized_delay": result.final("realized_delay"),
            "padding": result.final("padding"),
            "reported_delay": result.final("reported_delay"),
            "padding_at_90": result.series["padding"][90]}


def run_case(month_rows: list[dict] | None = None, hour_rows: list[dict] | None = None,
             clock_rows: list[dict] | None = None) -> dict:
    """Everything the chapter prints, in one dict, from the committed record."""
    month_rows = month_rows if month_rows is not None else read_months()
    hour_rows = hour_rows if hour_rows is not None else read_hour_bins()
    clock_rows = clock_rows if clock_rows is not None else read_clock_hours()
    fit_months = rows_for_year(month_rows, FIT_YEAR)
    fit_hours = rows_for_year(hour_rows, FIT_YEAR)
    hold_hours = rows_for_year(hour_rows, HOLDOUT_YEAR)
    bins = pooled_bins(fit_hours)
    fit = fit_curve(bins)
    points = fitted_congestion_lookup(hour_rows)
    facts = observed_summary(fit_months)
    document = fitted_document(month_rows, hour_rows)
    return {
        "facts": facts,
        "holdout_facts": observed_summary(rows_for_year(month_rows, HOLDOUT_YEAR)),
        "bins": bins,
        "delay_bins": pooled_bins(fit_hours, "mean_dep_delay_minutes"),
        "clock": clock_profile(rows_for_year(clock_rows, FIT_YEAR)),
        "month_correlation": month_load_correlation(fit_months),
        "fit": fit,
        "points": points,
        "convex": convex_above_knee(points, fit["fitted"]["knee"]),
        "holdout": holdout_error(points, hold_hours),
        "cancellation": cancellation_fit(fit_months),
        "policies": policy_table(document, facts, points),
        "critic": critic_report(document),
        "padding": padding_run(document),
        "document_hash": document.hash(),
    }


def as_variable(points: tuple[tuple[float, float], ...], note: str) -> Variable:
    """The lookup as a document variable, so a reader can see how it is carried."""
    return Variable("congestion_delay", "lookup", "minute/departure", equation="effective_load",
                    points=points, evidence="inferred", note=note)


if __name__ == "__main__":
    import json
    print(json.dumps(run_case(), indent=1, default=str))
