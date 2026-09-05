from pathlib import Path

from pydantic import BaseModel, ConfigDict


class ToolRequest(BaseModel):
    """Fail closed when a catalog request contains undocumented fields."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class ProblemContractFileRequest(ToolRequest):
    contract_path: Path


class ModelFileRequest(ToolRequest):
    model_path: Path


class PolicyProposalFileRequest(ToolRequest):
    proposal_path: Path


class SimulationRequest(ToolRequest):
    model_path: Path
    experiment_path: Path
    output_path: Path
