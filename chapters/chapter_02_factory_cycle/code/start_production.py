from .validate_number import validate_number


def start_production(order_rate: float, gap: float, adjustment_time: float) -> float:
    """Calculate production starts from order rate and inventory gap."""
    validate_number(order_rate, "order_rate")
    validate_number(gap, "gap")
    validate_number(adjustment_time, "adjustment_time")
    if order_rate < 0:
        raise ValueError("order_rate must be non-negative")
    if adjustment_time <= 0:
        raise ValueError("adjustment_time must be positive")
    return max(0.0, order_rate + gap / adjustment_time)
