import json
from pathlib import Path

import pytest
from pydantic import BaseModel, Field, ValidationError

from stai.contracts import (
    ArtifactState,
    ClaimStatus,
    EvidenceClaim,
    EvidenceMode,
    ProblemContract,
    ToolError,
    ToolResponse,
    ToolStatus,
)
from stai.contracts.io import dump_canonical_json, load_yaml


def problem_payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "artifact_id": "factory-cycle-problem",
        "title": "Factory cycle capacity decision",
        "decision": "Choose a production policy for the next quarter.",
        "decision_owner": "Factory operations director",
        "time_horizon": "One quarter",
        "reference_behavior": "Work in process rises when demand exceeds capacity.",
        "authority_boundary": "This contract recommends; humans approve execution.",
        "stakeholders": ["operations", "finance", "customers"],
        "variables": [
            {
                "name": "work_in_process",
                "unit": "units",
                "observation": "Queue length grows during demand spikes.",
            }
        ],
        "capabilities": ["simulate inventory dynamics"],
        "assumptions": ["Demand is measured monthly."],
        "constraints": ["No external execution is permitted."],
        "prohibited_objectives": ["Optimize output at the expense of worker safety."],
        "success_criteria": ["Explain trade-offs to the decision owner."],
        "review_requirements": ["A human reviewer must approve any policy."],
        "evidence_mode": EvidenceMode.TEACHING_RECONSTRUCTION,
        "state": ArtifactState.DRAFT,
    }
    payload.update(overrides)
    return payload


def test_teaching_reconstruction_problem_allows_zero_evidence() -> None:
    contract = ProblemContract.model_validate(problem_payload())

    assert contract.evidence_mode is EvidenceMode.TEACHING_RECONSTRUCTION
    assert contract.evidence == []


def test_contract_enum_values_match_the_universal_vocabulary() -> None:
    assert {state.value for state in ArtifactState} == {
        "draft",
        "proposed",
        "verified",
        "approved",
        "superseded",
    }
    assert {status.value for status in ClaimStatus} == {"verified", "unverified", "contested"}
    assert {mode.value for mode in EvidenceMode} == {"empirical", "teaching_reconstruction"}
    assert {status.value for status in ToolStatus} == {"success", "warning", "error"}


def test_empirical_problem_requires_evidence() -> None:
    with pytest.raises(ValidationError, match="evidence"):
        ProblemContract.model_validate(problem_payload(evidence_mode=EvidenceMode.EMPIRICAL))


def test_empirical_problem_accepts_a_claim() -> None:
    contract = ProblemContract.model_validate(
        problem_payload(
            evidence_mode=EvidenceMode.EMPIRICAL,
            evidence=[
                EvidenceClaim(
                    claim_id="wip-observation",
                    statement="Work in process rose during the demand spike.",
                    status=ClaimStatus.VERIFIED,
                )
            ],
        )
    )

    assert len(contract.evidence) == 1


def test_problem_contract_collections_are_deeply_immutable() -> None:
    evidence = EvidenceClaim(
        claim_id="wip-observation",
        statement="Work in process rose during the demand spike.",
        status=ClaimStatus.VERIFIED,
        source_urls=["https://example.com/evidence"],
    )
    contract = ProblemContract.model_validate(problem_payload(evidence=[evidence]))

    assert contract.stakeholders == ["operations", "finance", "customers"]
    assert list(contract.evidence) == [evidence]

    with pytest.raises(TypeError, match="immutable"):
        contract.stakeholders.append("regulator")
    with pytest.raises(TypeError, match="immutable"):
        contract.stakeholders.clear()
    with pytest.raises(TypeError, match="immutable"):
        contract.stakeholders[0] = "regulator"

    with pytest.raises(TypeError, match="immutable"):
        contract.evidence.append(evidence)
    with pytest.raises(TypeError, match="immutable"):
        contract.evidence.clear()
    with pytest.raises(TypeError, match="immutable"):
        contract.evidence[0] = evidence
    with pytest.raises(TypeError, match="immutable"):
        contract.evidence[0].source_urls.append("https://example.com/more-evidence")


def test_problem_contract_rejects_empty_required_lists() -> None:
    with pytest.raises(ValidationError):
        ProblemContract.model_validate(problem_payload(stakeholders=[]))


def test_tool_error_requires_nonempty_safety_details() -> None:
    with pytest.raises(ValidationError):
        ToolError(root_cause="", safe_retry="Correct the input and retry.", stop_condition="Stop.")


def test_error_tool_response_requires_a_tool_error() -> None:
    with pytest.raises(ValidationError, match="ToolError"):
        ToolResponse(status=ToolStatus.ERROR, summary="The model could not be loaded.")


def test_error_tool_response_accepts_a_complete_tool_error() -> None:
    response = ToolResponse(
        status=ToolStatus.ERROR,
        summary="The model could not be loaded.",
        error=ToolError(
            root_cause="The model file is malformed.",
            safe_retry="Correct the model file and retry validation.",
            stop_condition="Stop after the second malformed input.",
        ),
    )

    assert response.error is not None


def test_non_error_tool_response_rejects_a_tool_error() -> None:
    error = ToolError(
        root_cause="Malformed model input.",
        safe_retry="Correct the input and retry.",
        stop_condition="Stop after two failed corrections.",
    )

    with pytest.raises(ValidationError, match="non-error"):
        ToolResponse(status=ToolStatus.SUCCESS, summary="Completed.", error=error)


