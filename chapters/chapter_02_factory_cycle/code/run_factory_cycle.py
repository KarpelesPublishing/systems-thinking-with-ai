import math

from .advance_factory_cycle import advance_factory_cycle
from .models import FactoryCycleParameters, FactoryCycleState


def run_factory_cycle(
    state: FactoryCycleState,
    parameters: FactoryCycleParameters,
    horizon: float,
    dt: float,
) -> list[dict[str, float]]:
    """Run the atomic factory-cycle composition and return inspectable rows."""
    if horizon <= 0:
        raise ValueError("horizon must be positive")
    if dt <= 0:
        raise ValueError("dt must be positive")
    raw_steps = horizon / dt
    steps = round(raw_steps)
    if not math.isclose(raw_steps, steps, rel_tol=0.0, abs_tol=1e-9):
        raise ValueError("horizon must be an exact multiple of dt")

    rows: list[dict[str, float]] = []
    current_state = state
    for step_number in range(steps + 1):
        step = advance_factory_cycle(current_state, parameters, dt)
        rows.append(
            {
                "time": step_number * dt,
                "inventory": current_state.inventory,
                "work_in_process": current_state.work_in_process,
                **step.auxiliaries,
                **step.rates,
            }
        )
        if step_number < steps:
            current_state = step.state
    return rows
