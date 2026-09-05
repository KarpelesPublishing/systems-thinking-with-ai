"""The same clinic as individual patients waiting in line. What discrete-event sees."""

import random
import statistics


def run_queue(
    arrivals_per_period: float,
    servers: int,
    service_time: float,
    periods: int,
    seed: int,
) -> list[float]:
    """Serve arriving patients first-come-first-served and return every individual wait.

    Arrivals are Poisson within each period and service times are exponential, so two
    runs with the same averages produce different individual experiences. That gap is
    the reason this sketch exists alongside the aggregate one.
    """
    if servers < 1:
        raise ValueError("servers must be at least 1")
    if service_time <= 0 or arrivals_per_period < 0:
        raise ValueError("service_time must be positive and arrivals non-negative")
    if periods < 1:
        raise ValueError("periods must be at least 1")

    rng = random.Random(seed)
    arrival_times: list[float] = []
    for period in range(periods):
        for _ in range(_poisson(rng, arrivals_per_period)):
            arrival_times.append(period + rng.random())
    arrival_times.sort()

    free_at = [0.0] * servers
    waits: list[float] = []
    for arrival in arrival_times:
        i = min(range(servers), key=lambda k: free_at[k])
        start = arrival if free_at[i] < arrival else free_at[i]
        waits.append(start - arrival)
        free_at[i] = start + rng.expovariate(1.0 / service_time)
    return waits


def _poisson(rng: random.Random, mean: float) -> int:
    """Knuth's method. Small means only, which is all this teaching model needs."""
    if mean <= 0:
        return 0
    import math

    limit, k, product = math.exp(-mean), 0, 1.0
    while True:
        product *= rng.random()
        if product <= limit:
            return k
        k += 1


def wait_percentile(waits: list[float], percentile: float) -> float:
    """Return the wait that the given percentage of patients came in under."""
    if not waits:
        raise ValueError("waits must not be empty")
    if not 0.0 < percentile < 100.0:
        raise ValueError("percentile must lie strictly between 0 and 100")
    ordered = sorted(waits)
    index = int(round((percentile / 100.0) * (len(ordered) - 1)))
    return ordered[index]


def wait_summary(waits: list[float]) -> dict[str, float]:
    """Mean, median, and tail. The aggregate sketch can only produce the first."""
    return {
        "mean": statistics.fmean(waits),
        "median": statistics.median(waits),
        "p90": wait_percentile(waits, 90.0),
        "p99": wait_percentile(waits, 99.0),
        "worst": max(waits),
    }
