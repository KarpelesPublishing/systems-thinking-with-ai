"""An approved-function registry: what a model may call, and on what terms.

Chapter 13 refused everything outside a whitelist. A whitelist of names is not
enough once functions carry units, have domains they are undefined outside, and
differ in whether two calls with the same arguments return the same answer.
"""

import math
from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class ApprovedFunction:
    """One callable, with everything a reviewer needs to judge it."""

    name: str
    arity: int
    implementation: Callable[..., float]
    domain: str            # human-readable statement of where it is defined
    unit_rule: str         # how the result's unit follows from the arguments'
    deterministic: bool
    guard: Callable[..., None] | None = None
    added_in: str = "1.0.0"
    approved_by: str = ""   # the person who accepted it; no AI role may fill this

    def call(self, *args: float) -> float:
        if len(args) != self.arity:
            raise ValueError(f"{self.name} takes {self.arity} argument(s), got {len(args)}")
        if self.guard is not None:
            self.guard(*args)
        return self.implementation(*args)


def _positive(x: float) -> None:
    if x <= 0:
        raise ValueError("argument must be positive")


def _non_negative(x: float) -> None:
    if x < 0:
        raise ValueError("argument must be non-negative")


class Registry:
    """The set of functions a model is permitted to call, with a version of its own."""

    def __init__(self, version: str = "1.0.0") -> None:
        self.version = version
        self._functions: dict[str, ApprovedFunction] = {}

    def add(self, function: ApprovedFunction) -> None:
        if function.name in self._functions:
            raise ValueError(f"'{function.name}' is already registered")
        self._functions[function.name] = function

    def get(self, name: str) -> ApprovedFunction:
        if name not in self._functions:
            raise ValueError(
                f"'{name}' is not in registry {self.version}. A model may only call approved "
                f"functions. Approved: {sorted(self._functions)}"
            )
        return self._functions[name]

    def call(self, name: str, *args: float) -> float:
        return self.get(name).call(*args)

    def names(self) -> list[str]:
        return sorted(self._functions)

    def nondeterministic(self) -> list[str]:
        return sorted(n for n, f in self._functions.items() if not f.deterministic)


def evaluate_with(registry: Registry, text: str, values: dict[str, float]) -> float:
    """Evaluate an expression against this registry rather than the default table.

    This is the join Chapter 13 left open. The evaluator decides what syntax is
    permitted; the registry decides what functions are, and who approved each one.
    """
    from chapters.chapter_13_expressions.code.expressions import evaluate

    return evaluate(text, values, callable_table(registry))


def callable_table(registry: Registry) -> dict[str, Callable[..., float]]:
    """The registry as the table Chapter 13's evaluator calls.

    Chapter 13 shipped its own list of permitted functions, which was the right
    thing to teach first and the wrong thing to keep: it means a model calls what
    an import decided rather than what a person approved. Passing this table in
    routes every call through `ApprovedFunction.call`, so the arity check and the
    domain guard run on the way through.
    """
    return {name: registry.get(name).call for name in registry.names()}


def standard_registry() -> Registry:
    """The functions this book's models are permitted to use."""
    registry = Registry("1.0.0")
    for spec in (
        ApprovedFunction("min", 2, min, "all reals", "both arguments share a unit", True,
                         approved_by="modeling lead"),
        ApprovedFunction("max", 2, max, "all reals", "both arguments share a unit", True,
                         approved_by="modeling lead"),
        ApprovedFunction("abs", 1, abs, "all reals", "same unit as the argument", True,
                         approved_by="modeling lead"),
        ApprovedFunction("sqrt", 1, math.sqrt, "x >= 0", "half the argument's unit exponent",
                         True, _non_negative, approved_by="modeling lead"),
        ApprovedFunction("log", 1, math.log, "x > 0", "argument must be dimensionless",
                         True, _positive, approved_by="modeling lead"),
        ApprovedFunction("exp", 1, math.exp, "all reals", "argument must be dimensionless", True,
                         approved_by="modeling lead"),
    ):
        registry.add(spec)
    return registry


def review_request(function: ApprovedFunction) -> list[str]:
    """What a human has to settle before a proposed function is approved."""
    questions = [
        f"Unit rule: {function.unit_rule}. Does it hold for every model that would call it?",
        f"Domain: {function.domain}. What does the model do when an argument falls outside it?",
    ]
    if not function.deterministic:
        questions.append(
            "This function is not deterministic. Which seeded stream does it draw from, and "
            "is that stream recorded in the run settings?"
        )
    if function.guard is None and "all reals" not in function.domain:
        questions.append("The domain is restricted and no guard was supplied.")
    return questions
