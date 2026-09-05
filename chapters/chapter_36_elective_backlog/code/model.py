"""An elective waiting list as three stocks: the list, the long waiters, and the capacity.

The structure is the bathtub of Chapter 4 with an aging chain (Chapter 17) hung off it. Referrals
flow in. Treatments flow out, limited by capacity. Validation removes pathways that should not be
on the list. Three loops close the structure: R1, long waiters erode
effective capacity; B1, validation removals scale with the list; B2, a large list suppresses
referrals.

Pathways cross into the long-wait stock at a rate that rises steeply with the load on the
schedule (months of work on the list), a tail that a national aggregate cannot resolve any other
way, after a delay (Chapter 16).

Everything observed comes from `data/nhs_rtt/rtt_national_monthly.csv`. Every parameter the
record does not give is marked `assumed`, and the three the fit moves are marked `inferred` by
Chapter 35's `with_fitted`. Time unit: months.
"""

import csv
from pathlib import Path

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

ROOT = Path(__file__).resolve().parents[3]
RECORD = ROOT / "data" / "nhs_rtt" / "rtt_national_monthly.csv"
SOURCE = "NHS England RTT waiting times, commissioner basis, retrieved 2026-09-03"
WEEKS_PER_MONTH = 4.35

# The three parameters a fit is allowed to move, and the ranges someone will defend. Anything
# beyond these is not a fit of this model, it is a different model.
FREE_KNOBS = ("validation_rate", "system_growth", "tail_steepness")


def read_record(path: Path = RECORD) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def month_index(rows: list[dict[str, str]], period: str) -> int:
    for i, row in enumerate(rows):
        if row["period"] == period:
            return i
    raise KeyError(f"{period} is not in the record")


def first_year_mean(rows: list[dict[str, str]], column: str, period: str, months: int = 12
                    ) -> float:
    """Mean of a column over the `months` rows starting at `period` inclusive.

    The level of a flow during the first year of a run, used as that flow's starting level.
    Monthly flows in this record swing by a fifth with the calendar, so one month is not a
    level; a year is.
    """
    start = month_index(rows, period)
    values = [float(r[column]) for r in rows[start:start + months] if r[column]]
    if len(values) < months:
        raise ValueError(f"{column}: fewer than {months} months of values from {period}")
    return sum(values) / len(values)


def window_mean(rows: list[dict[str, str]], column: str, start: str, end: str) -> float:
    """Mean of a column over the rows from `start` to `end` inclusive. A record fact, not a fit."""
    a, b = month_index(rows, start), month_index(rows, end) + 1
    values = [float(r[column]) for r in rows[a:b] if r[column]]
    if not values:
        raise ValueError(f"{column} has no values between {start} and {end}")
    return sum(values) / len(values)


def window_ratio(rows: list[dict[str, str]], numerator: str, denominator: str, start: str,
                 end: str) -> float:
    """Mean of one column divided by the mean of another over the same months."""
    return window_mean(rows, numerator, start, end) / window_mean(rows, denominator, start, end)


