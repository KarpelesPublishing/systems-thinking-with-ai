import pytest

from chapters.chapter_07_decision_contract.code.contract import Quantity
from chapters.chapter_26_interview.code.interview import (
    QUESTIONS,
    SECTIONS,
    Interview,
    to_contract,
)


def fill(interview: Interview, section: str, answer: str = "yes") -> None:
    for question in QUESTIONS[section]:
        interview.ask(section, question, answer)
    interview.accept(section)


def complete() -> Interview:
    interview = Interview(question_budget=40)
    for section in SECTIONS:
        fill(interview, section)
    return interview


def test_only_approved_questions_may_be_asked() -> None:
    interview = Interview()
    with pytest.raises(ValueError):
        interview.ask("purpose", "So what's the vibe here?", "unclear")
    with pytest.raises(ValueError):
        interview.ask("vibes", QUESTIONS["purpose"][0], "x")


def test_the_question_budget_is_enforced() -> None:
    """A bounded interview, so the model cannot ask its way to a model."""
    interview = Interview(question_budget=2)
    interview.ask("purpose", QUESTIONS["purpose"][0], "a")
    interview.ask("purpose", QUESTIONS["purpose"][1], "b")
    with pytest.raises(ValueError):
        interview.ask("purpose", QUESTIONS["purpose"][2], "c")


def test_a_section_cannot_be_accepted_until_it_is_answered() -> None:
    interview = Interview()
    interview.ask("purpose", QUESTIONS["purpose"][0], "a")
    with pytest.raises(ValueError):
        interview.accept("purpose")


def test_outstanding_lists_every_unaccepted_section() -> None:
    interview = Interview(question_budget=40)
    assert interview.outstanding() == list(SECTIONS)
    fill(interview, "purpose")
    assert "purpose" not in interview.outstanding()


def test_answers_admitting_no_evidence_are_surfaced() -> None:
    """The challenge: find the question the evidence cannot answer."""
    interview = Interview(question_budget=40)
    fill(interview, "purpose")
    interview.ask("behavior", QUESTIONS["behavior"][0], "rising, we think")
    interview.ask("behavior", QUESTIONS["behavior"][1], "no record before last year")
    assert interview.unanswerable() == [QUESTIONS["behavior"][1]]


def test_a_contract_cannot_be_produced_from_an_unfinished_interview() -> None:
    interview = Interview(question_budget=40)
    fill(interview, "purpose")
    with pytest.raises(ValueError):
        to_contract(interview, "whether to hire", "ops", 6, "quarter", [], [], [], [], [], [])


def test_an_accepted_interview_produces_a_contract() -> None:
    contract = to_contract(
        complete(), decision="whether to raise the intake cap", decider="head of operations",
        horizon_length=6, horizon_unit="quarter",
        outcomes=[Quantity("churn", "customers/quarter", "observed")],
        levers=[Quantity("intake cap", "accounts/week", "observed")],
        inside=["intake", "workforce"], outside=["competitor pricing"],
        prohibited=["reduce contracted service levels"], affected=["front-line staff"],
    )
    assert contract.decision.startswith("whether")
    assert contract.horizon_unit == "quarter"


def test_every_section_has_questions_and_they_are_distinct() -> None:
    assert set(QUESTIONS) == set(SECTIONS)
    all_questions = [q for qs in QUESTIONS.values() for q in qs]
    assert len(all_questions) == len(set(all_questions))


def test_a_section_cannot_start_before_the_earlier_ones_are_accepted() -> None:
    """Chapter 26 calls the gate a sequence of agreements, so order has to be enforced."""
    interview = Interview(question_budget=40)
    with pytest.raises(ValueError):
        interview.ask("structure", QUESTIONS["structure"][0], "headcount")


def test_a_section_cannot_be_accepted_out_of_order() -> None:
    interview = Interview(question_budget=40)
    fill(interview, "purpose")
    interview.ask("behavior", QUESTIONS["behavior"][0], "rising")
    interview.ask("behavior", QUESTIONS["behavior"][1], "since spring")
    interview.accept("behavior")
    assert interview.outstanding() == ["boundary", "structure", "evidence", "rights"]
