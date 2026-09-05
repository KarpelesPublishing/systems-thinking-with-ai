"""State and parameters for one stage of a four-stage distribution chain."""

from dataclasses import dataclass, field

STAGE_NAMES = ("retailer", "wholesaler", "distributor", "factory")


@dataclass
class Stage:
    """One link in the chain: what it holds, what it owes, and what is in transit to it."""

    inventory: float = 12.0
    backlog: float = 0.0
    expected_demand: float = 4.0
    order_pipeline: list[float] = field(default_factory=lambda: [4.0, 4.0])
    shipment_pipeline: list[float] = field(default_factory=lambda: [4.0, 4.0])

    def supply_line(self) -> float:
        """Everything ordered and not yet received. The quantity players forget."""
        return sum(self.order_pipeline) + sum(self.shipment_pipeline)


@dataclass
class ChainParameters:
    """One policy, applied identically at every stage."""

    target_inventory: float = 12.0
    inventory_adjustment_time: float = 4.0
    supply_line_weight: float = 0.0
    demand_smoothing_time: float = 4.0
    pipeline_weeks: int = 2   # weeks of delay in each direction, order and shipment

    def __post_init__(self) -> None:
        if self.pipeline_weeks < 1:
            raise ValueError("pipeline_weeks must be at least 1")
