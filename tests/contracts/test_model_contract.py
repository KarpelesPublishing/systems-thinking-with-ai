import json
from copy import deepcopy
from fractions import Fraction

import pytest
from pydantic import ValidationError

from stai.contracts import (
    ApprovalRecord,
    ArtifactState,
    AuxiliarySpec,
    ExperimentSpec,
    FlowSpec,
    ModelSpec,
    PolicyProposal,
    StockSpec,
    dump_canonical_json,
)


def stock(name: str = "work_in_process") -> StockSpec:
    return StockSpec(name=name, unit="units", initial_value=100.0)


def test_flow_requires_a_source_or_target_endpoint() -> None:
    with pytest.raises(ValidationError, match="source or target"):
        FlowSpec(name="production", expression="capacity * utilization")


def test_model_rejects_duplicate_variable_names_across_components() -> None:
    with pytest.raises(ValidationError, match="duplicate variable names"):
        ModelSpec(
            model_id="factory-cycle",
            capability="Explore factory throughput dynamics.",
            time_unit="month",
            time_step=1.0,
            stocks=[stock()],
            auxiliaries=[
                AuxiliarySpec(
                    name="work_in_process",
                    expression="stock / 2",
                    unit="units",
                )
            ],
        )


def test_model_rejects_non_numeric_parameters() -> None:
    with pytest.raises(ValidationError, match="numeric"):
        ModelSpec(
            model_id="factory-cycle",
            capability="Explore factory throughput dynamics.",
            time_unit="month",
            time_step=1.0,
            parameters={"capacity": "high"},
            stocks=[stock()],
        )


def test_experiment_accepts_numeric_parameter_overrides() -> None:
    experiment = ExperimentSpec(
        experiment_id="capacity-sensitivity",
        model_id="factory-cycle",
        horizon=12,
        parameter_overrides={"capacity": 240, "utilization": 0.85},
    )

    assert experiment.parameter_overrides == {"capacity": 240.0, "utilization": 0.85}


def test_experiment_rejects_non_numeric_parameter_overrides() -> None:
    with pytest.raises(ValidationError, match="numeric"):
        ExperimentSpec(
            experiment_id="capacity-sensitivity",
            model_id="factory-cycle",
            horizon=12,
            parameter_overrides={"capacity": "high"},
        )


def test_policy_proposal_defaults_to_non_executable_and_rejects_execution_requests() -> None:
    proposal = PolicyProposal(
        proposal_id="add-second-shift",
        model_id="factory-cycle",
        objective="Reduce work in process without increasing safety risk.",
        constraints=["Human approval is required before execution."],
    )

    assert proposal.state is ArtifactState.PROPOSED
    assert proposal.external_execution_requested is False

    with pytest.raises(ValidationError):
        PolicyProposal(
            proposal_id="add-second-shift",
            model_id="factory-cycle",
            objective="Reduce work in process without increasing safety risk.",
            constraints=["Human approval is required before execution."],
            external_execution_requested=True,
        )


def test_approval_record_cannot_approve_failed_tests() -> None:
    with pytest.raises(ValidationError, match="approved.*passed"):
        ApprovalRecord(
            artifact_id="factory-cycle-model",
            reviewer="Operations safety reviewer",
            decision="approved",
            rationale="The proposal is safe to proceed to a human review meeting.",
            rollback_condition="Stop if safety metrics worsen.",
            model_hash="model-sha256",
            input_hash="input-sha256",
            tool_version="0.1.0",
            test_status="failed",
        )


def test_approval_record_accepts_approved_passing_tests() -> None:
    record = ApprovalRecord(
        artifact_id="factory-cycle-model",
        reviewer="Operations safety reviewer",
        decision="approved",
        rationale="The proposal passed the review gate.",
        rollback_condition="Stop if safety metrics worsen.",
        model_hash="model-sha256",
        input_hash="input-sha256",
        tool_version="0.1.0",
        test_status="passed",
    )

    assert record.decision == "approved"


def test_model_requires_a_stock_and_positive_time_step() -> None:
    with pytest.raises(ValidationError):
        ModelSpec(
            model_id="no-stocks",
            capability="stock-flow",
            time_unit="month",
            time_step=1.0,
            stocks=[],
        )

    with pytest.raises(ValidationError):
        ModelSpec(
            model_id="invalid-step",
            capability="stock-flow",
            time_unit="month",
            time_step=0,
            stocks=[stock()],
        )


@pytest.mark.parametrize("time_step", [True, "1", float("nan"), float("inf"), float("-inf")])
def test_model_rejects_non_strict_or_nonfinite_time_steps(time_step: object) -> None:
    with pytest.raises(ValidationError):
        ModelSpec(
            model_id="invalid-step",
            capability="stock-flow",
            time_unit="month",
            time_step=time_step,
            stocks=[stock()],
        )


@pytest.mark.parametrize("time_step", [1, 1.5])
def test_model_accepts_positive_int_and_float_time_steps(time_step: float) -> None:
    model = ModelSpec(
        model_id="valid-step",
        capability="stock-flow",
        time_unit="month",
        time_step=time_step,
        stocks=[stock()],
    )

    assert model.time_step == time_step


