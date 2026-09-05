"""An industry that builds capacity when margins are good, as a model document.

One stock, capacity, measured in units of monthly output the industry's plants could produce.
Demand is a constant, held fixed on purpose: Chapter 2 asked whether a factory could make its own
crisis with incoming orders held constant, and this document is that test at the scale of a
sector. If utilization still swings with nothing outside the loop moving, the loop is sufficient
to produce a swing. Whether it produced the recorded one is a separate question the fit cannot
answer.

The loop: utilization sets the margin through a saturating lookup; the margin is perceived through
an information delay (kind delay); investment above replacement responds to the perceived margin;
new capacity arrives through a construction delay (a material delay, kind delay); capacity retires
at a fixed lifetime. Every quantity is in months.

Reporting counters track elapsed time, deviation from normal, and utilization itself. Derived
outputs include steadiness and mean utilization; an alias supports the fit's separate targets.
These reporting branches never feed back into the dynamics.
Chapter 30's comparison reads one final value per run, so a swing has to be accumulated inside
the model to be compared at all.
"""

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime

NORMAL_UTILIZATION = 78.0     # percent; the lookup's normal point, near the 1990 to 2019 mean
DEFAULT_CONSTRUCTION_DELAY = 24.0   # months, assumed; the fit loops over it
DEFAULT_PERCEPTION_DELAY = 6.0      # months, assumed
DEFAULT_CAPITAL_LIFETIME = 180.0    # months, assumed
DEFAULT_INVESTMENT_GAIN = 0.15      # per month per unit of excess margin, before fitting
DEFAULT_MARGIN_SENSITIVITY = 1.0    # dimensionless, before fitting

# Utilization (percent) to margin relative to normal. Assumed shape: flat and poor below sixty
# percent, rising through normal, saturating above ninety. Chapter 15's rule applies: the points
# are a hypothesis about a shape, and the fit moves only its steepness through margin_sensitivity.
MARGIN_POINTS = ((0.0, 0.0), (60.0, 0.30), (70.0, 0.60), (78.0, 1.00), (85.0, 1.50),
                 (92.0, 1.90), (100.0, 2.10), (120.0, 2.20))


