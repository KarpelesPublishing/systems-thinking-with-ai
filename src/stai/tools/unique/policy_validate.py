from stai.contracts.common import ToolResponse, ToolStatus
from stai.contracts.model import PolicyProposal


def validate_policy_proposal(proposal: PolicyProposal) -> ToolResponse:
    """Return a reviewable proposal without granting execution authority."""
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary=(
            f"Policy proposal {proposal.proposal_id} is non-executable and ready for human review."
        ),
        next_actions=[
            "Run verification before a human approves, rejects, or supersedes the proposal."
        ],
        artifacts=[f"proposals/{proposal.proposal_id}.json"],
        details={
            "state": proposal.state.value,
            "external_execution_requested": proposal.external_execution_requested,
        },
    )
