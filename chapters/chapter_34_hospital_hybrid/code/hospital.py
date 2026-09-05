"""Aggregate staffing joined to a patient-level queue, with subgroup outcomes."""

import random
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Group:
    """A patient group with its own share of arrivals and its own service demand."""

    name: str
    share: float
    service_multiplier: float


DEFAULT_GROUPS = (
    Group("routine", 0.75, 0.8),
    Group("complex", 0.25, 2.0),
)


@dataclass(frozen=True)
class StaffingPolicy:
    """The staffing rule and the scheduling discipline it runs under."""
    target_wait: float = 1.0
    adjustment_time: float = 4.0
    max_staff: float = 30.0
    min_staff: float = 4.0
    priority: str = "fifo"     # "fifo" or "shortest_first"


def _serve(queue: list[tuple[float, Group]], capacity: int, now: float,
           policy: StaffingPolicy) -> tuple[list[tuple[float, Group]], dict[str, list[float]]]:
    if policy.priority == "shortest_first":
        queue = sorted(queue, key=lambda item: item[1].service_multiplier)
    served, remaining = queue[:capacity], queue[capacity:]
    waits: dict[str, list[float]] = {}
    for arrival, group in served:
        waits.setdefault(group.name, []).append(now - arrival)
    return remaining, waits


def run(policy: StaffingPolicy, periods: int = 60, arrivals: float = 18.0,
        groups: tuple[Group, ...] = DEFAULT_GROUPS, seed: int = 5) -> dict[str, object]:
    """Run the coupled system and return outcomes per group, not only in total."""
    if abs(sum(g.share for g in groups) - 1.0) > 1e-9:
        raise ValueError("group shares must sum to 1")
    rng = random.Random(seed)
    staff = 10.0
    queue: list[tuple[float, Group]] = []
    waits: dict[str, list[float]] = {g.name: [] for g in groups}
    staff_path: list[float] = []

    for period in range(periods):
        for _ in range(int(round(arrivals))):
            roll, cumulative = rng.random(), 0.0
            for group in groups:
                cumulative += group.share
                if roll <= cumulative:
                    queue.append((period + rng.random(), group))
                    break
        mean_multiplier = sum(g.share * g.service_multiplier for g in groups)
        capacity = int(round(staff / mean_multiplier))
        queue, served = _serve(queue, capacity, period + 1.0, policy)
        for name, values in served.items():
            waits[name].extend(values)
        observed = statistics.fmean(
            [w for values in served.values() for w in values]
        ) if served else 0.0
        desired = staff * (observed / policy.target_wait) if policy.target_wait else staff
        staff += (min(desired, policy.max_staff) - staff) / policy.adjustment_time
        staff = max(policy.min_staff, min(policy.max_staff, staff))
        staff_path.append(staff)

    return {
        "staff": staff_path,
        "waits": waits,
        "mean_by_group": {k: (statistics.fmean(v) if v else 0.0) for k, v in waits.items()},
        "p90_by_group": {
            k: (sorted(v)[int(0.9 * (len(v) - 1))] if v else 0.0) for k, v in waits.items()
        },
        "queue_left": float(len(queue)),
    }


def equity_gap(outcome: dict[str, object]) -> float:
    """Worst group's mean wait divided by the best group's. One number, deliberately."""
    means = list(outcome["mean_by_group"].values())  # type: ignore[union-attr]
    best = min(m for m in means if m > 0) if any(m > 0 for m in means) else 0.0
    return max(means) / best if best > 0 else 0.0


def prohibited_objectives() -> tuple[str, ...]:
    """Objectives this model must never be optimized against."""
    return (
        "mean wait alone: improves by serving easy cases and abandoning hard ones",
        "throughput alone: same failure, expressed as volume",
        "cost per patient: rewards refusing the expensive patients",
        "any objective with no subgroup constraint attached",
    )
