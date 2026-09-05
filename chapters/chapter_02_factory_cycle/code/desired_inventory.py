from .validate_number import validate_number


def desired_inventory(order_rate: float, coverage: float) -> float:
    """Convert an order rate and desired coverage into a target inventory."""
    validate_number(order_rate, "order_rate")
    validate_number(coverage, "coverage")
    if order_rate < 0 or coverage < 0:
        raise ValueError("order_rate and coverage must be non-negative")
    return order_rate * coverage