def document(construction_delay: float = DEFAULT_CONSTRUCTION_DELAY,
             perception_delay: float = DEFAULT_PERCEPTION_DELAY,
             investment_gain: float = DEFAULT_INVESTMENT_GAIN,
             margin_sensitivity: float = DEFAULT_MARGIN_SENSITIVITY,
             capital_lifetime: float = DEFAULT_CAPITAL_LIFETIME,
             demand: float = 80.0, horizon: int = 360) -> ModelDocument:
    """The capacity-cycle document. Delay times are fixed per document; parameters can be fitted."""
    if construction_delay <= 0 or perception_delay <= 0:
        raise ValueError("delays must be positive")
    initial_capacity = 100.0
    return ModelDocument(
        name="capacity_cycle", version="1.0.0", horizon=horizon, horizon_unit="month",
        time_step=1.0,
        variables=[
            Variable("capacity", "stock", "units", value=initial_capacity, evidence="assumed",
                     note="index; the record's capacity index is 74.9 in 1990-01, scale is free"),
            Variable("demand", "parameter", "units/month", value=demand, evidence="assumed",
                     note="held constant: the Chapter 2 test, orders fixed, does the loop swing"),
            Variable("production", "auxiliary", "units/month", equation="min(demand, capacity)"),
            Variable("utilization", "auxiliary", "percent",
                     equation="100 * production / max(capacity, 1)"),
            Variable("utilization_level", "auxiliary", "percent", equation="utilization",
                     note="alias so the fit can score amplitude and period as two targets"),
            Variable("normal_utilization", "parameter", "percent", value=NORMAL_UTILIZATION,
                     evidence="assumed",
                     note="lookup normal point; record mean 1990 to 2019 is 77.5"),
            Variable("margin_shape", "lookup", "dimensionless",
                     equation="min(max(utilization, 0), 120)", points=MARGIN_POINTS,
                     evidence="assumed",
                     note="saturating; steepness fitted via margin_sensitivity"),
            Variable("margin_sensitivity", "parameter", "dimensionless", value=margin_sensitivity,
                     evidence="assumed", note="scales the lookup's departure from normal"),
            Variable("margin", "auxiliary", "dimensionless",
                     equation="1 + margin_sensitivity * (margin_shape - 1)"),
            Variable("perceived_margin", "delay", "dimensionless", equation="margin",
                     delay_time=perception_delay, value=1.0, evidence="assumed",
                     note="information delay: reported margins lag realized ones"),
            Variable("investment_gain", "parameter", "1/month", value=investment_gain,
                     evidence="assumed", note="capacity growth per month per unit excess margin"),
            Variable("capital_lifetime", "parameter", "month", value=capital_lifetime,
                     evidence="assumed", note="fifteen years; retirement is capacity over this"),
            Variable("margin_dead_band", "parameter", "dimensionless", value=0.0,
                     evidence="assumed", note="policy: margins within the band trigger nothing"),
            Variable("rule_gain_utilization", "parameter", "1/month", value=0.0,
                     evidence="assumed", note="policy: response to current utilization gap"),
            Variable("trigger_utilization", "parameter", "percent", value=NORMAL_UTILIZATION,
                     evidence="assumed", note="policy: utilization the trigger rule aims at"),
            Variable("excess_margin", "auxiliary", "dimensionless",
                     equation="max(0, perceived_margin - 1 - margin_dead_band)"
                              " - max(0, 1 - margin_dead_band - perceived_margin)"),
            Variable("utilization_gap", "auxiliary", "dimensionless",
                     equation="(utilization - trigger_utilization) / 100"),
            Variable("desired_investment", "auxiliary", "units/month",
                     equation="max(0, capacity * (1 / capital_lifetime"
                              " + investment_gain * excess_margin"
                              " + rule_gain_utilization * utilization_gap))"),
            Variable("completions", "delay", "units/month", equation="desired_investment",
                     delay_time=construction_delay, value=initial_capacity / capital_lifetime,
                     evidence="assumed", note="material delay: plants ordered now open later"),
            Variable("building", "flow", "units/month", equation="completions",
                     target="capacity", sign=1),
            Variable("retirement", "flow", "units/month", equation="capacity / capital_lifetime",
                     target="capacity", sign=-1),
            # Accumulators for the policy comparison. None feeds back.
            Variable("elapsed", "stock", "month", value=0.0, evidence="assumed", note="clock"),
            Variable("ticking", "flow", "month/month", equation="1", target="elapsed", sign=1),
            Variable("cumulative_deviation", "stock", "point_months", value=0.0,
                     evidence="assumed", note="running sum of |utilization minus normal|"),
            Variable("deviating", "flow", "point_months/month",
                     equation="abs(utilization - normal_utilization)",
                     target="cumulative_deviation", sign=1),
            Variable("swing", "auxiliary", "percent",
                     equation="cumulative_deviation / max(elapsed, 1)",
                     note="mean absolute distance of utilization from normal, so far"),
            Variable("steadiness", "auxiliary", "percent", equation="100 - swing",
                     note="policy objective: higher is a flatter utilization path"),
            Variable("mean_utilization", "auxiliary", "percent",
                     equation="cumulative_utilization / max(elapsed, 1)"),
            Variable("cumulative_utilization", "stock", "point_months", value=0.0,
                     evidence="assumed", note="running sum of utilization"),
            Variable("accumulating_utilization", "flow", "point_months/month",
                     equation="utilization", target="cumulative_utilization", sign=1),
        ],
    )


def utilization_path(doc: ModelDocument, months: int | None = None, dt: float = 1.0,
                     solver: str = "euler") -> list[float]:
    """Utilization sampled once a month from a run of the document."""
    horizon = float(months if months is not None else doc.horizon)
    result = Runtime(doc, RunSettings(solver=solver, dt=dt, horizon=horizon)).run()
    stride = int(round(1.0 / dt))
    return result.series["utilization"][::stride]
