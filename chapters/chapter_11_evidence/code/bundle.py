"""An evidence bundle: a causal claim with everything needed to challenge it.

A claim without provenance, units, a date, and an evidence level is an opinion
formatted as a finding. This module refuses to accept one.
"""

from dataclasses import dataclass, field
from datetime import date

EVIDENCE_LEVELS = ("observed", "inferred", "assumed", "proposed")


@dataclass(frozen=True)
class Source:
    """Where a claim came from and when it was true."""

    kind: str  # "record", "interview", "document", "measurement", "model"
    locator: str  # a URL, a system name, a person's role, a file path
    retrieved: date

    def __post_init__(self) -> None:
        if self.kind not in ("record", "interview", "document", "measurement", "model"):
            raise ValueError(f"unknown source kind: {self.kind}")
        if not self.locator.strip():
            raise ValueError("a source needs a locator someone could follow")


@dataclass(frozen=True)
class Revision:
    """What a claim used to say, and why it stopped saying it."""

    statement: str
    evidence: str
    changed: date
    reason: str

    def __post_init__(self) -> None:
        if not self.reason.strip():
            raise ValueError("a revision needs a reason: overwriting silently is the defect")


@dataclass
class Claim:
    """One causal assertion with its unit, its provenance, and its falsifier."""

    statement: str
    unit: str
    evidence: str
    sources: list[Source] = field(default_factory=list)
    falsifier: str = ""
    contradicts: list[str] = field(default_factory=list)
    owner: str = ""
    history: list[Revision] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.statement.strip():
            raise ValueError("a claim needs a statement")
        if self.evidence not in EVIDENCE_LEVELS:
            raise ValueError(f"evidence must be one of {EVIDENCE_LEVELS}")

    def __setattr__(self, name: str, value: object) -> None:
        """Refuse the silent overwrite. What a claim says may only change through revise()."""
        if name in ("statement", "evidence") and hasattr(self, name):
            raise AttributeError(f"assigning to '{name}' would overwrite a claim; use revise()")
        object.__setattr__(self, name, value)

    def revise(self, statement: str, evidence: str, changed: date, reason: str) -> None:
        """Replace what the claim says, keeping what it used to say and why it moved."""
        if evidence not in EVIDENCE_LEVELS:
            raise ValueError(f"evidence must be one of {EVIDENCE_LEVELS}")
        self.history.append(Revision(self.statement, self.evidence, changed, reason))
        object.__setattr__(self, "statement", statement)
        object.__setattr__(self, "evidence", evidence)


def validate(claim: Claim) -> list[str]:
    """Return every reason this claim is not yet usable as evidence."""
    problems = []
    if claim.evidence == "observed" and not claim.sources:
        problems.append("claims observation but names no source")
    if not claim.unit.strip():
        problems.append("no unit: the claim cannot be checked against a record")
    if not claim.falsifier.strip():
        problems.append("no falsifier: nothing would show this claim is wrong")
    if not claim.owner.strip():
        problems.append("no owner: nobody is named who would know")
    return problems


def validate_bundle(claims: list[Claim]) -> dict[str, list[str]]:
    """Validate every claim and report the problems by statement."""
    if not claims:
        raise ValueError("a bundle must contain at least one claim")
    return {c.statement: validate(c) for c in claims if validate(c)}


def contradictions(claims: list[Claim]) -> list[tuple[str, str]]:
    """Find pairs where one claim names another as contradicting it."""
    statements = {c.statement for c in claims}
    found = []
    for claim in claims:
        for other in claim.contradicts:
            if other in statements:
                pair = tuple(sorted((claim.statement, other)))
                if pair not in found:
                    found.append(pair)  # type: ignore[arg-type]
    return found  # type: ignore[return-value]


def confidence_profile(claims: list[Claim]) -> dict[str, int]:
    """The count at each evidence level. One claim has a level; a bundle has this profile."""
    return {level: sum(1 for c in claims if c.evidence == level) for level in EVIDENCE_LEVELS}


def stale(claims: list[Claim], today: date, max_age_days: int) -> list[str]:
    """Claims whose newest source is older than the allowed age."""
    out = []
    for claim in claims:
        if not claim.sources:
            continue
        newest = max(s.retrieved for s in claim.sources)
        if (today - newest).days > max_age_days:
            out.append(claim.statement)
    return out
