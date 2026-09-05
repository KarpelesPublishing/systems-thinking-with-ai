from dataclasses import dataclass


@dataclass(frozen=True)
class FactoryCycleState:
    """What the factory holds at the start of a week."""
    inventory: float
    work_in_process: float


@dataclass(frozen=True)
class FactoryCycleParameters:
    """The policy constants a factory run is given."""
    order_rate: float
    desired_coverage: float
    inventory_adjustment_time: float
    production_delay: float


@dataclass(frozen=True)
class FactoryCycleStep:
    """One week's flows, kept beside the state they produced."""
    state: FactoryCycleState
    auxiliaries: dict[str, float]
    rates: dict[str, float]
