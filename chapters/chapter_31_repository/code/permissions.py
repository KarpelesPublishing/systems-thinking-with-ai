"""Who may do what to a model, and the local gate that enforces it."""

from dataclasses import dataclass

STAGES = ("read", "simulate", "propose", "approve", "execute")
ROLES = ("interviewer", "compiler", "critic", "experiment_designer", "policy_searcher", "human")

# Every AI role stops before approve. Only a human crosses the last two stages.
GRANTS: dict[str, tuple[str, ...]] = {
    "interviewer": ("read",),
    "compiler": ("read", "propose"),
    "critic": ("read", "simulate", "propose"),
    "experiment_designer": ("read", "simulate", "propose"),
    "policy_searcher": ("read", "simulate", "propose"),
    "human": STAGES,
}


@dataclass(frozen=True)
class Request:
    """One attempted action, named at the stage it belongs to."""

    role: str
    stage: str
    target: str
    reason: str = ""

    def __post_init__(self) -> None:
        if self.role not in ROLES:
            raise ValueError(f"role must be one of {ROLES}")
        if self.stage not in STAGES:
            raise ValueError(f"stage must be one of {STAGES}")


@dataclass(frozen=True)
class Denial:
    """A refusal, recorded so that attempts are visible rather than only blocked."""

    request: Request
    reason: str


def check(request: Request) -> Denial | None:
    """Allow or deny one request, and say which rule decided."""
    granted = GRANTS[request.role]
    if request.stage not in granted:
        return Denial(request, f"role '{request.role}' may only {', '.join(granted)}")
    return None


def gate(requests: list[Request]) -> tuple[list[Request], list[Denial]]:
    """Split a batch into what proceeds and what is refused."""
    allowed, denied = [], []
    for request in requests:
        denial = check(request)
        (denied if denial else allowed).append(denial or request)
    return allowed, denied


def ci_sequence() -> tuple[str, ...]:
    """The order local checks run in, cheapest and most-specific first."""
    return (
        "schema: every model document validates against its schema",
        "semantics: references resolve, flows name stocks, units carry a time base",
        "compile: no algebraic loops, evaluation order exists",
        "tests: the chapter packs and the runtime suite pass",
        "provenance: every parameter claiming observation names a source",
        "replay: recorded scenarios reproduce their stored outputs",
    )


def run_ci(results: dict[str, bool]) -> dict[str, object]:
    """Report the first failing stage. Later stages are not evidence if an earlier one failed."""
    order = [step.split(":")[0] for step in ci_sequence()]
    missing = [s for s in order if s not in results]
    if missing:
        raise ValueError(f"no result reported for: {missing}")
    for stage in order:
        if not results[stage]:
            return {"passed": False, "failed_at": stage,
                    "note": "later stages were not evaluated as evidence"}
    return {"passed": True, "failed_at": None}
