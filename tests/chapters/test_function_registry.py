import pytest

from chapters.chapter_23_registry.code.registry import (
    ApprovedFunction,
    review_request,
    standard_registry,
)


def test_approved_functions_can_be_called() -> None:
    registry = standard_registry()
    assert registry.call("max", 0.0, -5.0) == 0.0
    assert registry.call("sqrt", 9.0) == 3.0


def test_an_unregistered_name_is_refused_with_the_approved_list() -> None:
    with pytest.raises(ValueError) as caught:
        standard_registry().call("system", 1.0)
    assert "not in registry" in str(caught.value)
    assert "sqrt" in str(caught.value)


def test_a_domain_guard_rejects_an_argument_outside_the_domain() -> None:
    """sqrt of a negative is a modelling error, not a complex number."""
    with pytest.raises(ValueError):
        standard_registry().call("sqrt", -1.0)
    with pytest.raises(ValueError):
        standard_registry().call("log", 0.0)


def test_arity_is_enforced() -> None:
    with pytest.raises(ValueError):
        standard_registry().call("max", 1.0)


def test_the_registry_reports_which_functions_are_not_deterministic() -> None:
    registry = standard_registry()
    assert registry.nondeterministic() == []
    registry.add(ApprovedFunction("noise", 1, lambda x: x, "all reals", "same as argument", False))
    assert registry.nondeterministic() == ["noise"]


def test_a_name_cannot_be_registered_twice() -> None:
    registry = standard_registry()
    with pytest.raises(ValueError):
        registry.add(ApprovedFunction("max", 2, max, "all reals", "shared unit", True))


def test_a_review_asks_about_units_domain_and_determinism() -> None:
    proposed = ApprovedFunction("sample", 1, lambda x: x, "x > 0", "same as argument", False)
    questions = review_request(proposed)
    assert any("Unit rule" in q for q in questions)
    assert any("not deterministic" in q for q in questions)
    assert any("no guard was supplied" in q for q in questions)


def test_a_well_specified_function_raises_fewer_questions() -> None:
    clean = ApprovedFunction("double", 1, lambda x: x * 2, "all reals", "same as argument", True)
    assert len(review_request(clean)) == 2


def test_every_standard_function_names_the_person_who_approved_it() -> None:
    """Chapter 23 says the registry answers who approved a function, so it has to."""
    registry = standard_registry()
    for name in registry.names():
        assert registry.get(name).approved_by


def test_the_registry_can_be_the_evaluators_function_table() -> None:
    """Chapter 13's evaluator calls what a person approved, not what a file imported."""
    from chapters.chapter_13_expressions.code.expressions import evaluate
    from chapters.chapter_23_registry.code.registry import callable_table

    table = callable_table(standard_registry())
    assert evaluate("sqrt(x) + max(a, b)", {"x": 9.0, "a": 1.0, "b": 4.0}, table) == 7.0


def test_a_guard_fires_through_the_evaluator() -> None:
    """The reviewed message, not Python's raw one, which is the point of the guard."""
    from chapters.chapter_13_expressions.code.expressions import evaluate
    from chapters.chapter_23_registry.code.registry import callable_table

    table = callable_table(standard_registry())
    with pytest.raises(ValueError, match="non-negative"):
        evaluate("sqrt(x)", {"x": -1.0}, table)


def test_a_function_outside_the_registry_is_refused_by_the_parser() -> None:
    from chapters.chapter_13_expressions.code.expressions import UnsafeExpression, evaluate
    from chapters.chapter_23_registry.code.registry import Registry, callable_table

    thin = Registry("1.0.0")
    thin.add(standard_registry().get("abs"))
    with pytest.raises(UnsafeExpression, match="not an allowed function"):
        evaluate("sqrt(x)", {"x": 4.0}, callable_table(thin))


def test_evaluate_with_joins_the_registry_to_the_evaluator() -> None:
    from chapters.chapter_23_registry.code.registry import evaluate_with

    registry = standard_registry()
    assert evaluate_with(registry, "log(exp(x))", {"x": 2.0}) == pytest.approx(2.0)
    with pytest.raises(ValueError, match="positive"):
        evaluate_with(registry, "log(x)", {"x": 0.0})
