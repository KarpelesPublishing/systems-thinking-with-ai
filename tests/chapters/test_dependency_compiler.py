import pytest

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_21_compiler.code.compiler import (
    algebraic_loops,
    declared_versus_inferred,
    diagnostics,
    edges,
    evaluation_order,
    strongly_connected,
)


def factory() -> ModelDocument:
    return ModelDocument("factory", "1.0.0", [
        Variable("inventory", "stock", "units", value=12.0),
        Variable("order_rate", "parameter", "units/week", value=10.0),
        Variable("coverage", "parameter", "week", value=2.0),
        Variable("desired_inventory", "auxiliary", "units", "order_rate * coverage"),
        Variable("gap", "auxiliary", "units", "desired_inventory - inventory"),
        Variable("production", "flow", "units/week", "order_rate + gap / coverage",
                 target="inventory", sign=1),
    ])


def looped() -> ModelDocument:
    return ModelDocument("bad", "0.1.0", [
        Variable("a", "stock", "x", value=1.0),
        Variable("p", "auxiliary", "x", "q + 1"),
        Variable("q", "auxiliary", "x", "p * 2"),
    ])


def test_edges_come_from_the_equations_not_from_a_declaration() -> None:
    assert edges(factory())["gap"] == {"desired_inventory", "inventory"}
    assert edges(factory())["order_rate"] == set()


def test_evaluation_order_puts_every_dependency_first() -> None:
    order = evaluation_order(factory())
    assert order.index("desired_inventory") < order.index("gap")
    assert order.index("gap") < order.index("production")


def test_stocks_are_not_ordered_because_they_are_state() -> None:
    assert "inventory" not in evaluation_order(factory())


def test_an_algebraic_loop_is_found() -> None:
    assert algebraic_loops(looped()) == [["p", "q"]]


def test_feedback_through_a_stock_is_not_an_algebraic_loop() -> None:
    """gap reads inventory, production changes inventory. Legitimate feedback."""
    assert algebraic_loops(factory()) == []


def test_a_model_with_an_algebraic_loop_refuses_to_order() -> None:
    with pytest.raises(ValueError):
        evaluation_order(looped())


def test_diagnostics_explain_the_loop_and_how_to_break_it() -> None:
    message = diagnostics(looped())[0]
    assert "p -> q -> p" in message
    assert "stock" in message


def test_solvable_loop_reports_solver_limit_not_mathematical_impossibility() -> None:
    from chapters.chapter_13_expressions.code.expressions import evaluate

    document = looped()
    solution = {"p": -1.0, "q": -2.0}
    for variable in document.variables:
        if variable.equation:
            assert evaluate(variable.equation, solution) == solution[variable.id]
    message = diagnostics(document)[0]
    assert "no value satisfies" not in message
    assert "simultaneous-equation solver" in message
    with pytest.raises(ValueError, match="algebraic loops"):
        evaluation_order(document)


def test_strongly_connected_groups_mutually_reachable_nodes() -> None:
    groups = strongly_connected({"a": {"b"}, "b": {"a"}, "c": {"a"}})
    assert ["a", "b"] in groups
    assert ["c"] in groups


def test_a_declared_edge_the_equations_do_not_support_is_reported() -> None:
    mismatch = declared_versus_inferred(factory(), {"gap": {"order_rate"}})
    assert "gap" in mismatch


def test_the_declared_versus_inferred_report_is_ordered() -> None:
    """Chapter 21 prints this dict, so its key order cannot depend on hash randomization."""
    report = declared_versus_inferred(factory(), declared={"gap": {"order_rate"}})
    assert list(report) == sorted(report)
