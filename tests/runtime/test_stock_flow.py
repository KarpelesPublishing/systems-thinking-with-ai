import pytest

from stai.compiler.model import compile_model
from stai.contracts.model import FlowSpec, ModelSpec, StockSpec
from stai.runtime.stock_flow import MAX_SIMULATION_STEPS, simulate


def draining_model(*, rate: float = 4.0, time_step: float = 0.5) -> ModelSpec:
    return ModelSpec(
        model_id="draining-stock",
        capability="stock-flow",
        time_unit="month",
        time_step=time_step,
        parameters={"rate": rate},
        stocks=[StockSpec(name="inventory", initial_value=10.0, unit="units")],
        flows=[FlowSpec(name="ship_orders", expression="rate", source="inventory")],
    )


def test_outflow_reduces_stock_by_rate_times_step() -> None:
    result = simulate(compile_model(draining_model()), horizon=1.0, parameter_overrides={})

    assert result.status == "success"
    assert result.rows[-1]["inventory"] == 6.0


def test_runtime_returns_error_for_negative_stock() -> None:
    result = simulate(
        compile_model(draining_model(rate=20.0, time_step=1.0)),
        horizon=1.0,
        parameter_overrides={},
    )

    assert result.status == "error"
    assert "negative stock" in result.message.lower()


def test_runtime_rejects_horizon_that_is_not_a_multiple_of_the_time_step() -> None:
    result = simulate(compile_model(draining_model()), horizon=0.75, parameter_overrides={})

    assert result.status == "error"
    assert "multiple" in result.message.lower()


@pytest.mark.parametrize("horizon", [True, 0.0, -1.0, float("nan"), float("inf")])
def test_runtime_rejects_invalid_horizons(horizon: object) -> None:
    result = simulate(compile_model(draining_model()), horizon=horizon, parameter_overrides={})

    assert result.status == "error"
    assert result.rows == []


def test_runtime_rejects_overflowing_horizons_and_excessive_step_counts() -> None:
    compiled = compile_model(draining_model())

    overflowing = simulate(compiled, horizon=10**400, parameter_overrides={})
    excessive = simulate(
        compiled,
        horizon=(MAX_SIMULATION_STEPS + 1) * compiled.spec.time_step,
        parameter_overrides={},
    )

    assert overflowing.status == "error"
    assert "finite" in overflowing.message.lower()
    assert excessive.status == "error"
    assert "step limit" in excessive.message.lower()


def test_runtime_rejects_unknown_or_nonfinite_parameter_overrides() -> None:
    compiled = compile_model(draining_model())

    unknown = simulate(compiled, horizon=1.0, parameter_overrides={"unknown": 1.0})
    nonfinite = simulate(compiled, horizon=1.0, parameter_overrides={"rate": float("nan")})
    malformed = simulate(compiled, horizon=1.0, parameter_overrides={1: 1.0})

    assert unknown.status == "error"
    assert "unknown parameter" in unknown.message.lower()
    assert nonfinite.status == "error"
    assert "finite" in nonfinite.message.lower()
    assert malformed.status == "error"
    assert "names" in malformed.message.lower()


def test_runtime_is_deterministic_for_identical_inputs() -> None:
    compiled = compile_model(draining_model())

    first = simulate(compiled, horizon=1.0, parameter_overrides={})
    second = simulate(compiled, horizon=1.0, parameter_overrides={})

    assert first == second
