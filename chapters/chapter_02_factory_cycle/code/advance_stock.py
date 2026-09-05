from .validate_number import validate_number


def advance_stock(stock: float, inflow: float, outflow: float, dt: float) -> float:
    """Advance one stock by its inflow minus its outflow over one time step."""
    for value, name in (
        (stock, "stock"),
        (inflow, "inflow"),
        (outflow, "outflow"),
        (dt, "dt"),
    ):
        validate_number(value, name)
    if dt < 0:
        raise ValueError("dt must be non-negative")
    return stock + dt * (inflow - outflow)
