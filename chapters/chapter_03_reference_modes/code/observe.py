"""Add measurement noise to a clean path, with a seed so the run is reproducible."""

import random

from .validate_number import validate_number


def add_observation_noise(path: list[float], sd: float, seed: int) -> list[float]:
    """Return `path` with independent Gaussian measurement error, reproducible from `seed`."""
    validate_number(sd, "sd")
    if sd < 0:
        raise ValueError("sd must be non-negative")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    if not path:
        raise ValueError("path must not be empty")
    rng = random.Random(seed)
    return [value + rng.gauss(0.0, sd) for value in path]
