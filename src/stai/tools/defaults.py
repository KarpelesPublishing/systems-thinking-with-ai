from pathlib import Path

from pydantic import BaseModel

from stai.contracts.common import ToolResponse
from stai.contracts.io import load_yaml
from stai.contracts.model import PolicyProposal
from stai.contracts.problem import ProblemContract
from stai.contracts.tooling import ToolCatalog
from stai.tools.evidence import validate_evidence
from stai.tools.model import compile_model_file, validate_model_file
from stai.tools.policy import validate_policy_proposal
from stai.tools.problem import validate_problem_contract
from stai.tools.registry import ToolRegistry
from stai.tools.requests import (
    ModelFileRequest,
    PolicyProposalFileRequest,
    ProblemContractFileRequest,
    SimulationRequest,
)
from stai.tools.simulation import run_simulation
from stai.tools.verification import run_verification


def _load_problem_contract(request: BaseModel) -> ProblemContract:
    typed = ProblemContractFileRequest.model_validate(request)
    return load_yaml(typed.contract_path, ProblemContract)


def _validate_problem(request: BaseModel) -> ToolResponse:
    return validate_problem_contract(_load_problem_contract(request))


def _validate_evidence(request: BaseModel) -> ToolResponse:
    return validate_evidence(_load_problem_contract(request))


def _validate_model(request: BaseModel) -> ToolResponse:
    typed = ModelFileRequest.model_validate(request)
    return validate_model_file(typed.model_path)


def _compile_model(request: BaseModel) -> ToolResponse:
    typed = ModelFileRequest.model_validate(request)
    return compile_model_file(typed.model_path)


def _validate_policy(request: BaseModel) -> ToolResponse:
    typed = PolicyProposalFileRequest.model_validate(request)
    proposal = load_yaml(typed.proposal_path, PolicyProposal)
    return validate_policy_proposal(proposal)


def _run_simulation(request: BaseModel) -> ToolResponse:
    typed = SimulationRequest.model_validate(request)
    return run_simulation(typed.model_path, typed.experiment_path, typed.output_path)


def _run_verification(request: BaseModel) -> ToolResponse:
    typed = SimulationRequest.model_validate(request)
    return run_verification(typed.model_path, typed.experiment_path, typed.output_path)


def build_default_registry(repository_root: Path) -> ToolRegistry:
    """Build the complete local-only registry from the checked-in catalog."""
    root = repository_root.resolve()
    catalog = load_yaml(root / "tooling/catalog.yaml", ToolCatalog)
    definitions = {definition.tool_id: definition for definition in catalog.tools}
    return ToolRegistry(
        definitions=definitions,
        input_models={
            "problem.validate": ProblemContractFileRequest,
            "evidence.validate": ProblemContractFileRequest,
            "model.validate": ModelFileRequest,
            "model.compile": ModelFileRequest,
            "policy.validate": PolicyProposalFileRequest,
            "simulation.run": SimulationRequest,
            "verification.run": SimulationRequest,
        },
        handlers={
            "problem.validate": _validate_problem,
            "evidence.validate": _validate_evidence,
            "model.validate": _validate_model,
            "model.compile": _compile_model,
            "policy.validate": _validate_policy,
            "simulation.run": _run_simulation,
            "verification.run": _run_verification,
        },
        repository_root=root,
    )
