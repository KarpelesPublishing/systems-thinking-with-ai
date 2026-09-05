import math
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from stai.compiler.expressions import ExpressionError, evaluate_expression
from stai.compiler.model import CompiledModel

MAX_SIMULATION_STEPS = 100_000


@dataclass(frozen=True)
class SimulationResult:
    status: str
    rows: list[dict[str, float]]
    message: str


def _error(message: str, rows: list[dict[str, float]] | None = None) -> SimulationResult:
    return SimulationResult("error", rows or [], message)


def _is_finite_number(value: Any) -> bool:
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(float(value))
    except OverflowError:
        return False


def simulate(
    compiled: CompiledModel,
    horizon: float,
    parameter_overrides: Mapping[str, float],
) -> SimulationResult:
    """Run a deterministic Euler simulation without interacting with external systems."""
    if not _is_finite_number(horizon) or float(horizon) <= 0:
        return _error("Simulation horizon must be a finite positive number.")
    if not isinstance(parameter_overrides, Mapping):
        return _error("Parameter overrides must be a mapping of finite numeric values.")

    spec = compiled.spec
    if any(not isinstance(name, str) or not name for name in parameter_overrides):
        return _error("Parameter override names must be non-empty strings.")
    unknown_parameters = sorted(set(parameter_overrides) - set(spec.parameters))
    if unknown_parameters:
        return _error(f"Unknown parameter overrides: {', '.join(unknown_parameters)}.")
    if any(not _is_finite_number(value) for value in parameter_overrides.values()):
        return _error("Parameter overrides must contain finite numeric values.")

    parameters = {**dict(spec.parameters), **parameter_overrides}
    state = {stock.name: stock.initial_value for stock in spec.stocks}
    auxiliaries = {auxiliary.name: auxiliary for auxiliary in spec.auxiliaries}
    flows = {flow.name: flow for flow in spec.flows}
    rows: list[dict[str, float]] = []
    raw_steps = float(horizon) / spec.time_step
    if not math.isfinite(raw_steps):
        return _error("Simulation horizon produces a non-finite step count.")
    if raw_steps > MAX_SIMULATION_STEPS + 0.5:
        return _error(f"Simulation exceeds the step limit of {MAX_SIMULATION_STEPS}.")
    steps = int(round(raw_steps))
    if not math.isclose(raw_steps, steps, rel_tol=0.0, abs_tol=1e-9):
        return _error("Simulation horizon must be an exact multiple of the model time step.")

    for step in range(steps + 1):
        values = {**parameters, **state}
        try:
            for name in compiled.auxiliary_order:
                values[name] = evaluate_expression(auxiliaries[name].expression, values)
            flow_rates = {
                name: evaluate_expression(flows[name].expression, values)
                for name in compiled.flow_order
            }
        except ExpressionError as error:
            return _error(str(error), rows)

        rows.append({"time": step * spec.time_step, **state, **flow_rates})
        if step == steps:
            break

        changes = {name: 0.0 for name in state}
        for name, rate in flow_rates.items():
            flow = flows[name]
            if flow.source is not None:
                changes[flow.source] -= rate * spec.time_step
            if flow.target is not None:
                changes[flow.target] += rate * spec.time_step
        next_state = {name: state[name] + changes[name] for name in state}
        if any(not math.isfinite(value) for value in next_state.values()):
            return _error("Simulation produced a non-finite stock value.", rows)
        if any(value < -1e-9 for value in next_state.values()):
            return _error("Simulation would create a negative stock.", rows)
        state = {name: max(0.0, value) for name, value in next_state.items()}

    return SimulationResult("success", rows, "Simulation completed.")