@pytest.mark.parametrize("horizon", [True, "12", float("nan"), float("inf"), float("-inf")])
def test_experiment_rejects_non_strict_or_nonfinite_horizons(horizon: object) -> None:
    with pytest.raises(ValidationError):
        ExperimentSpec(
            experiment_id="invalid-horizon",
            model_id="factory-cycle",
            horizon=horizon,
        )


@pytest.mark.parametrize("horizon", [12, 12.5])
def test_experiment_accepts_positive_int_and_float_horizons(horizon: float) -> None:
    experiment = ExperimentSpec(
        experiment_id="valid-horizon",
        model_id="factory-cycle",
        horizon=horizon,
    )

    assert experiment.horizon == horizon


@pytest.mark.parametrize("invalid_value", [True, "1", float("nan"), float("inf")])
def test_other_finite_numeric_contract_fields_are_strict(invalid_value: object) -> None:
    with pytest.raises(ValidationError):
        StockSpec(name="inventory", unit="units", initial_value=invalid_value)

    with pytest.raises(ValidationError):
        ModelSpec(
            model_id="invalid-parameter",
            capability="stock-flow",
            time_unit="month",
            time_step=1,
            parameters={"capacity": invalid_value},
            stocks=[stock()],
        )

    with pytest.raises(ValidationError):
        ExperimentSpec(
            experiment_id="invalid-override",
            model_id="factory-cycle",
            horizon=12,
            parameter_overrides={"capacity": invalid_value},
        )

    with pytest.raises(ValidationError):
        PolicyProposal(
            proposal_id="invalid-change",
            model_id="factory-cycle",
            objective="Keep a numeric policy adjustment.",
            constraints=["Human approval is required before execution."],
            proposed_changes={"capacity": invalid_value},
        )


@pytest.mark.parametrize("attempted_value", [0, True, 2.5])
def test_model_assignment_is_frozen_and_preserves_time_step(attempted_value: object) -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        stocks=[stock()],
    )

    with pytest.raises(ValidationError) as error:
        model.time_step = attempted_value

    assert error.value.errors()[0]["type"] == "frozen_instance"
    assert error.value.errors()[0]["loc"] == ("time_step",)
    assert model.time_step == 1.0


@pytest.mark.parametrize(
    ("attribute", "attempted_value"),
    [("initial_value", True), ("name", ""), ("initial_value", 125)],
)
def test_nested_stock_assignment_is_frozen_and_preserves_valid_state(
    attribute: str,
    attempted_value: object,
) -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        stocks=[stock()],
    )
    nested_stock = model.stocks[0]

    with pytest.raises(ValidationError) as error:
        setattr(nested_stock, attribute, attempted_value)

    assert error.value.errors()[0]["type"] == "frozen_instance"
    assert error.value.errors()[0]["loc"] == (attribute,)
    assert nested_stock.initial_value == 100.0
    assert nested_stock.name == "work_in_process"


def test_policy_proposal_assignment_preserves_external_execution_guard() -> None:
    proposal = PolicyProposal(
        proposal_id="add-second-shift",
        model_id="factory-cycle",
        objective="Reduce work in process without increasing safety risk.",
        constraints=["Human approval is required before execution."],
    )

    with pytest.raises(ValidationError) as error:
        proposal.external_execution_requested = True

    assert error.value.errors()[0]["type"] == "frozen_instance"
    assert error.value.errors()[0]["loc"] == ("external_execution_requested",)
    assert proposal.external_execution_requested is False

    with pytest.raises(ValidationError) as valid_assignment_error:
        proposal.objective = "Evaluate a revised capacity policy."

    assert valid_assignment_error.value.errors()[0]["type"] == "frozen_instance"
    assert valid_assignment_error.value.errors()[0]["loc"] == ("objective",)
    assert proposal.objective == "Reduce work in process without increasing safety risk."


@pytest.mark.parametrize("value", [1, 1.5])
def test_numeric_maps_accept_builtin_ints_and_floats(value: int | float) -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        parameters={"capacity": value},
        stocks=[stock()],
    )
    experiment = ExperimentSpec(
        experiment_id="capacity-sensitivity",
        model_id="factory-cycle",
        horizon=12,
        parameter_overrides={"capacity": value},
    )
    proposal = PolicyProposal(
        proposal_id="capacity-change",
        model_id="factory-cycle",
        objective="Evaluate a capacity adjustment.",
        constraints=["Human approval is required before execution."],
        proposed_changes={"capacity": value},
    )

    assert model.parameters == {"capacity": float(value)}
    assert experiment.parameter_overrides == {"capacity": float(value)}
    assert proposal.proposed_changes == {"capacity": float(value)}


