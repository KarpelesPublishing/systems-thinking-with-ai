"""One queue, counted two ways: as a population and as its parts.

The aggregate model answers what the average wait is. It cannot answer whose.
"""

import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Group:
    """A population with its own share of arrivals and its own service demand."""

    name: str
    share: float  # fraction of total arrivals
    service_multiplier: float  # how much longer this group takes to serve

    def __post_init__(self) -> None:
        if not 0.0 < self.share <= 1.0:
            raise ValueError("share must lie in (0, 1]")
        if self.service_multiplier <= 0:
            raise ValueError("service_multiplier must be positive")


def aggregate_wait(arrivals: float, servers: int, service_time: float) -> float:
    """Mean wait for one undifferentiated population, from queueing approximation."""
    if servers < 1:
        raise ValueError("servers must be at least 1")
    if service_time <= 0 or arrivals < 0:
        raise ValueError("service_time positive, arrivals non-negative")
    utilization = (arrivals * service_time) / servers
    if utilization >= 1.0:
        raise ValueError("the aggregate model is unstable at or above full utilization")
    return (utilization / (1.0 - utilization)) * (service_time / servers)


def stratified_waits(
    arrivals: float, servers: int, service_time: float, groups: list[Group]
) -> dict[str, float]:
    """Mean wait per group when each group's service demand differs.

    Shares must sum to 1. Every group waits in the same line, so each one's wait
    depends on the whole population's load, while its own service time differs.
    """
    total = sum(group.share for group in groups)
    if abs(total - 1.0) > 1e-9:
        raise ValueError(f"group shares must sum to 1, got {total}")
    mean_multiplier = sum(g.share * g.service_multiplier for g in groups)
    base = aggregate_wait(arrivals, servers, service_time * mean_multiplier)
    return {g.name: base + service_time * (g.service_multiplier - mean_multiplier) for g in groups}


def hidden_spread(waits: dict[str, float]) -> float:
    """The gap the aggregate number conceals: worst group minus best."""
    if len(waits) < 2:
        raise ValueError("stratification needs at least two groups")
    return max(waits.values()) - min(waits.values())


def population_mean(waits: dict[str, float], groups: list[Group]) -> float:
    """The share-weighted mean, which is what the aggregate model reports."""
    share = {g.name: g.share for g in groups}
    return sum(waits[name] * share[name] for name in waits)


def worst_served(waits: dict[str, float]) -> str:
    """Name the group that carries the cost. The aggregate model has no such function."""
    return max(waits, key=lambda name: waits[name])


def spread_ratio(waits: dict[str, float]) -> float:
    """How many times longer the worst-served group waits than the best-served."""
    values = list(waits.values())
    best = min(values)
    if best <= 0:
        raise ValueError("undefined when the best-served group has no wait")
    return max(values) / best


def summarize(waits: dict[str, float]) -> dict[str, float]:
    """Mean, spread, and worst-served group, reported together."""
    return {
        "mean_of_groups": statistics.fmean(waits.values()),
        "spread": hidden_spread(waits),
        "ratio": spread_ratio(waits),
    }
