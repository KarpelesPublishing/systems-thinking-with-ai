"""Limits to growth, implemented twice with different boundaries.

Same archetype, same growth engine, one difference: whether the limit is outside
the model or inside it. The behaviors are not variations on each other.
"""

from .validate_number import validate_number


def _check(initial: float, capacity: float, rate: float, steps: int) -> None:
    for value, name in ((initial, "initial"), (capacity, "capacity"), (rate, "rate")):
        validate_number(value, name)
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    if type(steps) is not int or steps < 1:
        raise ValueError("steps must be a positive integer")


def fixed_limit(
    initial: float, capacity: float, rate: float, steps: int, dt: float = 1.0
) -> list[float]:
    """Boundary A: the limit is exogenous. Growth approaches it and stops."""
    _check(initial, capacity, rate, steps)
    path = [float(initial)]
    for _ in range(steps):
        state = path[-1]
        path.append(state + dt * rate * state * (1.0 - state / capacity))
    return path


def eroding_limit(
    initial: float,
    capacity: float,
    rate: float,
    erosion_rate: float,
    steps: int,
    dt: float = 1.0,
) -> tuple[list[float], list[float]]:
    """Boundary B: the limit is endogenous, consumed by the growth it constrains.

    Returns the state path and the capacity path, because under this boundary the
    capacity is a model variable and hiding it would hide the mechanism.
    """
    _check(initial, capacity, rate, steps)
    validate_number(erosion_rate, "erosion_rate")
    if erosion_rate < 0:
        raise ValueError("erosion_rate must be non-negative")
    state_path, capacity_path = [float(initial)], [float(capacity)]
    for _ in range(steps):
        state, limit = state_path[-1], capacity_path[-1]
        growth = rate * state * (1.0 - state / limit) if limit > 0 else -rate * state
        capacity_path.append(max(0.0, limit - dt * erosion_rate * state))
        state_path.append(max(0.0, state + dt * growth))
    return state_path, capacity_path


def settles(path: list[float], tolerance: float = 0.01) -> bool:
    """True when the path stops moving. The observable that separates the two boundaries."""
    if len(path) < 3:
        raise ValueError("path is too short to judge")
    return abs(path[-1] - path[-2]) < tolerance and path[-1] > tolerance


def peaks_then_falls(path: list[float], margin: float = 0.05) -> bool:
    """True when the path rises to a peak and ends meaningfully below it."""
    peak = max(path)
    return peak > path[0] and path[-1] < peak * (1.0 - margin)
