from pathlib import Path

from stai.compiler.model import compile_model
from stai.contracts.common import ToolResponse, ToolStatus
from stai.contracts.io import load_yaml
from stai.contracts.model import ModelSpec


def compile_model_file(path: Path) -> ToolResponse:
    """Compile a model after the compiler's capability and unit checks pass."""
    compiled = compile_model(load_yaml(path, ModelSpec))
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary=f"Model {compiled.spec.model_id} compiled.",
        next_actions=["Run a case experiment."],
        artifacts=[str(path)],
        details={
            "auxiliary_order": list(compiled.auxiliary_order),
            "flow_order": list(compiled.flow_order),
        },
    )
