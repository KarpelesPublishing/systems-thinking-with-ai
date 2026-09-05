import pytest

from stai.compiler.model import compile_model
from stai.compiler.units import validate_flow_units
from stai.contracts.common import ToolStatus
from stai.contracts.model import FlowSpec, ModelSpec, StockSpec


def model_with_flow(
    *,
    unit: str,
    source: str = "inventory",
    target: str | None = None,
) -> ModelSpec:
    return ModelSpec(
        model_id="unit-check",
        capability="stock-flow",
        time_unit="month",
        time_step=1.0,
        parameters={},
        stocks=[
            StockSpec(name="inventory", initial_value=10.0, unit="units"),
            StockSpec(name="cash", initial_value=10.0, unit="dollars"),
        ],
        flows=[
            FlowSpec(
                name="ship_orders",
                expression="1",
                source=source,
                target=target,
                unit=unit,
            )
        ],
    )


def test_valid_flow_unit_uses_endpoint_unit_and_model_time() -> None:
    response = validate_flow_units(model_with_flow(unit="units/month"))

    assert response.status is ToolStatus.SUCCESS


def test_flow_unit_must_use_model_time_unit() -> None:
    response = validate_flow_units(model_with_flow(unit="units"))

    assert response.status is ToolStatus.ERROR
    assert "units/month" in response.summary
    assert response.error is not None
    assert "do not compile" in response.error.stop_condition.lower()


def test_flow_unit_must_match_its_stock_endpoint() -> None:
    response = validate_flow_units(model_with_flow(unit="dollars/month"))

    assert response.status is ToolStatus.ERROR
    assert "expected units/month" in response.summary


def test_cross_stock_and_unknown_endpoints_are_rejected() -> None:
    mismatched = validate_flow_units(
        model_with_flow(unit="units/month", source="inventory", target="cash")
    )
    unknown = validate_flow_units(model_with_flow(unit="units/month", source="missing"))

    assert mismatched.status is ToolStatus.ERROR
    assert "expected" in mismatched.summary.lower()
    assert unknown.status is ToolStatus.ERROR
    assert "unknown stocks" in unknown.summary.lower()


def test_compiler_cannot_bypass_a_failed_flow_unit_check() -> None:
    with pytest.raises(ValueError, match="Flow units must match endpoint stock units"):
        compile_model(model_with_flow(unit="dollars/month"))
