"""A decision contract: what the model is for, stated before the model exists.

The contract is a refusal device. A request a contract cannot express is a request
nobody has finished framing, and building against it produces a model whose purpose
is discovered afterwards by whoever reads the output.
"""

from dataclasses import dataclass, field

ALLOWED_HORIZON_UNITS = ("day", "week", "month", "quarter", "year")

# The book's four evidence levels, used identically from Chapter 8 onward.
EVIDENCE_LEVELS = ("observed", "inferred", "assumed", "proposed")


@dataclass(frozen=True)
class Quantity:
    """A named variable with the unit it is measured in and how it is known."""

    name: str
    unit: str
    evidence: str  # one of EVIDENCE_LEVELS

    def __post_init__(self) -> None:
        if not self.name or not self.unit:
            raise ValueError("a quantity needs a name and a unit")
        if self.evidence not in EVIDENCE_LEVELS:
            raise ValueError(f"evidence must be one of {EVIDENCE_LEVELS}")


@dataclass
class DecisionContract:
    """What decision this model informs, over what horizon, inside what boundary."""

    decision: str
    decider: str
    horizon_length: int
    horizon_unit: str
    outcomes: list[Quantity] = field(default_factory=list)
    levers: list[Quantity] = field(default_factory=list)
    inside_boundary: list[str] = field(default_factory=list)
    outside_boundary: list[str] = field(default_factory=list)
    prohibited_actions: list[str] = field(default_factory=list)
    affected_parties: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.decision.strip():
            raise ValueError("a contract needs a decision, not a topic")
        if not self.decider.strip():
            raise ValueError("a contract needs a named decider")
        if self.horizon_unit not in ALLOWED_HORIZON_UNITS:
            raise ValueError(f"horizon_unit must be one of {ALLOWED_HORIZON_UNITS}")
        if self.horizon_length < 1:
            raise ValueError("horizon_length must be at least 1")


def missing_pieces(contract: DecisionContract) -> list[str]:
    """Return the parts a contract needs before modeling should start."""
    gaps = []
    if not contract.outcomes:
        gaps.append("no outcome: nothing states what better would look like")
    if not contract.levers:
        gaps.append("no lever: nothing the decider controls is represented")
    if not contract.outside_boundary:
        gaps.append("nothing excluded: a boundary that excludes nothing was not drawn")
    if not contract.affected_parties:
        gaps.append("no affected parties: the distributional question was not asked")
    if not contract.prohibited_actions:
        gaps.append("no prohibited actions: the model may propose what cannot be done")
    return gaps


def is_ready(contract: DecisionContract) -> bool:
    """A contract is ready when nothing on the checklist is missing."""
    return not missing_pieces(contract)


def unit_conflicts(contract: DecisionContract) -> list[str]:
    """Report names used twice with different units, the commonest framing defect."""
    seen: dict[str, str] = {}
    conflicts = []
    for quantity in list(contract.outcomes) + list(contract.levers):
        previous = seen.get(quantity.name)
        if previous is not None and previous != quantity.unit:
            conflicts.append(f"{quantity.name}: {previous} vs {quantity.unit}")
        seen[quantity.name] = quantity.unit
    return conflicts
