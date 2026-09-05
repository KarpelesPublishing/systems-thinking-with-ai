"""A bounded modeling interview that produces a contract, not a model."""

from dataclasses import dataclass, field

from chapters.chapter_07_decision_contract.code.contract import DecisionContract, Quantity

SECTIONS = ("purpose", "behavior", "boundary", "structure", "evidence", "rights")

QUESTIONS: dict[str, tuple[str, ...]] = {
    "purpose": (
        "What decision will this model inform, and who makes it?",
        "What are the alternatives being chosen between?",
        "Over what period do the consequences count?",
    ),
    "behavior": (
        "What has the outcome quantity done over time, and across what window?",
        "What record shows that, and how often was it measured?",
    ),
    "boundary": (
        "What is deliberately outside this model?",
        "Who is affected by this decision and not in this conversation?",
    ),
    "structure": (
        "What accumulates here, and in what unit?",
        "What changes each of those, and how quickly?",
        "Where does time pass between a decision and its effect?",
    ),
    "evidence": (
        "For each quantity: is it observed, inferred, assumed, or proposed?",
        "Which two sources here disagree?",
    ),
    "rights": (
        "What is this model not permitted to propose?",
        "Who has to agree before the recommendation can be acted on?",
    ),
}


@dataclass
class Section:
    """One part of the interview, accepted or not by a human."""

    name: str
    answers: dict[str, str] = field(default_factory=dict)
    accepted: bool = False

    def __post_init__(self) -> None:
        if self.name not in SECTIONS:
            raise ValueError(f"section must be one of {SECTIONS}")


@dataclass
class Interview:
    """A transcript with a question budget and a human gate per section."""

    question_budget: int = 20
    sections: dict[str, Section] = field(default_factory=dict)

    def asked(self) -> int:
        return sum(len(s.answers) for s in self.sections.values())

    def _unaccepted_before(self, section: str) -> list[str]:
        """Earlier sections still waiting on a person. The gate is an order, not a count."""
        return [s for s in SECTIONS[:SECTIONS.index(section)]
                if not self.sections.get(s, Section(s)).accepted]

    def ask(self, section: str, question: str, answer: str) -> None:
        if section not in SECTIONS:
            raise ValueError(f"section must be one of {SECTIONS}")
        waiting = self._unaccepted_before(section)
        if waiting:
            raise ValueError(f"section '{section}' cannot start until {waiting} are accepted")
        if question not in QUESTIONS[section]:
            raise ValueError(f"'{question}' is not one of this section's approved questions")
        if self.asked() >= self.question_budget:
            raise ValueError(f"question budget of {self.question_budget} is exhausted")
        self.sections.setdefault(section, Section(section)).answers[question] = answer

    def accept(self, section: str) -> None:
        if section not in self.sections:
            raise ValueError(f"section '{section}' has no answers to accept")
        waiting = self._unaccepted_before(section)
        if waiting:
            raise ValueError(f"section '{section}' cannot be accepted before {waiting}")
        if len(self.sections[section].answers) < len(QUESTIONS[section]):
            raise ValueError(f"section '{section}' is not fully answered")
        self.sections[section].accepted = True

    def outstanding(self) -> list[str]:
        return [s for s in SECTIONS if not self.sections.get(s, Section(s)).accepted]

    def unanswerable(self) -> list[str]:
        """Questions answered with an explicit statement that the evidence is absent."""
        markers = ("unknown", "not measured", "no record", "nobody knows")
        return sorted(
            question
            for section in self.sections.values()
            for question, answer in section.answers.items()
            if any(marker in answer.lower() for marker in markers)
        )


def to_contract(interview: Interview, decision: str, decider: str, horizon_length: int,
                horizon_unit: str, outcomes: list[Quantity], levers: list[Quantity],
                inside: list[str], outside: list[str], prohibited: list[str],
                affected: list[str]) -> DecisionContract:
    """Convert an accepted interview into Chapter 7's contract. Refuses if unaccepted."""
    if interview.outstanding():
        raise ValueError(f"sections not accepted: {interview.outstanding()}")
    return DecisionContract(
        decision=decision, decider=decider, horizon_length=horizon_length,
        horizon_unit=horizon_unit, outcomes=outcomes, levers=levers,
        inside_boundary=inside, outside_boundary=outside,
        prohibited_actions=prohibited, affected_parties=affected,
    )