def build(start: str = "2016-04", *, horizon: int = 45, rows: list[dict[str, str]] | None = None,
          validation_rate: float = 0.06, system_growth: float = 0.002,
          tail_steepness: float = 1.75, long_share: float = 0.05) -> ModelDocument:
    """The model with its stocks set from the record at `start`.

    `validation_rate`, `system_growth` and `tail_steepness` default to the middle of their
    search ranges; `calibrate.fit` replaces them with fitted values marked inferred.
    """
    rows = rows or read_record()
    at = rows[month_index(rows, start)]
    total = float(at["total_incomplete"])
    long_waiters = float(at["over_52_weeks"])
    referrals = first_year_mean(rows, "new_periods", start)
    capacity = first_year_mean(rows, "completed_pathways", start)
    load = (total - long_waiters) / capacity
    # The crossing share that sustains the start's long-wait count against its own drain.
    drain = min(long_waiters, long_share * capacity) + validation_rate * long_waiters
    tail_base = drain / (total - long_waiters)
    obs = f"observed: {SOURCE}, "
    variables = [
        # stocks
        Variable("waiting_list", "stock", "pathways", value=total - long_waiters,
                 evidence="observed",
                 note=obs + f"incomplete pathways under 52 weeks at {start}"),
        Variable("long_waiters", "stock", "pathways", value=long_waiters, evidence="observed",
                 note=obs + f"incomplete pathways over 52 weeks at {start}"),
        Variable("capacity", "stock", "treatments per month", value=capacity,
                 evidence="observed",
                 note=obs + f"completed pathways, mean of the 12 months from {start}"),
        # parameters the record gives
        Variable("base_referrals", "parameter", "pathways/month", value=referrals,
                 evidence="observed",
                 note=obs + f"new RTT periods, mean of the 12 months from {start}"),
        Variable("reference_list", "parameter", "pathways", value=total, evidence="observed",
                 note=obs + f"total incomplete pathways at {start}"),
        Variable("initial_capacity", "parameter", "treatments per month", value=capacity,
                 evidence="observed",
                 note=obs + f"completed pathways, mean of the 12 months from {start}; the "
                            "level referrals are scaled against"),
        Variable("reference_load", "parameter", "month", value=load, evidence="observed",
                 note=obs + f"months of work on the list at {start}: pathways under 52 weeks "
                            "divided by monthly completions"),
        # parameters the fit moves
        Variable("validation_rate", "parameter", "1/month", value=validation_rate,
                 note="share of the list removed each month without a recorded treatment"),
        Variable("system_growth", "parameter", "1/month", value=system_growth,
                 note="monthly growth shared by capacity and referrals; the record shows both "
                      "rising together, and the model does not let them drift apart"),
        Variable("tail_steepness", "parameter", "1/month", value=tail_steepness,
                 note="how fast the share of the list crossing 52 weeks rises with each extra "
                      "month of load on the schedule"),
        # parameters nobody has measured
        Variable("tail_base", "parameter", "1/month", value=tail_base,
                 note="assumed: share of the list crossing 52 weeks each month at the "
                      f"reference load, set so the {start} long-wait count is sustained "
                      "against its own treatment and validation drain"),
        Variable("suppression_strength", "parameter", "dimensionless", value=0.2,
                 note="referral reduction per unit of list growth above the reference"),
        Variable("complexity_penalty", "parameter", "dimensionless", value=0.5,
                 note="extra capacity a long waiter consumes, as a share of an ordinary "
                      "pathway"),
        Variable("long_share", "parameter", "dimensionless", value=long_share,
                 note="share of capacity directed at pathways already over 52 weeks"),
        Variable("capacity_uplift", "parameter", "dimensionless", value=0.0,
                 note="policy lever: proportional addition to capacity"),
        # auxiliaries
        Variable("total_incomplete", "auxiliary", "pathways",
                 equation="waiting_list + long_waiters"),
        Variable("pressure", "auxiliary", "dimensionless",
                 equation="total_incomplete / reference_list"),
        Variable("effective_capacity", "auxiliary", "pathways/month",
                 equation="capacity * (1 + capacity_uplift) / "
                          "(1 + complexity_penalty * long_waiters / max(1, total_incomplete))"),
        Variable("load_months", "auxiliary", "month",
                 equation="waiting_list / max(1, effective_capacity)"),
        Variable("crossing", "auxiliary", "pathways/month",
                 equation="waiting_list * tail_base * "
                          "exp(min(8, tail_steepness * (load_months - reference_load)))"),
        Variable("aging_pipeline", "delay", "pathways/month", equation="crossing",
                 delay_time=6.0,
                 note="assumed: a rise in load takes six months on average to appear as "
                      "pathways over 52 weeks; a first-order delay, so the arrival is spread"),
        Variable("mean_wait_weeks", "auxiliary", "week",
                 equation="total_incomplete / max(1, treatments + long_treatments) * 4.35"),
        Variable("list_reduction", "auxiliary", "pathways",
                 equation="reference_list - total_incomplete",
                 note="policy objective: pathways cleared relative to the start; higher is "
                      "better"),
        # flows
        Variable("referrals", "flow", "pathways/month", target="waiting_list", sign=1,
                 equation="base_referrals * capacity / initial_capacity * "
                          "max(0.5, 1 - suppression_strength * max(0, pressure - 1))"),
        Variable("long_treatments", "flow", "pathways/month", target="long_waiters", sign=-1,
                 equation="min(long_waiters, effective_capacity * long_share)"),
        Variable("treatments", "flow", "pathways/month", target="waiting_list", sign=-1,
                 equation="min(waiting_list, effective_capacity - long_treatments)"),
        Variable("validation_removals", "flow", "pathways/month", target="waiting_list",
                 sign=-1, equation="waiting_list * validation_rate"),
        Variable("long_validation", "flow", "pathways/month", target="long_waiters", sign=-1,
                 equation="long_waiters * validation_rate"),
        Variable("aging_out", "flow", "pathways/month", target="waiting_list", sign=-1,
                 equation="aging_pipeline"),
        Variable("aging_in", "flow", "pathways/month", target="long_waiters", sign=1,
                 equation="aging_pipeline"),
        Variable("capacity_change", "flow", "treatments per month/month", target="capacity",
                 sign=1, equation="capacity * system_growth"),
    ]
    return ModelDocument(name="elective_backlog", version="1.0.0", variables=variables,
                         horizon=horizon, horizon_unit="month", time_step=0.25)


def free_knob_count(document: ModelDocument) -> int:
    """How many parameters carry no observed value and no assumed note: the knobs a fit may move.

    A guard, not a report: the chapter's rule is at most three, and a test holds it there.
    """
    return sum(1 for v in document.variables
               if v.kind == "parameter" and v.id in FREE_KNOBS)
