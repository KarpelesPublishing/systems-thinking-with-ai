"""The solver is part of the model, not a detail underneath it."""

import random
from collections.abc import Callable


def euler(derivative: Callable[[float, float], float], state: float, t: float, dt: float) -> float:
    """One Euler step. Assumes the derivative at the start holds across the whole step."""
    return state + dt * derivative(t, state)


def heun(derivative: Callable[[float, float], float], state: float, t: float, dt: float) -> float:
    """Second-order: take an Euler step, then average the slopes at both ends."""
    slope_start = derivative(t, state)
    predicted = state + dt * slope_start
    slope_end = derivative(t + dt, predicted)
    return state + dt * 0.5 * (slope_start + slope_end)


def rk4(derivative: Callable[[float, float], float], state: float, t: float, dt: float) -> float:
    """Fourth-order Runge-Kutta: four slope samples across the step."""
    k1 = derivative(t, state)
    k2 = derivative(t + dt / 2, state + dt * k1 / 2)
    k3 = derivative(t + dt / 2, state + dt * k2 / 2)
    k4 = derivative(t + dt, state + dt * k3)
    return state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6


SOLVERS = {"euler": euler, "heun": heun, "rk4": rk4}


def integrate(
    derivative: Callable[[float, float], float],
    initial: float,
    dt: float,
    horizon: float,
    solver: str = "euler",
) -> list[float]:
    """Run one state variable to the horizon and return the whole path."""
    if solver not in SOLVERS:
        raise ValueError(f"solver must be one of {sorted(SOLVERS)}")
    if dt <= 0 or horizon <= 0:
        raise ValueError("dt and horizon must be positive")
    step = SOLVERS[solver]
    state, t, path = float(initial), 0.0, [float(initial)]
    while t < horizon - 1e-12:
        state = step(derivative, state, t, dt)
        t += dt
        path.append(state)
    return path


def logistic(rate: float, capacity: float) -> Callable[[float, float], float]:
    """The Bass-like growth used throughout this book, as a derivative."""
    if capacity <= 0:
        raise ValueError("capacity must be positive")
    return lambda _t, x: rate * x * (1.0 - x / capacity)


def sequential_pair(a: float, b: float, dt: float, k: float) -> tuple[float, float]:
    """Update stock A, then compute B's flow from A's NEW value. The bug."""
    a_new = a + dt * k * (b - a)
    b_new = b + dt * k * (a_new - b)
    return a_new, b_new


def simultaneous_pair(a: float, b: float, dt: float, k: float) -> tuple[float, float]:
    """Read both flows from the state at the start of the step, then write both."""
    flow_a = k * (b - a)
    flow_b = k * (a - b)
    return a + dt * flow_a, b + dt * flow_b


def step_refinement(
    derivative: Callable[[float, float], float],
    initial: float,
    horizon: float,
    solver: str,
    steps: tuple[float, ...] = (1.0, 0.5, 0.25),
) -> list[float]:
    """Endpoint of the same run at successively halved steps."""
    return [integrate(derivative, initial, dt, horizon, solver)[-1] for dt in steps]


def converged(endpoints: list[float], tolerance: float) -> bool:
    """True when halving the step has stopped moving the answer.

    Three runs at halved steps. Convergence means the last gap is inside the
    tolerance. A sequence that keeps moving by a similar amount at every halving
    has not settled, and no run in the set is reportable.
    """
    if len(endpoints) < 3:
        raise ValueError("convergence needs at least three runs")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    return abs(endpoints[-1] - endpoints[-2]) < tolerance


def apply_floor(state: float, floor: float = 0.0) -> float:
    """Hold a state at a physical bound after a step. A tank cannot drain past empty."""
    return state if state > floor else floor


def seeded_noise(values: list[float], sd: float, seed: int) -> list[float]:
    """Add reproducible measurement noise. Two runs with one seed are identical."""
    if sd < 0:
        raise ValueError("sd must be non-negative")
    if type(seed) is not int:
        raise ValueError("seed must be an integer")
    rng = random.Random(seed)
    return [v + rng.gauss(0.0, sd) for v in values]