def test_tool_response_defaults_are_independent() -> None:
    first = ToolResponse(status=ToolStatus.SUCCESS, summary="Completed.")
    second = ToolResponse(status=ToolStatus.WARNING, summary="Completed with warnings.")

    assert first.next_actions is not second.next_actions
    assert first.artifacts is not second.artifacts
    assert first.details is not second.details
    assert second.next_actions == []
    assert second.artifacts == []
    assert second.details == {}


def test_tool_response_collections_are_deeply_immutable() -> None:
    response = ToolResponse(
        status=ToolStatus.SUCCESS,
        summary="Completed.",
        next_actions=["Review the warning."],
        artifacts=["report.json"],
        details={
            "queue": ["initial"],
            "metadata": {"owner": "operations", "stages": ["draft"]},
        },
    )

    assert response.next_actions == ["Review the warning."]
    assert list(response.artifacts) == ["report.json"]
    assert response.details == {
        "queue": ["initial"],
        "metadata": {"owner": "operations", "stages": ["draft"]},
    }

    with pytest.raises(TypeError, match="immutable"):
        response.next_actions.append("Escalate the warning.")
    with pytest.raises(TypeError, match="immutable"):
        response.next_actions.clear()
    with pytest.raises(TypeError, match="immutable"):
        response.next_actions[0] = "Escalate the warning."

    with pytest.raises(TypeError, match="immutable"):
        response.artifacts.append("revised-report.json")
    with pytest.raises(TypeError, match="immutable"):
        response.artifacts.clear()
    with pytest.raises(TypeError, match="immutable"):
        response.artifacts[0] = "revised-report.json"

    with pytest.raises(TypeError, match="immutable"):
        response.details["attempts"] = 1
    with pytest.raises(TypeError, match="immutable"):
        del response.details["queue"]
    with pytest.raises(TypeError, match="immutable"):
        response.details.update({"attempts": 1})
    with pytest.raises(TypeError, match="immutable"):
        response.details.clear()
    with pytest.raises(TypeError, match="immutable"):
        response.details["queue"].append("second")
    with pytest.raises(TypeError, match="immutable"):
        response.details["metadata"]["owner"] = "finance"
    with pytest.raises(TypeError, match="immutable"):
        response.details["metadata"]["stages"].clear()

    with pytest.raises(TypeError):
        list.clear(response.next_actions)
    with pytest.raises(TypeError):
        dict.__setitem__(response.details, "attempts", 1)

    assert response.next_actions.copy() is response.next_actions
    assert response.details.copy() is response.details


@pytest.mark.parametrize("value", [bytearray(b"unsafe"), object()])
def test_tool_response_rejects_mutable_or_non_json_detail_values(value: object) -> None:
    with pytest.raises(ValidationError):
        ToolResponse(
            status=ToolStatus.SUCCESS,
            summary="Completed.",
            details={"unsafe": value},
        )


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_tool_response_rejects_nonfinite_detail_values_at_any_depth(value: float) -> None:
    for details in (
        {"metric": value},
        {"metrics": [{"value": value}]},
    ):
        with pytest.raises(ValidationError, match="non-finite"):
            ToolResponse(
                status=ToolStatus.SUCCESS,
                summary="Completed.",
                details=details,
            )


class AliasedPayload(BaseModel):
    artifact_id: str = Field(alias="artifactId")
    optional_note: str | None = None


class NonFinitePayload(BaseModel):
    value: float


def test_tool_response_assignment_is_frozen_and_preserves_error_dependency() -> None:
    response = ToolResponse(status=ToolStatus.SUCCESS, summary="Completed.")

    with pytest.raises(ValidationError) as error:
        response.status = ToolStatus.ERROR

    assert error.value.errors()[0]["type"] == "frozen_instance"
    assert error.value.errors()[0]["loc"] == ("status",)
    assert response.status is ToolStatus.SUCCESS

    with pytest.raises(ValidationError) as valid_assignment_error:
        response.summary = "Completed after a review."

    assert valid_assignment_error.value.errors()[0]["type"] == "frozen_instance"
    assert valid_assignment_error.value.errors()[0]["loc"] == ("summary",)
    assert response.summary == "Completed."


def test_yaml_mapping_validates_a_contract_and_canonical_json_omits_none(tmp_path: Path) -> None:
    path = tmp_path / "claim.yaml"
    path.write_text(
        "claim_id: capacity-observation\n"
        "statement: Capacity was stable in the observed period.\n"
        "status: verified\n",
        encoding="utf-8",
    )

    claim = load_yaml(path, EvidenceClaim)
    encoded = dump_canonical_json(AliasedPayload(artifactId="factory-cycle-problem"))

    assert claim.status is ClaimStatus.VERIFIED
    assert json.loads(encoded) == {"artifactId": "factory-cycle-problem"}


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_canonical_json_rejects_nonfinite_floats(value: float) -> None:
    with pytest.raises(ValueError, match="non-finite"):
        dump_canonical_json(NonFinitePayload(value=value))


def test_yaml_loading_rejects_non_mapping_payloads(tmp_path: Path) -> None:
    path = tmp_path / "claims.yaml"
    path.write_text("- one\n- two\n", encoding="utf-8")

    with pytest.raises(ValueError, match="mapping"):
        load_yaml(path, EvidenceClaim)
