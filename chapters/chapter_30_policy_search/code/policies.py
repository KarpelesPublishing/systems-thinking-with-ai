"""Compare policies across uncertainty, with constraints that can veto a winner."""

import statistics
from dataclasses import dataclass, field

from chapters.chapter_20_model_document.code.document import ModelDocument
from chapters.chapter_29_experiments.code.sensitivity import Uncertainty, metric


@dataclass(frozen=True)
class Policy:
    """A named set of settings, with an owner and whether it can be undone."""

    name: str
    settings: dict[str, float]
    owner: str
    reversible: bool
    note: str = ""

    def __post_init__(self) -> None:
        if not self.settings:
            raise ValueError(f"policy '{self.name}' sets nothing")
        if not self.owner.strip():
            raise ValueError(f"policy '{self.name}' has no owner")


@dataclass(frozen=True)
class Bound:
    """A constraint that a policy must satisfy in every draw, not on average."""

    metric_name: str
    low: float | None = None
    high: float | None = None
    reason: str = ""

    def violated_by(self, value: float) -> str | None:
        if self.low is not None and value < self.low:
            return f"{self.metric_name}={value:.4g} below {self.low} ({self.reason})"
        if self.high is not None and value > self.high:
            return f"{self.metric_name}={value:.4g} above {self.high} ({self.reason})"
        return None


@dataclass
class Evaluation:
    """What a policy did across every draw, including where it failed."""

    policy: str
    values: list[float] = field(default_factory=list)
    violations: list[str] = field(default_factory=list)
    reversible: bool = True

    def mean(self) -> float:
        return statistics.fmean(self.values) if self.values else float("-inf")

    def worst(self) -> float:
        return min(self.values) if self.values else float("-inf")

    def admissible(self) -> bool:
        return not self.violations


def evaluate(document: ModelDocument, policy: Policy, uncertainties: list[Uncertainty],
             objective: str, bounds: list[Bound], draws: int, seed: int) -> Evaluation:
    """Run one policy against a fixed set of uncertainty draws."""
    import random
    rng = random.Random(seed)
    result = Evaluation(policy=policy.name, reversible=policy.reversible)
    for _ in range(draws):
        overrides = {**{u.variable: rng.uniform(u.low, u.high) for u in uncertainties},
                     **policy.settings}
        try:
            value = metric(document, overrides, objective)
        except RuntimeError as exc:
            # A model that refuses to run under a draw has made the strongest
            # possible statement about this policy in that world: it is not
            # viable there. Recording it as a violation keeps the comparison
            # honest, where letting it propagate would lose every other draw.
            message = f"the model could not be run: {exc}"
            if message not in result.violations:
                result.violations.append(message)
            continue
        result.values.append(value)
        for bound in bounds:
            if bound.metric_name != objective:
                continue
            message = bound.violated_by(value)
            if message and message not in result.violations:
                result.violations.append(message)
    return result


def compare(document: ModelDocument, policies: list[Policy], uncertainties: list[Uncertainty],
            objective: str, bounds: list[Bound], draws: int = 40, seed: int = 7
            ) -> list[Evaluation]:
    """Every policy against the same draws, so the comparison is like for like."""
    return [evaluate(document, p, uncertainties, objective, bounds, draws, seed) for p in policies]


def recommend(evaluations: list[Evaluation]) -> dict[str, object]:
    """Rank by worst case among admissible policies, and say what was excluded and why."""
    admissible = [e for e in evaluations if e.admissible()]
    excluded = {e.policy: e.violations for e in evaluations if not e.admissible()}
    if not admissible:
        return {"recommended": None, "excluded": excluded,
                "reason": "every policy violated a stated constraint"}
    # Rank by worst case; where two policies are within a hair of each other,
    # prefer the reversible one. Chapter 25 argued reversibility changes what
    # evidence a decision needs, so it is the tiebreak rather than a report field.
    top = max(e.worst() for e in admissible)
    close = [e for e in admissible if top - e.worst() <= abs(top) * 0.01]
    best = max(close, key=lambda e: (e.reversible, e.worst()))
    return {
        "recommended": best.policy,
        "worst_case": best.worst(),
        "mean": best.mean(),
        "reversible": best.reversible,
        "excluded": excluded,
        "ranked_by": "worst case across draws, among policies satisfying every constraint; "
                     "reversibility breaks ties within one percent",
    }
