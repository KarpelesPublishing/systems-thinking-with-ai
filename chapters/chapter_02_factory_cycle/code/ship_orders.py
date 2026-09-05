from .validate_number import validate_number


def ship_orders(order_rate: float) -> float:
    """Use the external order rate as the shipment rate in the minimal model."""
    validate_number(order_rate, "order_rate")
    if order_rate < 0:
        raise ValueError("order_rate must be non-negative")
    return order_rate
