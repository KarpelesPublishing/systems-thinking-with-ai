"""One stock, its flows, and the invariants that decide whether a path is readable.

The stock is the level. The flows are the rates that change it. Reading the level
off the inflow is the error this chapter exists to prevent.
"""

from .validate_number import validate_number


def net_flow(inflow: float, outflow: float) -> float:
    """Return the rate at which the stock changes: inflow minus outflow."""
    validate_number(inflow, "inflow")
    validate_number(outflow, "outflow")
    return inflow - outflow


def advance_stock(stock: float, inflow: float, outflow: float, dt: float) -> float:
    """Advance one stock by its net flow over one time step."""
    validate_number(stock, "stock")
    validate_number(dt, "dt")
    if dt < 0:
        raise ValueError("dt must be non-negative")
    return stock + dt * net_flow(inflow, outflow)


def integrate(
    initial: float, inflows: list[float], outflows: list[float], dt: float = 1.0
) -> list[float]:
    """Rebuild the whole path of a stock from its initial level and its flow history."""
    validate_number(initial, "initial")
    validate_number(dt, "dt")
    if dt <= 0:
        raise ValueError("dt must be positive")
    if len(inflows) != len(outflows):
        raise ValueError("inflows and outflows must have the same length")
    if not inflows:
        raise ValueError("flow history must not be empty")
    path = [float(initial)]
    for inflow, outflow in zip(inflows, outflows, strict=True):
        path.append(advance_stock(path[-1], inflow, outflow, dt))
    return path


def conservation_error(
    path: list[float], inflows: list[float], outflows: list[float], dt: float = 1.0
) -> float:
    """Return how far a path departs from the total net flow that should have produced it.

    A correct reconstruction returns 0.0. Any other value means the path and the
    flow history disagree, and one of the two records is wrong.
    """
    if len(path) != len(inflows) + 1:
        raise ValueError("path must hold one more value than the flow history")
    if len(inflows) != len(outflows):
        raise ValueError("inflows and outflows must have the same length")
    validate_number(dt, "dt")
    accumulated = sum(
        dt * net_flow(inflow, outflow)
        for inflow, outflow in zip(inflows, outflows, strict=True)
    )
    return (path[-1] - path[0]) - accumulated


def apply_floor(stock: float, floor: float = 0.0) -> float:
    """Hold a stock at a physical bound. A tank cannot drain past empty."""
    validate_number(stock, "stock")
    validate_number(floor, "floor")
    return stock if stock > floor else floor
