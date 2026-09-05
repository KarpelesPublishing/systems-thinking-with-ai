"""The six reference modes this book uses as behavior targets.

Each generator returns the full path of one variable over `steps` time steps of
length `dt`. A path is a behavior target, not a causal explanation: two different
structures can produce the same curve.
"""

import math

from .validate_number import validate_number


def _check(steps: int, dt: float) -> None:
    if type(steps) is not int or steps < 1:
        raise ValueError("steps must be a positive integer")
    validate_number(dt, "dt")
    if dt <= 0:
        raise ValueError("dt must be positive")


def exponential_growth(initial: float, rate: float, steps: int, dt: float = 1.0) -> list[float]:
    """Reinforcing growth: the net flow is proportional to the stock itself."""
    validate_number(initial, "initial")
    validate_number(rate, "rate")
    _check(steps, dt)
    path = [float(initial)]
    for _ in range(steps):
        path.append(path[-1] + dt * rate * path[-1])
    return path


def exponential_decay(initial: float, rate: float, steps: int, dt: float = 1.0) -> list[float]:
    """Balancing decay toward zero at a rate proportional to what remains."""
    validate_number(initial, "initial")
    validate_number(rate, "rate")
    _check(steps, dt)
    if rate < 0:
        raise ValueError("rate must be non-negative")
    path = [float(initial)]
    for _ in range(steps):
        path.append(path[-1] - dt * rate * path[-1])
    return path


def goal_seeking(
    initial: float, goal: float, adjustment_time: float, steps: int, dt: float = 1.0
) -> list[float]:
    """Balancing approach to a goal, closing a fixed fraction of the gap each step."""
    validate_number(initial, "initial")
    validate_number(goal, "goal")
    validate_number(adjustment_time, "adjustment_time")
    _check(steps, dt)
    if adjustment_time <= 0:
        raise ValueError("adjustment_time must be positive")
    path = [float(initial)]
    for _ in range(steps):
        path.append(path[-1] + dt * (goal - path[-1]) / adjustment_time)
    return path


def oscillation(
    level: float, amplitude: float, period: float, steps: int, dt: float = 1.0
) -> list[float]:
    """Repeated overshoot and undershoot around a level, with a fixed period."""
    validate_number(level, "level")
    validate_number(amplitude, "amplitude")
    validate_number(period, "period")
    _check(steps, dt)
    if period <= 0:
        raise ValueError("period must be positive")
    return [level + amplitude * math.sin(2 * math.pi * (i * dt) / period) for i in range(steps + 1)]


def s_shaped_growth(
    initial: float, capacity: float, rate: float, steps: int, dt: float = 1.0
) -> list[float]:
    """Reinforcing growth that a fixed carrying capacity progressively limits."""
    validate_number(initial, "initial")
    validate_number(capacity, "capacity")
    validate_number(rate, "rate")
    _check(steps, dt)
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    path = [float(initial)]
    for _ in range(steps):
        current = path[-1]
        path.append(current + dt * rate * current * (1.0 - current / capacity))
    return path


def overshoot_and_collapse(
    initial: float,
    capacity: float,
    rate: float,
    erosion_rate: float,
    steps: int,
    dt: float = 1.0,
) -> list[float]:
    """S-shaped growth against a capacity that the stock itself erodes."""
    validate_number(initial, "initial")
    validate_number(capacity, "capacity")
    validate_number(rate, "rate")
    validate_number(erosion_rate, "erosion_rate")
    _check(steps, dt)
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    if erosion_rate < 0:
        raise ValueError("erosion_rate must be non-negative")
    path = [float(initial)]
    remaining = float(capacity)
    for _ in range(steps):
        current = path[-1]
        limit = remaining if remaining > 0 else 0.0
        growth = rate * current * (1.0 - current / limit) if limit > 0 else -rate * current
        remaining = max(0.0, remaining - dt * erosion_rate * current)
        path.append(max(0.0, current + dt * growth))
    return path
