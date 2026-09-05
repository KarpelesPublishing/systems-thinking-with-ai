"""A congested airport as a document: a queue that is a level, a delay curve, and padding.

Time unit: days. Each day carries one representative peak-hour exposure at `scheduled_load`
(peak-hour departures over the airport's p95 hourly count). The fitted curve says how long taxi-out
takes at that load, and the minutes above the lowest-load-bin baseline are the modeled delay that
day's representative departures generate. The queue of delay minutes fills at that rate and drains
over `queue_clear_time`. Schedule
padding is a second level: it rises toward the realized delay over `padding_adjustment_time`
and falls back when delay falls. The delay a schedule reports is realized delay minus padding,
which is how a balancing loop hides the signal it responds to.

Three free parameters beyond the fitted lookup: `queue_clear_time`, `padding_adjustment_time`,
`cancel_per_minute`. The lookup itself is the fitted curve from calibrate.py, carried as a
`lookup` variable with evidence `inferred`, and the runtime refuses any load outside its points.
"""

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

HORIZON_DAYS = 365
LOOKUP_ID = "congestion_delay"


def build_document(
    lookup_points: tuple[tuple[float, float], ...],
    scheduled_load: float,
    departures_per_day: float,
    cancel_at_record: float,
    cancel_per_minute: float,
    record_queue_delay: float,
    representative_peak_departures: float,
    baseline_taxi_out: float,
    lookup_note: str = "",
    queue_clear_time: float = 2.0,
    padding_adjustment_time: float = 90.0,
    load_cap: float = 10.0,
    movements_retained: float = 1.0,
) -> ModelDocument:
    """The airport model with the fitted curve in place and every value labeled."""
    variables = [
        Variable("scheduled_load", "parameter", "dimensionless", value=scheduled_load,
                 evidence="observed",
                 note="peak-hour departures over the airport's fit-year p95 hourly departures; "
                      "the driver, set from the record or stressed by an experiment"),
        Variable("load_cap", "parameter", "dimensionless", value=load_cap, evidence="assumed",
                 note="policy: the highest load a schedule cap allows; 10 means no cap"),
        Variable("movements_retained", "parameter", "dimensionless", value=movements_retained,
                 evidence="observed",
                 note="policy: share of scheduled departures that survive the cap, from the "
                      "record's departures above the p90 or p95 hourly count"),
        Variable("departures_per_day", "parameter", "departure/day", value=departures_per_day,
                 evidence="observed", note="mean scheduled departures per airport-day, fit year"),
        Variable("representative_peak_departures", "parameter", "departure/day",
                 value=representative_peak_departures, evidence="assumed",
                 note="one daily representative peak-hour exposure, scaled from the observed "
                      "mean fit-year p95 hourly departures across the thirty airports"),
        Variable("baseline_taxi_out", "parameter", "minute/departure", value=baseline_taxi_out,
                 evidence="inferred",
                 note="mean taxi-out in the lowest load bin of the fit year; not a measurement "
                      "of zero queueing"),
        Variable("queue_clear_time", "parameter", "day", value=queue_clear_time,
                 evidence="assumed", note="days for the delay backlog to drain; free knob 1"),
        Variable("padding_adjustment_time", "parameter", "day", value=padding_adjustment_time,
                 evidence="assumed",
                 note="days over which schedules absorb realized delay; free knob 2"),
        Variable("cancel_at_record", "parameter", "dimensionless", value=cancel_at_record,
                 evidence="observed", note="fit-year departure-weighted cancellation share"),
        Variable("record_queue_delay", "parameter", "minute/departure",
                 value=record_queue_delay, evidence="inferred",
                 note="queue delay the fitted curve gives at the record's mean load; the "
                      "anchor at which modelled cancellations equal the record"),
        Variable("cancel_per_minute", "parameter", "1/minute", value=cancel_per_minute,
                 evidence="inferred",
                 note="cancellation share per minute of realized delay, fitted; free knob 3"),
        Variable("effective_load", "auxiliary", "dimensionless",
                 equation="min(scheduled_load, load_cap)"),
        Variable("peak_departures", "auxiliary", "departure/day",
                 equation="representative_peak_departures * effective_load * movements_retained"),
        Variable(LOOKUP_ID, "lookup", "minute/departure", equation="effective_load",
                 points=lookup_points, evidence="inferred", note=lookup_note),
        Variable("queue_delay_per_departure", "auxiliary", "minute/departure",
                 equation="max(0, congestion_delay - baseline_taxi_out)"),
        Variable("queue", "stock", "minute", value=0.0, evidence="assumed",
                 note="delay minutes generated and not yet absorbed; a queue is a level"),
        Variable("delay_generated", "flow", "minute/day", target="queue", sign=1,
                 equation="peak_departures * queue_delay_per_departure"),
        Variable("delay_cleared", "flow", "minute/day", target="queue", sign=-1,
                 equation="queue / queue_clear_time"),
        Variable("realized_delay", "auxiliary", "minute/departure",
                 equation="delay_cleared / max(peak_departures, 1)"),
        Variable("padding", "stock", "minute", value=0.0, evidence="assumed",
                 note="minutes of schedule buffer per departure"),
        Variable("padding_added", "flow", "minute/day", target="padding", sign=1,
                 equation="max(0, realized_delay - padding) / padding_adjustment_time"),
        Variable("padding_removed", "flow", "minute/day", target="padding", sign=-1,
                 equation="max(0, padding - realized_delay) / padding_adjustment_time"),
        Variable("reported_delay", "auxiliary", "minute/departure",
                 equation="max(0, realized_delay - padding)"),
        Variable("cancellation_share", "auxiliary", "dimensionless",
                 equation="min(1, max(0, cancel_at_record + cancel_per_minute * "
                          "(realized_delay - record_queue_delay)))"),
        Variable("movements", "auxiliary", "departure/day",
                 equation="departures_per_day * movements_retained * (1 - cancellation_share)"),
        Variable("movements_lost_share", "auxiliary", "dimensionless",
                 equation="1 - movements / departures_per_day"),
    ]
    return ModelDocument(name="congestion_curve", version="1.0.0", variables=variables,
                         horizon=HORIZON_DAYS, horizon_unit="day", time_step=1.0)


def free_knobs() -> tuple[str, ...]:
    """The parameters nobody measured. Three, by design."""
    return ("queue_clear_time", "padding_adjustment_time", "cancel_per_minute")
