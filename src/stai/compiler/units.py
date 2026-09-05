from stai.contracts.common import ToolError, ToolResponse, ToolStatus
from stai.contracts.model import ModelSpec


def validate_flow_units(spec: ModelSpec) -> ToolResponse:
    """Require every flow to use its endpoint stock unit per model time unit."""
    stock_units = {stock.name: stock.unit for stock in spec.stocks}
    invalid: list[str] = []
    for flow in spec.flows:
        endpoints = [
            endpoint for endpoint in (flow.source, flow.target) if endpoint is not None
        ]
        unknown = [endpoint for endpoint in endpoints if endpoint not in stock_units]
        if unknown:
            invalid.append(f"{flow.name} references unknown stocks {', '.join(unknown)}")
            continue
        expected_units = {f"{stock_units[endpoint]}/{spec.time_unit}" for endpoint in endpoints}
        if len(expected_units) != 1 or flow.unit not in expected_units:
            expected = ", ".join(sorted(expected_units))
            invalid.append(f"{flow.name} expected {expected}, got {flow.unit}")
    if invalid:
        return ToolResponse(
            status=ToolStatus.ERROR,
            summary=(
                "Flow units must match endpoint stock units and time: "
                f"{'; '.join(invalid)}."
            ),
            next_actions=["Correct flow units before compiling the model."],
            artifacts=[],
            error=ToolError(
                root_cause="At least one flow uses a unit incompatible with the model time unit.",
                safe_retry="Correct flow units before compiling the model.",
                stop_condition=(
                    "Do not compile or simulate this model until every flow has a valid rate unit."
                ),
            ),
        )
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary="All flow units use the model time unit.",
        next_actions=["Compile the dependency graph."],
        artifacts=[],
    )
