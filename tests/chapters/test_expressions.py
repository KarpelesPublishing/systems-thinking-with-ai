import pytest

from chapters.chapter_13_expressions.code.expressions import (
    UnsafeExpression,
    evaluate,
    parse,
    variables,
)


def test_ordinary_model_algebra_evaluates() -> None:
    assert evaluate("max(0, demand - capacity) / adjustment",
                    {"demand": 120.0, "capacity": 100.0, "adjustment": 4.0}) == 5.0
    assert evaluate("backlog / delay", {"backlog": 40.0, "delay": 4.0}) == 10.0


def test_conditionals_and_comparisons_are_permitted() -> None:
    assert evaluate("inventory if inventory > 0 else 0", {"inventory": -5.0}) == 0


def test_variables_are_the_models_dependency_edges() -> None:
    assert variables("backlog / production_delay + safety") == {
        "backlog", "production_delay", "safety"
    }
    assert variables("max(0, a)") == {"a"}


@pytest.mark.parametrize("hostile", [
    '__import__("os").system("ls")',
    'open("/etc/passwd").read()',
    "x.__class__.__bases__",
    "[i for i in range(9)]",
    "(lambda: 1)()",
    "globals()",
])
def test_hostile_expressions_are_refused(hostile: str) -> None:
    with pytest.raises(UnsafeExpression):
        parse(hostile)


def test_unlisted_functions_are_refused_even_when_harmless() -> None:
    with pytest.raises(UnsafeExpression):
        parse("round(3.7)")


def test_string_constants_are_refused() -> None:
    with pytest.raises(UnsafeExpression):
        parse("'a' if x else 'b'")


def test_a_missing_value_is_an_error_not_a_zero() -> None:
    with pytest.raises(ValueError):
        evaluate("a + b", {"a": 1.0})


def test_malformed_and_empty_expressions_are_refused() -> None:
    with pytest.raises(UnsafeExpression):
        parse("2 +")
    with pytest.raises(UnsafeExpression):
        parse("   ")
