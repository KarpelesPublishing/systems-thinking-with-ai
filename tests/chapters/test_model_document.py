import pytest

from chapters.chapter_20_model_document.code.document import (
    ModelDocument,
    Variable,
    diff,
    validate,
)


def factory(version: str = "1.2.0") -> ModelDocument:
    return ModelDocument(name="factory", version=version, horizon=52, variables=[
        Variable("inventory", "stock", "units", value=12.0),
        Variable("order_rate", "parameter", "units/week", value=10.0),
        Variable("coverage", "parameter", "week", value=2.0),
        Variable("desired_inventory", "auxiliary", "units", "order_rate * coverage"),
        Variable("gap", "auxiliary", "units", "desired_inventory - inventory"),
        Variable("production", "flow", "units/week", "order_rate + gap / coverage",
                 target="inventory", sign=1),
    ])


def test_a_well_formed_document_validates() -> None:
    assert validate(factory()) == []


def test_a_reference_to_an_undefined_variable_is_caught() -> None:
    doc = factory()
    doc.variables.append(
        Variable("shipments", "flow", "units/week", "demand * 2", target="inventory", sign=-1)
    )
    assert any("undefined 'demand'" in p for p in validate(doc))


def test_a_model_with_nothing_that_accumulates_is_reported() -> None:
    doc = ModelDocument("flat", "0.1.0", [
        Variable("a", "parameter", "units", value=1.0),
        Variable("b", "auxiliary", "units", "a * 2"),
    ])
    assert any("no stock" in p for p in validate(doc))


def test_the_hash_tracks_meaning_and_not_the_version_label() -> None:
    """Bumping a version number must not look like a change to the model."""
    assert factory("1.2.0").hash() == factory("9.9.9").hash()


def test_changing_an_equation_changes_the_hash() -> None:
    changed = factory()
    changed.variables[-1] = Variable("production", "flow", "units/week", "order_rate + gap / 4.0",
                             target="inventory", sign=1)
    assert changed.hash() != factory().hash()


def test_the_hash_is_stable_under_reordering() -> None:
    shuffled = factory()
    shuffled.variables.reverse()
    assert shuffled.hash() == factory().hash()


def test_a_diff_reports_change_in_the_models_own_terms() -> None:
    changed = factory()
    changed.variables[-1] = Variable("production", "flow", "units/week", "order_rate + gap / 4.0",
                             target="inventory", sign=1)
    changed.variables.append(
        Variable("scrap", "flow", "units/week", "inventory * 0.01", target="inventory", sign=-1)
    )
    assert diff(factory(), changed) == {
        "added": ["scrap"], "removed": [], "changed": ["production"]
    }


def test_ids_units_and_versions_are_enforced() -> None:
    with pytest.raises(ValueError):
        Variable("Order Rate", "parameter", "units/week", value=1.0)
    with pytest.raises(ValueError):
        Variable("x", "widget", "units", value=1.0)
    with pytest.raises(ValueError):
        Variable("x", "stock", "", value=1.0)
    with pytest.raises(ValueError):
        ModelDocument("m", "1.2", [])


def test_a_stock_needs_a_value_and_an_auxiliary_needs_an_equation() -> None:
    with pytest.raises(ValueError):
        Variable("inventory", "stock", "units")
    with pytest.raises(ValueError):
        Variable("gap", "auxiliary", "units")


def test_duplicate_ids_are_refused() -> None:
    with pytest.raises(ValueError):
        ModelDocument("m", "1.0.0", [
            Variable("a", "stock", "u", value=1.0), Variable("a", "stock", "u", value=2.0),
        ])


def test_a_flow_that_does_not_say_which_stock_it_moves_is_reported() -> None:
    """A flow with no target changes nothing, and the model looks fine until it runs."""
    doc = factory()
    doc.variables[-1] = Variable("production", "flow", "units/week", "order_rate + gap / coverage")
    assert any("does not say which stock" in p for p in validate(doc))


def test_a_flow_targeting_something_that_is_not_a_stock_is_reported() -> None:
    doc = factory()
    doc.variables[-1] = Variable("production", "flow", "units/week", "order_rate + gap / coverage",
                                 target="coverage", sign=1)
    assert any("not a stock" in p for p in validate(doc))


def test_a_stock_nothing_moves_is_reported() -> None:
    doc = factory()
    doc.variables.append(Variable("scrap_pile", "stock", "units", value=0.0))
    assert any("scrap_pile" in p and "no flow" in p for p in validate(doc))


def test_only_a_flow_may_target_a_stock() -> None:
    with pytest.raises(ValueError):
        Variable("gap", "auxiliary", "units", "a - b", target="inventory")
    with pytest.raises(ValueError):
        Variable("f", "flow", "u/w", "1", target="s", sign=0)
