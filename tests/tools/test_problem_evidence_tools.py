from stai.contracts.common import ArtifactState, ClaimStatus, EvidenceMode, ToolStatus
from stai.contracts.problem import EvidenceClaim, ProblemContract, VariableSpec
from stai.tools.evidence import validate_evidence
from stai.tools.problem import validate_problem_contract


def build_contract(
    evidence_mode: EvidenceMode,
    evidence: list[EvidenceClaim],
) -> ProblemContract:
    return ProblemContract(
        artifact_id="problem",
        title="Problem",
        decision="Choose a simulated policy.",
        decision_owner="Human reviewer",
        stakeholders=["operator"],
        time_horizon="12 months",
        reference_behavior="Backlog changes over time.",
        variables=[VariableSpec(name="backlog", unit="work-items")],
        capabilities=["stock-flow"],
        assumptions=["The case remains within a simulated environment."],
        evidence_mode=evidence_mode,
        evidence=evidence,
        constraints=["Stay in the simulated environment."],
        prohibited_objectives=["Execute a real policy."],
        authority_boundary="Human approval required.",
        success_criteria=["Produce a reviewable artifact."],
        review_requirements=["A human must review the proposed artifact."],
        state=ArtifactState.PROPOSED,
    )


def test_teaching_reconstruction_returns_a_warning() -> None:
    response = validate_evidence(build_contract(EvidenceMode.TEACHING_RECONSTRUCTION, []))

    assert response.status is ToolStatus.WARNING
    assert "teaching reconstruction" in response.summary.lower()
    assert "empirical" in response.summary.lower()


def test_unverified_empirical_claim_blocks_promotion() -> None:
    claim = EvidenceClaim(
        claim_id="claim-1",
        statement="Observed backlog doubled.",
        status=ClaimStatus.UNVERIFIED,
        source_urls=[],
    )

    response = validate_evidence(build_contract(EvidenceMode.EMPIRICAL, [claim]))

    assert response.status is ToolStatus.ERROR
    assert "unverified" in response.summary.lower()
    assert response.error is not None
    assert "do not promote" in response.error.stop_condition.lower()


def test_contested_empirical_claim_also_blocks_promotion() -> None:
    claim = EvidenceClaim(
        claim_id="claim-2",
        statement="Observed backlog fell.",
        status=ClaimStatus.CONTESTED,
        source_urls=["https://example.test/evidence"],
    )

    response = validate_evidence(build_contract(EvidenceMode.EMPIRICAL, [claim]))

    assert response.status is ToolStatus.ERROR
    assert "contested" in response.summary.lower()


def test_verified_empirical_claims_are_validated_without_promotion() -> None:
    claim = EvidenceClaim(
        claim_id="claim-3",
        statement="Observed backlog was stable.",
        status=ClaimStatus.VERIFIED,
        source_urls=["https://example.test/evidence"],
    )

    response = validate_evidence(build_contract(EvidenceMode.EMPIRICAL, [claim]))

    assert response.status is ToolStatus.SUCCESS
    assert "verified" in response.summary.lower()


def test_problem_validator_preserves_proposed_state() -> None:
    contract = build_contract(EvidenceMode.TEACHING_RECONSTRUCTION, [])

    response = validate_problem_contract(contract)

    assert response.status is ToolStatus.SUCCESS
    assert response.details["state"] == "proposed"
    assert response.details["evidence_mode"] == "teaching_reconstruction"
    assert contract.state is ArtifactState.PROPOSED
