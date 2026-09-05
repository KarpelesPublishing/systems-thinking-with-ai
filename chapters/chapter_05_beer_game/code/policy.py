"""The ordering rule each stage applies using only what it can see."""

from .validate_number import validate_number


def smooth_demand(expected: float, observed: float, smoothing_time: float) -> float:
    """Update a stage's belief about demand by closing part of the gap to what it just saw."""
    for value, name in ((expected, "expected"), (observed, "observed")):
        validate_number(value, name)
    validate_number(smoothing_time, "smoothing_time")
    if smoothing_time <= 0:
        raise ValueError("smoothing_time must be positive")
    return expected + (observed - expected) / smoothing_time


def order_quantity(
    expected_demand: float,
    inventory: float,
    backlog: float,
    supply_line: float,
    target_inventory: float,
    inventory_adjustment_time: float,
    supply_line_weight: float = 0.0,
) -> float:
    """Replace expected demand, correct the inventory gap, and discount the supply line.

    `supply_line_weight` is the whole experiment. At 0.0 the stage ignores what it has
    already ordered and re-orders to fix a gap that existing orders will fix on their own.
    At 1.0 it credits the supply line in full.
    """
    for value, name in (
        (expected_demand, "expected_demand"),
        (inventory, "inventory"),
        (backlog, "backlog"),
        (supply_line, "supply_line"),
        (target_inventory, "target_inventory"),
        (supply_line_weight, "supply_line_weight"),
    ):
        validate_number(value, name)
    validate_number(inventory_adjustment_time, "inventory_adjustment_time")
    if inventory_adjustment_time <= 0:
        raise ValueError("inventory_adjustment_time must be positive")
    if not 0.0 <= supply_line_weight <= 1.0:
        raise ValueError("supply_line_weight must lie between 0 and 1")

    effective_stock = inventory - backlog + supply_line_weight * supply_line
    gap = target_inventory - effective_stock
    order = expected_demand + gap / inventory_adjustment_time
    return order if order > 0.0 else 0.0
