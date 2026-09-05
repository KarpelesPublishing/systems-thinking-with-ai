from .validate_number import validate_number


def inventory_gap(desired: float, current: float) -> float:
    """Return the difference between target and current inventory."""
    validate_number(desired, "desired")
    validate_number(current, "current")
    return desired - current
