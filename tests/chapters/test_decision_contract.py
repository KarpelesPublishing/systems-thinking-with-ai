import pytest

from chapters.chapter_07_decision_contract.code.contract import (
    DecisionContract,
    Quantity,
    is_ready,
    missing_pieces,
    unit_conflicts,
)


def complete_contract() -> DecisionContract:
    return DecisionContract(
        decision="whether to raise the intake cap on new accounts next quarter",
        decider="head of service operations",
        horizon_length=6,
        horizon_unit="quarter",
        outcomes=[Quantity("customer churn", "customers/quarter", "observed")],
        levers=[Quantity("intake cap", "accounts/week", "observed")],
        inside_boundary=["intake", "workforce", "service quality"],
        outside_boundary=["competitor pricing", "regulatory change"],
        prohibited_actions=["reduce contracted service levels"],
        affected_parties=["front-line staff", "existing customers"],
    )


def test_a_complete_contract_is_ready() -> None:
    assert is_ready(complete_contract())
    assert missing_pieces(complete_contract()) == []


def test_a_contract_with_no_excluded_boundary_is_not_ready() -> None:
    """A boundary that excludes nothing was never drawn."""
    contract = complete_contract()
    contract.outside_boundary = []
    assert not is_ready(contract)
    assert any("excluded" in gap for gap in missing_pieces(contract))


def test_a_contract_with_no_lever_is_not_ready() -> None:
    contract = complete_contract()
    contract.levers = []
    assert any("lever" in gap for gap in missing_pieces(contract))


def test_a_contract_that_names_nobody_affected_is_not_ready() -> None:
    contract = complete_contract()
    contract.affected_parties = []
    assert any("affected parties" in gap for gap in missing_pieces(contract))


def test_a_topic_is_not_a_decision() -> None:
    with pytest.raises(ValueError):
        DecisionContract(decision="   ", decider="ops", horizon_length=4, horizon_unit="quarter")
    with pytest.raises(ValueError):
        DecisionContract(
            decision="whether to hire", decider="", horizon_length=4, horizon_unit="quarter"
        )


def test_horizons_need_a_real_unit_and_a_real_length() -> None:
    with pytest.raises(ValueError):
        DecisionContract(decision="d", decider="p", horizon_length=4, horizon_unit="fortnight")
    with pytest.raises(ValueError):
        DecisionContract(decision="d", decider="p", horizon_length=0, horizon_unit="week")


def test_a_quantity_without_a_unit_is_rejected() -> None:
    with pytest.raises(ValueError):
        Quantity("capacity", "", "observed")
    with pytest.raises(ValueError):
        Quantity("capacity", "seats/week", "vibes")


def test_the_same_name_with_two_units_is_reported() -> None:
    contract = complete_contract()
    contract.levers.append(Quantity("customer churn", "percent", "inferred"))
    assert unit_conflicts(contract) == ["customer churn: customers/quarter vs percent"]


def test_the_contract_uses_the_books_four_evidence_levels() -> None:
    """One taxonomy across the whole book. 'estimated' is not one of them."""
    from chapters.chapter_07_decision_contract.code.contract import EVIDENCE_LEVELS
    assert EVIDENCE_LEVELS == ("observed", "inferred", "assumed", "proposed")
    for level in EVIDENCE_LEVELS:
        assert Quantity("churn", "customers/quarter", level).evidence == level
    with pytest.raises(ValueError):
        Quantity("churn", "customers/quarter", "estimated")
