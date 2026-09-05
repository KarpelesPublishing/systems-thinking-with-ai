"""Shortcuts, defects, rework, and the productivity they consume."""

from dataclasses import dataclass


@dataclass
class State:
    """Delivery, debt, defects, and morale at one moment."""
    features_done: float = 0.0
    debt: float = 0.0            # shortcuts taken and not repaid
    defects: float = 0.0         # discovered and not yet fixed
    morale: float = 1.0


@dataclass(frozen=True)
class Policy:
    """Capacity, pressure, and the share reserved for repayment."""
    capacity: float = 10.0            # engineer-weeks available per period
    feature_pressure: float = 1.0     # 0 to 1, how hard delivery is pushed
    repayment_share: float = 0.0      # fraction of capacity reserved for paying debt
    shortcut_rate: float = 0.5        # debt created per unit of pressure per feature
    defect_rate: float = 0.08         # defects surfacing per unit of debt per period
    rework_cost: float = 0.6          # capacity consumed per defect fixed
    drag: float = 0.02                # capacity lost per unit of debt


def available_capacity(state: State, policy: Policy) -> float:
    """What is left after debt drag and morale. The quantity nobody measures."""
    drag = policy.drag * state.debt
    return max(0.0, (policy.capacity - drag) * state.morale)


def step(state: State, policy: Policy, dt: float = 1.0) -> State:
    """One period: deliver, accrue debt, surface defects, move morale."""
    usable = available_capacity(state, policy)
    to_repay = usable * policy.repayment_share
    to_deliver = usable - to_repay

    fixing = min(state.defects, to_deliver / policy.rework_cost)
    feature_capacity = max(0.0, to_deliver - fixing * policy.rework_cost)
    delivered = feature_capacity * policy.feature_pressure
    new_debt = delivered * policy.shortcut_rate * policy.feature_pressure
    repaid = min(state.debt, to_repay)
    surfacing = policy.defect_rate * state.debt

    morale_target = 1.0 - min(0.6, 0.02 * state.defects)
    return State(
        features_done=state.features_done + dt * delivered,
        debt=max(0.0, state.debt + dt * (new_debt - repaid)),
        defects=max(0.0, state.defects + dt * (surfacing - fixing)),
        morale=min(1.0, max(0.2, state.morale + dt * (morale_target - state.morale) / 4.0)),
    )


def run(policy: Policy, periods: int = 60, start: State | None = None) -> list[State]:
    """Advance the team and return every period's state."""
    state = start or State()
    path = [state]
    for _ in range(periods):
        state = step(state, policy)
        path.append(state)
    return path


def summary(path: list[State], policy: Policy) -> dict[str, float]:
    """The few numbers a reader should carry out of a run."""
    early = path[12].features_done
    return {
        "features_by_12": early,
        "features_total": path[-1].features_done,
        "final_debt": path[-1].debt,
        "peak_defects": max(s.defects for s in path),
        "final_capacity": available_capacity(path[-1], policy),
    }


def observable_measures() -> dict[str, str]:
    """What can be counted, and what has to stay a proxy."""
    return {
        "defects": "observable: a defect tracker counts them",
        "rework_time": "observable: time booked against fixes, if it is booked honestly",
        "features_done": "observable: shipped items",
        "debt": "PROXY: nobody can count shortcuts. Inferred from drag, or estimated by the team",
        "morale": "PROXY: surveys measure something correlated, on a different clock",
    }
