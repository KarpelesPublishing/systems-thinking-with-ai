from stai.contracts.common import ArtifactState, ToolStatus
from stai.contracts.model import PolicyProposal
from stai.tools.policy import validate_policy_proposal


def test_policy_validator_returns_a_non_executable_proposal_for_human_review() -> None:
    proposal = PolicyProposal(
        proposal_id="slower-adjustment",
        model_id="factory-cycle",
        objective="Reduce oscillation in a teaching model.",
        constraints=["Remain a simulated proposal."],
        proposed_changes={"inventory_adjustment_time": 2.0},
        state=ArtifactState.PROPOSED,
    )

    response = validate_policy_proposal(proposal)

    assert response.status is ToolStatus.SUCCESS
    assert response.details["state"] == "proposed"
    assert response.details["external_execution_requested"] is False
