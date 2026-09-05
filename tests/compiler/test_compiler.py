import pytest
from pydantic import ValidationError

from stai.compiler.dependencies import DependencyCycleError, topological_order
from stai.compiler.expressions import ExpressionError, evaluate_expression, validate_expression
from stai.compiler.model import compile_model
from stai.contracts.model import AuxiliarySpec, FlowSpec, ModelSpec, StockSpec


def test_expression_allows_only_safe_math() -> None:
    assert evaluate_expression(
        "max(0, order_rate + inventory_gap / adjustment_time)",
        {"order_rate": 10.0, "inventory_gap": 4.0, "adjustment_time": 2.0},
    ) == 12.0


@pytest.mark.parametrize(
    "expression",
    [
        "().__class__.__mro__",
        "values[0]",
        "lambda: 1",
        "__import__('os')",
        "[item for item in range(2)]",
    ],
)
def test_expression_rejects_unsafe_syntax(expression: str) -> None:
    with pytest.raises(ExpressionError):
        evaluate_expression(expression, {})


def test_expression_rejects_unknown_or_nonfinite_values() -> None:
    with pytest.raises(ExpressionError, match="Unknown variable"):
        evaluate_expression("missing + 1", {})
    with pytest.raises(ExpressionError, match="finite"):
        evaluate_expression("rate", {"rate": float("nan")})
    with pytest.raises(ExpressionError, match="evaluation failed"):
        evaluate_expression("1 / 0", {})


def test_expression_rejects_unbounded_power_before_evaluation() -> None:
    with pytest.raises(ExpressionError, match="exponent"):
        validate_expression("2 ** 1000000")
    with pytest.raises(ExpressionError, match="exponent"):
        evaluate_expression("base ** exponent", {"base": 2.0, "exponent": 101.0})
    with pytest.raises(ExpressionError):
        evaluate_expression("2 ** 1024", {})


def test_topological_order_is_deterministic_and_rejects_cycles() -> None:
    assert topological_order(
        {"later": {"first"}, "first": set(), "other": set()},
        known_inputs=set(),
    ) == ["first", "other", "later"]

    with pytest.raises(DependencyCycleError):
        topological_order({"a": {"b"}, "b": {"a"}}, known_inputs=set())


def test_compiler_rejects_unknown_flow_endpoints_before_runtime() -> None:
    model = ModelSpec(
        model_id="invalid-endpoint",
        capability="stock-flow",
        time_unit="month",
        time_step=1.0,
        parameters={"rate": 1.0},
        stocks=[StockSpec(name="inventory", initial_value=10.0, unit="units")],
        flows=[FlowSpec(name="ship", expression="rate", source="missing")],
    )

    with pytest.raises(ValueError, match="Unknown flow source"):
        compile_model(model)


def test_stock_flow_compiler_rejects_an_unsupported_capability() -> None:
    model = ModelSpec(
        model_id="unsupported-capability",
        capability="agent-based",
        time_unit="month",
        time_step=1.0,
        parameters={},
        stocks=[StockSpec(name="inventory", initial_value=10.0, unit="units")],
    )

    with pytest.raises(ValueError, match="stock-flow"):
        compile_model(model)


def test_compiler_rejects_unsafe_expressions_before_runtime() -> None:
    model = ModelSpec(
        model_id="unsafe-expression",
        capability="stock-flow",
        time_unit="month",
        time_step=1.0,
        parameters={},
        stocks=[StockSpec(name="inventory", initial_value=10.0, unit="units")],
        flows=[FlowSpec(name="ship", expression="().__class__", source="inventory")],
    )

    with pytest.raises(ExpressionError, match="Unsupported"):
        compile_model(model)


def test_model_rejects_parameter_names_that_shadow_model_variables() -> None:
    with pytest.raises(ValidationError, match="parameter names"):
        ModelSpec(
            model_id="ambiguous-names",
            capability="stock-flow",
            time_unit="month",
            time_step=1.0,
            parameters={"inventory": 99.0},
            stocks=[StockSpec(name="inventory", initial_value=1.0, unit="units")],
        )


def test_model_rejects_names_reserved_for_expression_functions() -> None:
    with pytest.raises(ValidationError, match="reserved expression names"):
        ModelSpec(
            model_id="reserved-name",
            capability="stock-flow",
            time_unit="month",
            time_step=1.0,
            parameters={},
            stocks=[StockSpec(name="inventory", initial_value=1.0, unit="units")],
            auxiliaries=[
                AuxiliarySpec(name="abs", expression="1", unit="units"),
                AuxiliarySpec(name="derived", expression="abs", unit="units"),
            ],
        )


def test_compiler_rejects_bare_reserved_function_names() -> None:
    model = ModelSpec(
        model_id="bare-reserved-function",
        capability="stock-flow",
        time_unit="month",
        time_step=1.0,
        parameters={},
        stocks=[StockSpec(name="inventory", initial_value=1.0, unit="units")],
        flows=[FlowSpec(name="ship", expression="abs", source="inventory")],
    )

    with pytest.raises(ExpressionError, match="only be called"):
        compile_model(model)
