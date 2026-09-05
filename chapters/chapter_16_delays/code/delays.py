"""Two delays with the same mean and different behavior."""

from collections import deque

from .validate_number import validate_number


class PipelineDelay:
    """A conveyor. What goes in comes out intact, exactly `length` periods later."""

    def __init__(self, length: int, initial: float = 0.0) -> None:
        if type(length) is not int or length < 1:
            raise ValueError("length must be a positive whole number of periods")
        validate_number(initial, "initial")
        self.length = length
        self.line: deque[float] = deque([float(initial)] * length, maxlen=length)

    def step(self, inflow: float) -> float:
        validate_number(inflow, "inflow")
        out = self.line[0]
        self.line.append(inflow)
        return out

    def in_transit(self) -> float:
        return sum(self.line)


class FirstOrderDelay:
    """A well-stirred tank. Output is proportional to what is currently held."""

    def __init__(self, mean: float, initial_rate: float = 0.0) -> None:
        validate_number(mean, "mean")
        if mean <= 0:
            raise ValueError("mean delay must be positive")
        validate_number(initial_rate, "initial_rate")
        self.mean = mean
        self.held = float(initial_rate) * mean

    def step(self, inflow: float, dt: float = 1.0) -> float:
        validate_number(inflow, "inflow")
        if dt <= 0:
            raise ValueError("dt must be positive")
        out = self.held / self.mean
        self.held += dt * (inflow - out)
        return out

    def in_transit(self) -> float:
        return self.held


def run_pipeline(inflows: list[float], length: int, initial: float = 0.0) -> list[float]:
    """Feed a series through a pipeline and return what emerges."""
    delay = PipelineDelay(length, initial)
    return [delay.step(x) for x in inflows]


def run_first_order(inflows: list[float], mean: float, initial_rate: float = 0.0) -> list[float]:
    """Feed a series through a first-order delay and return its output."""
    delay = FirstOrderDelay(mean, initial_rate)
    return [delay.step(x) for x in inflows]


def time_to_fraction(outflows: list[float], target: float, fraction: float) -> int | None:
    """First period where the output reaches a fraction of its eventual level."""
    if not 0.0 < fraction <= 1.0:
        raise ValueError("fraction must lie in (0, 1]")
    for i, value in enumerate(outflows):
        if value >= fraction * target:
            return i
    return None
