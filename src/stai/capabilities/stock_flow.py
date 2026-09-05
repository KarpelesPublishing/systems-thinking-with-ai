from dataclasses import dataclass

from stai.contracts.model import ModelSpec


@dataclass(frozen=True)
class Capability:
    name: str
    required_artifacts: tuple[str, ...]
    supported_tools: tuple[str, ...]


STOCK_FLOW_CAPABILITY = Capability(
    name="stock-flow",
    required_artifacts=("ModelSpec", "ExperimentSpec"),
    supported_tools=("model.validate", "model.compile", "simulation.run", "verification.run"),
)


def supports_stock_flow(spec: ModelSpec) -> bool:
    return spec.capability == STOCK_FLOW_CAPABILITY.name
