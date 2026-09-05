from dataclasses import dataclass

from stai.capabilities.stock_flow import supports_stock_flow
from stai.compiler.dependencies import expression_dependencies, topological_order
from stai.compiler.expressions import validate_expression
from stai.compiler.units import validate_flow_units
from stai.contracts.common import ToolStatus
from stai.contracts.model import ModelSpec


@dataclass(frozen=True)
class CompiledModel:
    spec: ModelSpec
    auxiliary_order: tuple[str, ...]
    flow_order: tuple[str, ...]


def compile_model(spec: ModelSpec) -> CompiledModel:
    if not supports_stock_flow(spec):
        raise ValueError(
            f"The stock-flow compiler does not support capability {spec.capability!r}."
        )
    stocks = {stock.name for stock in spec.stocks}
    for flow in spec.flows:
        if flow.source is not None and flow.source not in stocks:
            raise ValueError(f"Unknown flow source: {flow.source}.")
        if flow.target is not None and flow.target not in stocks:
            raise ValueError(f"Unknown flow target: {flow.target}.")

    unit_response = validate_flow_units(spec)
    if unit_response.status is ToolStatus.ERROR:
        raise ValueError(unit_response.summary)

    parameters = set(spec.parameters)
    expression_names = stocks | parameters | {auxiliary.name for auxiliary in spec.auxiliaries}
    for auxiliary in spec.auxiliaries:
        validate_expression(auxiliary.expression, allowed_names=expression_names)
    for flow in spec.flows:
        validate_expression(flow.expression, allowed_names=expression_names)
    auxiliary_dependencies = {
        auxiliary.name: expression_dependencies(auxiliary.expression)
        for auxiliary in spec.auxiliaries
    }
    auxiliary_order = topological_order(auxiliary_dependencies, stocks | parameters)
    flow_dependencies = {
        flow.name: expression_dependencies(flow.expression)
        for flow in spec.flows
    }
    flow_order = topological_order(flow_dependencies, stocks | parameters | set(auxiliary_order))
    return CompiledModel(spec, tuple(auxiliary_order), tuple(flow_order))
