from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import BeforeValidator, Field, model_validator

from .common import ArtifactState, ContractModel, FrozenDict, FrozenList, NonEmptyStr

_RESERVED_EXPRESSION_NAMES = {"abs", "max", "min"}


def require_builtin_number(value: object) -> object:
    """Accept only built-in int and float inputs for numeric contract values."""
    if type(value) not in (int, float):
        raise ValueError("numeric contract values must be built-in ints or floats")
    return value


FiniteFloat = Annotated[
    float,
    BeforeValidator(require_builtin_number),
    Field(strict=True, allow_inf_nan=False),
]


class StockSpec(ContractModel):
    name: NonEmptyStr
    unit: NonEmptyStr
    initial_value: FiniteFloat


class AuxiliarySpec(ContractModel):
    name: NonEmptyStr
    expression: NonEmptyStr
    unit: NonEmptyStr


class FlowSpec(ContractModel):
    name: NonEmptyStr
    expression: NonEmptyStr
    source: NonEmptyStr | None = None
    target: NonEmptyStr | None = None
    unit: NonEmptyStr = "units/month"

    @model_validator(mode="after")
    def validate_endpoint(self) -> Self:
        if self.source is None and self.target is None:
            raise ValueError("flow requires a source or target endpoint")
        return self


class ModelSpec(ContractModel):
    model_id: NonEmptyStr
    capability: NonEmptyStr
    time_unit: NonEmptyStr
    time_step: FiniteFloat = Field(gt=0)
    parameters: FrozenDict[NonEmptyStr, FiniteFloat] = Field(default_factory=FrozenDict)
    stocks: FrozenList[StockSpec] = Field(min_length=1)
    auxiliaries: FrozenList[AuxiliarySpec] = Field(default_factory=FrozenList)
    flows: FrozenList[FlowSpec] = Field(default_factory=FrozenList)

    @model_validator(mode="after")
    def validate_variable_names(self) -> Self:
        names: set[str] = set()
        duplicates: set[str] = set()
        for component in (*self.stocks, *self.auxiliaries, *self.flows):
            if component.name in names:
                duplicates.add(component.name)
            names.add(component.name)
        if duplicates:
            duplicate_names = ", ".join(sorted(duplicates))
            raise ValueError(f"model contains duplicate variable names: {duplicate_names}")
        parameter_collisions = set(self.parameters) & names
        if parameter_collisions:
            collision_names = ", ".join(sorted(parameter_collisions))
            raise ValueError(
                f"parameter names cannot shadow model variables: {collision_names}"
            )
        reserved_names = (names | set(self.parameters)) & _RESERVED_EXPRESSION_NAMES
        if reserved_names:
            reserved_name_list = ", ".join(sorted(reserved_names))
            raise ValueError(
                f"model names cannot use reserved expression names: {reserved_name_list}"
            )
        return self


class ExperimentSpec(ContractModel):
    experiment_id: NonEmptyStr
    model_id: NonEmptyStr
    horizon: FiniteFloat = Field(gt=0)
    parameter_overrides: FrozenDict[NonEmptyStr, FiniteFloat] = Field(default_factory=FrozenDict)


class PolicyProposal(ContractModel):
    proposal_id: NonEmptyStr
    model_id: NonEmptyStr
    objective: NonEmptyStr
    constraints: FrozenList[NonEmptyStr] = Field(min_length=1)
    proposed_changes: FrozenDict[NonEmptyStr, FiniteFloat] = Field(default_factory=FrozenDict)
    state: ArtifactState = ArtifactState.PROPOSED
    external_execution_requested: Literal[False] = False


class ApprovalRecord(ContractModel):
    artifact_id: NonEmptyStr
    reviewer: NonEmptyStr
    decision: Literal["approved", "rejected", "superseded"]
    rationale: NonEmptyStr
    rollback_condition: NonEmptyStr
    model_hash: NonEmptyStr
    input_hash: NonEmptyStr
    tool_version: NonEmptyStr
    test_status: Literal["passed", "failed"]

    @model_validator(mode="after")
    def validate_approved_test_status(self) -> Self:
        if self.decision == "approved" and self.test_status != "passed":
            raise ValueError("approved decisions require a passed test status")
        return self
