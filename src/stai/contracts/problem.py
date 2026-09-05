from __future__ import annotations

from typing import Self

from pydantic import Field, model_validator

from .common import (
    ArtifactState,
    ClaimStatus,
    ContractModel,
    EvidenceMode,
    FrozenList,
    NonEmptyStr,
)


class VariableSpec(ContractModel):
    name: NonEmptyStr
    unit: NonEmptyStr
    observation: str | None = None
    assumption: str | None = None


class EvidenceClaim(ContractModel):
    claim_id: NonEmptyStr
    statement: NonEmptyStr
    status: ClaimStatus
    source_urls: FrozenList[str] = Field(default_factory=FrozenList)


class ProblemContract(ContractModel):
    artifact_id: NonEmptyStr
    title: NonEmptyStr
    decision: NonEmptyStr
    decision_owner: NonEmptyStr
    time_horizon: NonEmptyStr
    reference_behavior: NonEmptyStr
    authority_boundary: NonEmptyStr
    stakeholders: FrozenList[NonEmptyStr] = Field(min_length=1)
    variables: FrozenList[VariableSpec] = Field(min_length=1)
    capabilities: FrozenList[NonEmptyStr] = Field(min_length=1)
    assumptions: FrozenList[NonEmptyStr] = Field(min_length=1)
    constraints: FrozenList[NonEmptyStr] = Field(min_length=1)
    prohibited_objectives: FrozenList[NonEmptyStr] = Field(min_length=1)
    success_criteria: FrozenList[NonEmptyStr] = Field(min_length=1)
    review_requirements: FrozenList[NonEmptyStr] = Field(min_length=1)
    evidence_mode: EvidenceMode
    state: ArtifactState
    evidence: FrozenList[EvidenceClaim] = Field(default_factory=FrozenList)

    @model_validator(mode="after")
    def validate_evidence_mode(self) -> Self:
        if self.evidence_mode is EvidenceMode.EMPIRICAL and not self.evidence:
            raise ValueError("empirical contracts require evidence")
        return self
