from stai.capabilities.stock_flow import STOCK_FLOW_CAPABILITY, supports_stock_flow
from stai.contracts.model import ModelSpec, StockSpec


def model_with_capability(capability: str) -> ModelSpec:
    return ModelSpec(
        model_id="inventory",
        capability=capability,
        time_unit="month",
        time_step=1.0,
        parameters={},
        stocks=[StockSpec(name="inventory", initial_value=1.0, unit="units")],
    )


def test_stock_flow_capability_accepts_stock_flow_model() -> None:
    assert STOCK_FLOW_CAPABILITY.name == "stock-flow"
    assert STOCK_FLOW_CAPABILITY.required_artifacts == ("ModelSpec", "ExperimentSpec")
    assert supports_stock_flow(model_with_capability("stock-flow")) is True


def test_stock_flow_capability_rejects_other_model_types() -> None:
    assert supports_stock_flow(model_with_capability("agent-based")) is False
