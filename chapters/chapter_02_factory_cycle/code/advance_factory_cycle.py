from .advance_stock import advance_stock
from .complete_production import complete_production
from .desired_inventory import desired_inventory
from .inventory_gap import inventory_gap
from .models import FactoryCycleParameters, FactoryCycleState, FactoryCycleStep
from .ship_orders import ship_orders
from .start_production import start_production


def advance_factory_cycle(
    state: FactoryCycleState,
    parameters: FactoryCycleParameters,
    dt: float,
) -> FactoryCycleStep:
    """Assemble the atomic equations into one deterministic factory-cycle step."""
    target_inventory = desired_inventory(
        order_rate=parameters.order_rate,
        coverage=parameters.desired_coverage,
    )
    gap = inventory_gap(desired=target_inventory, current=state.inventory)
    starts = start_production(
        order_rate=parameters.order_rate,
        gap=gap,
        adjustment_time=parameters.inventory_adjustment_time,
    )
    completions = complete_production(
        work_in_process=state.work_in_process,
        production_delay=parameters.production_delay,
    )
    shipments = ship_orders(parameters.order_rate)
    next_state = FactoryCycleState(
        inventory=advance_stock(state.inventory, completions, shipments, dt),
        work_in_process=advance_stock(state.work_in_process, starts, completions, dt),
    )
    return FactoryCycleStep(
        state=next_state,
        auxiliaries={"desired_inventory": target_inventory, "inventory_gap": gap},
        rates={
            "start_production": starts,
            "complete_production": completions,
            "ship_orders": shipments,
        },
    )
