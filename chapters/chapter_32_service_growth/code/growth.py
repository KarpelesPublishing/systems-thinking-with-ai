"""A service business where growth consumes the capacity that produced it."""

from dataclasses import dataclass


@dataclass
class State:
    """Customers, workforce, experience, and quality at one moment."""
    customers: float = 100.0
    workforce: float = 10.0
    experience: float = 40.0     # person-years held by the workforce
    quality: float = 1.0         # 0 to 1, a capability level


@dataclass(frozen=True)
class Policy:
    """The growth and hiring settings a run is given."""
    intake_rate: float = 0.10        # new customers per existing customer per period
    hiring_aggression: float = 0.25  # fraction of the workforce gap closed per period
    quality_floor: float = 0.0       # intake is throttled when quality falls below this
    customers_per_head: float = 12.0
    ramp_years: float = 2.0
    attrition: float = 0.05
    churn_sensitivity: float = 0.6


def effective_capacity(state: State, policy: Policy) -> float:
    """Heads weighted by experience. Chapter 17's dilution, in the growth loop."""
    if state.workforce <= 0:
        return 0.0
    average = state.experience / state.workforce
    return state.workforce * min(1.0, average / policy.ramp_years) * policy.customers_per_head


def load(state: State, policy: Policy) -> float:
    """Customers divided by experience-weighted capacity."""
    capacity = effective_capacity(state, policy)
    return state.customers / capacity if capacity > 0 else float("inf")


def step(state: State, policy: Policy, dt: float = 1.0) -> State:
    """One period. All flows read the state at the start, then all stocks are written."""
    pressure = load(state, policy)
    target_quality = 1.0 / pressure if pressure > 1.0 else 1.0
    quality_change = (target_quality - state.quality) / 2.0

    # Intake is scaled down as quality approaches the floor, not switched off at it.
    # A binary switch stops growth while churn continues, which shrinks the business faster.
    headroom = 1.0
    if policy.quality_floor > 0.0:
        span = 1.0 - policy.quality_floor
        if span > 0:
            headroom = min(1.0, max(0.0, (state.quality - policy.quality_floor) / span))
        else:
            headroom = 0.0
    joining = policy.intake_rate * state.customers * state.quality * headroom
    leaving = policy.churn_sensitivity * state.customers * (1.0 - state.quality)

    desired = state.customers / policy.customers_per_head
    hiring = max(0.0, (desired - state.workforce)) * policy.hiring_aggression
    departures = policy.attrition * state.workforce
    average = state.experience / state.workforce if state.workforce > 0 else 0.0

    return State(
        customers=max(0.0, state.customers + dt * (joining - leaving)),
        workforce=max(0.0, state.workforce + dt * (hiring - departures)),
        experience=max(0.0, state.experience + dt * (state.workforce - departures * average)),
        quality=min(1.0, max(0.0, state.quality + dt * quality_change)),
    )


def run(policy: Policy, periods: int = 60, start: State | None = None) -> list[State]:
    """Advance the business and return every period's state."""
    state = start or State()
    path = [state]
    for _ in range(periods):
        state = step(state, policy)
        path.append(state)
    return path


def summary(path: list[State], policy: Policy) -> dict[str, float]:
    """The few numbers a reader should carry out of a run."""
    return {
        "final_customers": path[-1].customers,
        "peak_customers": max(s.customers for s in path),
        "final_quality": path[-1].quality,
        "min_quality": min(s.quality for s in path),
        "final_workforce": path[-1].workforce,
        "peak_load": max(load(s, policy) for s in path),
    }
