"""Advance the whole chain one week, reading every flow before writing any stock."""

from .models import STAGE_NAMES, ChainParameters, Stage
from .policy import order_quantity, smooth_demand


def ship(stage: Stage, requested: float) -> float:
    """Ship what is asked for, or everything on hand. What is missed becomes backlog."""
    owed = stage.backlog + requested
    shipped = owed if owed <= stage.inventory else stage.inventory
    return shipped


def step_chain(
    stages: list[Stage], customer_order: float, parameters: ChainParameters
) -> tuple[list[Stage], list[float]]:
    """Advance every stage by one week and return the new state plus the orders placed.

    Flows are computed from the state at the start of the week. Stocks are written
    afterwards, so the result does not depend on the order the stages are visited in.
    """
    if len(stages) != len(STAGE_NAMES):
        raise ValueError(f"expected {len(STAGE_NAMES)} stages")

    incoming = [customer_order] + [stage.order_pipeline[0] for stage in stages[:-1]]
    arrivals = [stage.shipment_pipeline[0] for stage in stages]
    shipped = [ship(stage, request) for stage, request in zip(stages, incoming, strict=True)]

    orders = []
    for stage, observed in zip(stages, incoming, strict=True):
        expected = smooth_demand(stage.expected_demand, observed, parameters.demand_smoothing_time)
        orders.append(
            order_quantity(
                expected_demand=expected,
                inventory=stage.inventory,
                backlog=stage.backlog,
                supply_line=stage.supply_line(),
                target_inventory=parameters.target_inventory,
                inventory_adjustment_time=parameters.inventory_adjustment_time,
                supply_line_weight=parameters.supply_line_weight,
            )
        )

    updated = []
    for i, stage in enumerate(stages):
        upstream_shipment = shipped[i + 1] if i + 1 < len(stages) else orders[i]
        updated.append(
            Stage(
                inventory=stage.inventory + arrivals[i] - shipped[i],
                backlog=stage.backlog + incoming[i] - shipped[i],
                expected_demand=smooth_demand(
                    stage.expected_demand, incoming[i], parameters.demand_smoothing_time
                ),
                order_pipeline=stage.order_pipeline[1:] + [orders[i]],
                shipment_pipeline=stage.shipment_pipeline[1:] + [upstream_shipment],
            )
        )
    return updated, orders


def run_chain(
    customer_demand: list[float], parameters: ChainParameters | None = None
) -> dict[str, list[list[float]]]:
    """Run the chain over a demand history and return every stage's weekly record."""
    if not customer_demand:
        raise ValueError("customer_demand must not be empty")
    parameters = parameters or ChainParameters()
    weeks = parameters.pipeline_weeks
    stages = [
        Stage(order_pipeline=[4.0] * weeks, shipment_pipeline=[4.0] * weeks)
        for _ in STAGE_NAMES
    ]
    history: dict[str, list[list[float]]] = {"inventory": [], "backlog": [], "orders": []}
    for demand in customer_demand:
        history["inventory"].append([s.inventory for s in stages])
        history["backlog"].append([s.backlog for s in stages])
        stages, orders = step_chain(stages, demand, parameters)
        history["orders"].append(orders)
    return history
