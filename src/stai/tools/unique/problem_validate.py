from stai.contracts.common import ToolResponse, ToolStatus
from stai.contracts.problem import ProblemContract


def validate_problem_contract(contract: ProblemContract) -> ToolResponse:
    """Report whether an already-parsed problem contract is structurally valid."""
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary=f"Problem contract {contract.artifact_id} is structurally valid.",
        next_actions=["Validate evidence before promoting the artifact."],
        artifacts=[f"proposals/{contract.artifact_id}.json"],
        details={
            "state": contract.state.value,
            "evidence_mode": contract.evidence_mode.value,
        },
    )
