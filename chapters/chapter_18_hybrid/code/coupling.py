"""One boundary contract joining an aggregate staffing model to a patient queue.

The aggregate side carries staffing as a continuous stock. The queue side serves
individual patients. Neither can see inside the other. Everything that crosses does
so through one declared interface, at a stated frequency, in stated units.
"""

import random
import statistics
from dataclasses import dataclass


@dataclass(frozen=True)
class Interface:
    """What crosses the boundary, in which direction, and in what unit."""

    to_queue: tuple[str, ...] = ("servers",)
    to_aggregate: tuple[str, ...] = ("mean_wait", "queue_length")
    units: tuple[tuple[str, str], ...] = (
        ("servers", "clinicians"),
        ("mean_wait", "hours"),
        ("queue_length", "patients"),
    )
    exchange_every: int = 1  # periods between exchanges

    def unit_of(self, name: str) -> str:
        for key, unit in self.units:
            if key == name:
                return unit
        raise KeyError(f"'{name}' does not cross this boundary")

    def validate(self, payload: dict[str, float], direction: str) -> None:
        expected = self.to_queue if direction == "to_queue" else self.to_aggregate
        if set(payload) != set(expected):
            raise ValueError(
                f"{direction} payload must carry exactly {sorted(expected)}, got {sorted(payload)}"
            )


class AggregateStaffing:
    """Staff level closes part of the gap to a target derived from observed waiting."""

    def __init__(self, staff: float = 10.0, adjustment_time: float = 4.0,
                 target_wait: float = 0.5) -> None:
        if adjustment_time <= 0 or target_wait <= 0:
            raise ValueError("adjustment_time and target_wait must be positive")
        self.staff = float(staff)
        self.baseline = float(staff)
        self.adjustment_time = adjustment_time
        self.target_wait = target_wait

    def step(self, mean_wait: float, dt: float = 1.0) -> float:
        """Adjust staffing toward what the observed wait implies is needed.

        The target is anchored to the baseline establishment, not to whatever
        staffing happens to be now. A rule that multiplies the current level has
        no equilibrium: it drifts geometrically and never settles.
        """
        desired = self.baseline * (mean_wait / self.target_wait)
        desired = min(desired, self.baseline * 3.0)
        self.staff += dt * (desired - self.staff) / self.adjustment_time
        self.staff = max(1.0, self.staff)
        return self.staff


class PatientQueue:
    """Individual patients, first come first served, by however many servers exist."""

    def __init__(self, arrivals_per_period: float, service_time: float, seed: int) -> None:
        if arrivals_per_period < 0 or service_time <= 0:
            raise ValueError("arrivals non-negative, service_time positive")
        self.arrivals = arrivals_per_period
        self.service_time = service_time
        self.rng = random.Random(seed)
        self.waiting: list[float] = []

    def step(self, servers: int, now: float, dt: float = 1.0) -> dict[str, float]:
        if servers < 1:
            raise ValueError("a queue needs at least one server")
        for _ in range(int(round(self.arrivals * dt))):
            self.waiting.append(now + self.rng.random() * dt)
        capacity = int(round(servers * dt / self.service_time))
        served = self.waiting[:capacity]
        self.waiting = self.waiting[capacity:]
        waits = [(now + dt) - t for t in served]
        return {
            "mean_wait": statistics.fmean(waits) if waits else 0.0,
            "queue_length": float(len(self.waiting)),
        }


def run_coupled(periods: int, interface: Interface | None = None, seed: int = 3
                ) -> dict[str, list[float]]:
    """Run both models, exchanging only what the interface permits."""
    if periods < 1:
        raise ValueError("periods must be at least 1")
    interface = interface or Interface()
    staffing = AggregateStaffing()
    queue = PatientQueue(arrivals_per_period=9.0, service_time=1.0, seed=seed)
    history: dict[str, list[float]] = {"staff": [], "mean_wait": [], "queue_length": []}
    feedback = {"mean_wait": 0.0, "queue_length": 0.0}
    for period in range(periods):
        to_queue = {"servers": staffing.staff}
        interface.validate(to_queue, "to_queue")
        observed = queue.step(servers=max(1, int(round(to_queue["servers"]))), now=float(period))
        interface.validate(observed, "to_aggregate")
        if period % interface.exchange_every == 0:
            feedback = observed
        staffing.step(feedback["mean_wait"])
        history["staff"].append(staffing.staff)
        history["mean_wait"].append(observed["mean_wait"])
        history["queue_length"].append(observed["queue_length"])
    return history
