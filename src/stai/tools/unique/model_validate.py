from pathlib import Path

from stai.compiler.units import validate_flow_units
from stai.contracts.common import ToolResponse, ToolStatus
from stai.contracts.io import load_yaml
from stai.contracts.model import ModelSpec


def validate_model_file(path: Path) -> ToolResponse:
    """Load and dimension-check a stock-flow model artifact."""
    model = load_yaml(path, ModelSpec)
    unit_response = validate_flow_units(model)
    if unit_response.status is ToolStatus.ERROR:
        return unit_response
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary=f"Model file {path} is structurally and dimensionally valid.",
        next_actions=["Compile the model before simulation."],
        artifacts=[str(path)],
    )
