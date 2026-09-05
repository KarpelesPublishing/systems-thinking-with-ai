"""The clinic as one stock and two flows. What system dynamics sees."""

from .validate_number import validate_number


def advance_queue(waiting: float, arrivals: float, capacity: float, dt: float = 1.0) -> float:
    """Advance the number waiting. Service is capped by capacity and by who is present."""
    for value, name in ((waiting, "waiting"), (arrivals, "capacity"), (capacity, "capacity")):
        validate_number(value, name)
    if capacity < 0:
        raise ValueError("capacity must be non-negative")
    served = min(capacity, waiting / dt + arrivals)
    result = waiting + dt * (arrivals - served)
    return result if result > 0.0 else 0.0


def run_aggregate(
    arrival_rates: list[float], capacity: float, initial_waiting: float = 0.0
) -> list[float]:
    """Return the number waiting at the end of each period."""
    if not arrival_rates:
        raise ValueError("arrival_rates must not be empty")
    waiting, path = initial_waiting, []
    for arrivals in arrival_rates:
        waiting = advance_queue(waiting, arrivals, capacity)
        path.append(waiting)
    return path


def mean_wait(waiting_path: list[float], capacity: float) -> float:
    """Little's law, applied to the averages: mean queue divided by throughput."""
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    return (sum(waiting_path) / len(waiting_path)) / capacity