@pytest.mark.parametrize(
    "invalid_value",
    [True, "1", Fraction(1, 2), float("nan"), float("inf"), float("-inf")],
)
def test_numeric_maps_reject_identical_invalid_values_at_mapping_entries(
    invalid_value: object,
) -> None:
    cases = (
        (
            "parameters",
            lambda: ModelSpec(
                model_id="invalid-parameter",
                capability="stock-flow",
                time_unit="month",
                time_step=1,
                parameters={"capacity": invalid_value},
                stocks=[stock()],
            ),
        ),
        (
            "parameter_overrides",
            lambda: ExperimentSpec(
                experiment_id="invalid-override",
                model_id="factory-cycle",
                horizon=12,
                parameter_overrides={"capacity": invalid_value},
            ),
        ),
        (
            "proposed_changes",
            lambda: PolicyProposal(
                proposal_id="invalid-change",
                model_id="factory-cycle",
                objective="Keep a numeric policy adjustment.",
                constraints=["Human approval is required before execution."],
                proposed_changes={"capacity": invalid_value},
            ),
        ),
    )

    for field_name, construct in cases:
        with pytest.raises(ValidationError) as error:
            construct()

        assert error.value.errors()[0]["loc"] == (field_name, "capacity")


def test_model_collections_are_deeply_immutable_and_remain_serializable() -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        parameters={"capacity": 240},
        stocks=[stock()],
    )

    assert model.stocks == [stock()]
    assert list(model.stocks) == [stock()]
    assert model.parameters == {"capacity": 240.0}
    assert dict(model.parameters) == {"capacity": 240.0}

    with pytest.raises(TypeError, match="immutable"):
        model.stocks.append(stock("finished_goods"))
    with pytest.raises(TypeError, match="immutable"):
        model.stocks.clear()
    with pytest.raises(TypeError, match="immutable"):
        model.stocks[0] = stock("finished_goods")

    with pytest.raises(TypeError, match="immutable"):
        model.parameters["capacity"] = 300
    with pytest.raises(TypeError, match="immutable"):
        del model.parameters["capacity"]
    with pytest.raises(TypeError, match="immutable"):
        model.parameters.update({"capacity": 300})
    with pytest.raises(TypeError, match="immutable"):
        model.parameters.clear()

    payload = model.model_dump()

    assert payload["stocks"] == [
        {"name": "work_in_process", "unit": "units", "initial_value": 100.0}
    ]
    assert payload["parameters"] == {"capacity": 240.0}
    assert json.loads(dump_canonical_json(model))["parameters"] == {"capacity": 240.0}


def test_contract_model_copies_preserve_deeply_immutable_collections() -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        parameters={"capacity": 240},
        stocks=[stock()],
    )

    updated_copy = model.model_copy(update={"parameters": {"capacity": 300}})

    assert updated_copy.parameters == {"capacity": 300}
    with pytest.raises(TypeError, match="immutable"):
        updated_copy.parameters["capacity"] = 1

    try:
        deep_copy = deepcopy(model)
    except TypeError as error:
        pytest.fail(f"deep copy must preserve immutable contract containers: {error}")

    assert deep_copy == model
    with pytest.raises(TypeError, match="immutable"):
        deep_copy.parameters.clear()


def test_contract_collections_reject_unbound_builtin_mutators_and_keep_safe_copies() -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        parameters={"capacity": 240},
        stocks=[stock()],
    )

    with pytest.raises(TypeError):
        list.clear(model.stocks)
    with pytest.raises(TypeError):
        list.append(model.stocks, stock("finished_goods"))
    with pytest.raises(TypeError):
        dict.__setitem__(model.parameters, "capacity", "not-a-number")
    with pytest.raises(TypeError):
        dict.update(model.parameters, {"capacity": "not-a-number"})

    assert model.stocks == [stock()]
    assert model.parameters == {"capacity": 240.0}
    assert model.stocks.copy() is model.stocks
    assert model.parameters.copy() is model.parameters


def test_contract_model_copy_validates_updates_before_freezing() -> None:
    model = ModelSpec(
        model_id="factory-cycle",
        capability="Explore factory throughput dynamics.",
        time_unit="month",
        time_step=1,
        parameters={"capacity": 240},
        stocks=[stock()],
    )

    for update in (
        {"time_step": 0},
        {"stocks": []},
        {"parameters": {"capacity": "not-a-number"}},
    ):
        with pytest.raises(ValidationError):
            model.model_copy(update=update)

    updated_copy = model.model_copy(update={"parameters": {"capacity": 300}})

    assert updated_copy.parameters == {"capacity": 300.0}
    with pytest.raises(TypeError):
        dict.__setitem__(updated_copy.parameters, "capacity", 1)


def test_policy_proposed_changes_are_deeply_immutable() -> None:
    proposal = PolicyProposal(
        proposal_id="capacity-change",
        model_id="factory-cycle",
        objective="Evaluate a capacity adjustment.",
        constraints=["Human approval is required before execution."],
        proposed_changes={"capacity": 240},
    )

    assert proposal.proposed_changes == {"capacity": 240.0}

    with pytest.raises(TypeError, match="immutable"):
        proposal.proposed_changes["capacity"] = 300
    with pytest.raises(TypeError, match="immutable"):
        del proposal.proposed_changes["capacity"]
    with pytest.raises(TypeError, match="immutable"):
        proposal.proposed_changes.update({"capacity": 300})
    with pytest.raises(TypeError, match="immutable"):
        proposal.proposed_changes.clear()
