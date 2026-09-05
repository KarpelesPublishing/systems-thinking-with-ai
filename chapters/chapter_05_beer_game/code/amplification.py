"""Measure how much larger a stage's order swing is than the customer's."""

import statistics


def swing(series: list[float]) -> float:
    """Peak-to-trough range of a series."""
    if not series:
        raise ValueError("series must not be empty")
    return max(series) - min(series)


def amplification_ratio(customer_orders: list[float], stage_orders: list[float]) -> float:
    """Return the stage's order swing divided by the customer's.

    A ratio above 1.0 means the stage ordered more erratically than its customer did.
    The beer game's central observation is that this ratio grows with distance upstream.
    """
    base = swing(customer_orders)
    if base <= 0.0:
        raise ValueError("customer orders must vary for amplification to be defined")
    return swing(stage_orders) / base


def stage_variability(history: dict[str, list[list[float]]]) -> list[float]:
    """Standard deviation of each stage's order stream, retailer first."""
    orders = history["orders"]
    return [statistics.pstdev([week[i] for week in orders]) for i in range(len(orders[0]))]
