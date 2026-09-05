"""A support desk whose effectiveness saturates with load.

Chapter 15's lookup carried in the document, Chapter 12's accounting for the
queue, and Chapter 13's rule for the intake. The shape is evidenced between
load 0 and 3; outside that the lookup refuses rather than extrapolating.
"""

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

# Observed at four load levels. Beyond 3.0 nobody measured, so the model stops.
OBSERVED_EFFECTIVENESS = ((0.0, 1.0), (1.0, 0.92), (2.0, 0.70), (3.0, 0.45))

# The same curve carried past the evidence on purpose, so an overloaded desk can be
# run at all. The extra points are a judgement, not a measurement, and the variable
# that uses them says so. Compare the two runs before believing either.
ASSUMED_EFFECTIVENESS = OBSERVED_EFFECTIVENESS + ((5.0, 0.28), (10.0, 0.15))


def support_desk(arrivals: float = 22.0, staff: float = 10.0,
                 past_the_evidence: bool = False) -> ModelDocument:
    """Open tickets, served by a desk that slows down as its queue grows.

    With past_the_evidence the curve is extended by judgement and the variable is
    marked assumed, which is the only honest way to run a load the desk has never
    been measured at.
    """
    shape = ASSUMED_EFFECTIVENESS if past_the_evidence else OBSERVED_EFFECTIVENESS
    level = "assumed" if past_the_evidence else "observed"
    return ModelDocument("support_desk", "1.0.0", horizon=40, horizon_unit="week", variables=[
        Variable("open_tickets", "stock", "tickets", value=15.0,
                 evidence="observed", note="ticket system, 2026-08-01"),
        Variable("staff", "parameter", "people", value=staff, evidence="observed",
                 note="rota, 2026-08-01"),
        Variable("per_head", "parameter", "tickets/person/week", value=2.5, evidence="inferred",
                 note="from the last quarter of closures"),
        Variable("arrivals", "parameter", "tickets/week", value=arrivals, evidence="observed",
                 note="ticket system, 2026-08-01"),
        Variable("nominal_capacity", "auxiliary", "tickets/week", "staff * per_head"),
        Variable("load", "auxiliary", "dimensionless", "open_tickets / nominal_capacity"),
        # Chapter 15's curve, in the document. Refuses outside [0, 3].
        Variable("effectiveness", "lookup", "dimensionless", "load",
                 points=shape, evidence=level,
                 note="four load levels measured over the last year"),
        # A desk cannot close more than it holds. Without the floor the stock goes
        # negative, load goes negative, and the lookup stops the run: the refusal
        # is right and the missing constraint is the defect.
        Variable("closing", "flow", "tickets/week",
                 "min(nominal_capacity * effectiveness, open_tickets + arrivals)",
                 target="open_tickets", sign=-1),
        Variable("opening", "flow", "tickets/week", "arrivals",
                 target="open_tickets", sign=1),
        # Final backlog is a bad decision metric here: a desk with enough staff
        # clears to zero under every draw, so the number stops discriminating.
        # Ticket-weeks accumulate the waiting itself, which is what people feel.
        Variable("ticket_weeks", "stock", "ticket weeks", value=0.0, evidence="inferred",
                 note="a cumulative counter, so the critic's no-outflow finding is expected"),
        Variable("accruing", "flow", "ticket weeks/week", "open_tickets",
                 target="ticket_weeks", sign=1),
    ])
