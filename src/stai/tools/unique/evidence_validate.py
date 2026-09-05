from stai.contracts.common import (
    ClaimStatus,
    EvidenceMode,
    ToolError,
    ToolResponse,
    ToolStatus,
)
from stai.contracts.problem import ProblemContract


def validate_evidence(contract: ProblemContract) -> ToolResponse:
    """Keep teaching labels visible and block empirical promotion gaps."""
    if contract.evidence_mode is EvidenceMode.TEACHING_RECONSTRUCTION:
        return ToolResponse(
            status=ToolStatus.WARNING,
            summary=(
                "Case is a teaching reconstruction and cannot support an empirical policy claim."
            ),
            next_actions=["Preserve the teaching-reconstruction label in derived artifacts."],
            artifacts=[f"proposals/{contract.artifact_id}-evidence.json"],
        )

    blocking = [
        f"{claim.claim_id} ({claim.status.value})"
        for claim in contract.evidence
        if claim.status is not ClaimStatus.VERIFIED
    ]
    if blocking:
        return ToolResponse(
            status=ToolStatus.ERROR,
            summary=(
                "Unverified or contested evidence claims block promotion: "
                f"{', '.join(blocking)}."
            ),
            next_actions=["Verify each claim or remove it from the empirical contract."],
            artifacts=[],
            error=ToolError(
                root_cause="The empirical contract contains evidence claims that are not verified.",
                safe_retry="Verify each claim or remove it from the empirical contract.",
                stop_condition=(
                    "Do not promote this empirical artifact until every remaining "
                    "claim is verified."
                ),
            ),
        )

    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary="Evidence bundle contains only verified claims.",
        next_actions=["Proceed to a human review of the model proposal."],
        artifacts=[f"evidence/{contract.artifact_id}.json"],
    )
