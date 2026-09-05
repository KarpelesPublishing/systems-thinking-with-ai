from datetime import date

import pytest

from chapters.chapter_11_evidence.code.bundle import (
    Claim,
    Revision,
    Source,
    confidence_profile,
    contradictions,
    stale,
    validate,
    validate_bundle,
)

RECORD = Source("record", "billing system, table invoices", date(2026, 8, 1))


def good_claim(statement: str = "raising the intake cap increases churn",
               evidence: str = "observed") -> Claim:
    return Claim(
        statement=statement,
        unit="customers/quarter",
        evidence=evidence,
        sources=[RECORD],
        falsifier="a quarter where the cap rose and churn did not",
        owner="head of service operations",
    )


def test_a_complete_claim_validates() -> None:
    assert validate(good_claim()) == []


def test_claiming_observation_without_a_source_is_rejected() -> None:
    claim = good_claim()
    claim.sources = []
    assert any("names no source" in p for p in validate(claim))


def test_a_claim_without_a_falsifier_is_not_evidence() -> None:
    claim = good_claim()
    claim.falsifier = ""
    assert any("falsifier" in p for p in validate(claim))


def test_a_claim_without_a_unit_cannot_be_checked() -> None:
    claim = good_claim()
    claim.unit = "  "
    assert any("unit" in p for p in validate(claim))


def test_a_claim_with_nobody_named_is_not_actionable() -> None:
    claim = good_claim()
    claim.owner = ""
    assert any("owner" in p for p in validate(claim))


def test_the_bundle_reports_only_the_claims_with_problems() -> None:
    fine, broken = good_claim(), good_claim("quality drives referrals")
    broken.falsifier = ""
    problems = validate_bundle([fine, broken])
    assert list(problems) == ["quality drives referrals"]


def test_contradictions_are_reported_as_pairs() -> None:
    a, b = good_claim(), good_claim("raising the intake cap reduces churn")
    a.contradicts = [b.statement]
    assert contradictions([a, b]) == [tuple(sorted((a.statement, b.statement)))]


def test_the_confidence_profile_shows_how_little_is_observed() -> None:
    claims = [good_claim()]
    for level in ("inferred", "assumed", "proposed"):
        claims.append(good_claim(f"claim {level}", level))
    assert confidence_profile(claims) == {
        "observed": 1, "inferred": 1, "assumed": 1, "proposed": 1
    }


def test_claims_resting_on_old_sources_are_flagged() -> None:
    claim = good_claim()
    assert stale([claim], today=date(2026, 8, 30), max_age_days=10) == [claim.statement]
    assert stale([claim], today=date(2026, 8, 30), max_age_days=60) == []


def test_malformed_claims_and_sources_are_rejected() -> None:
    with pytest.raises(ValueError):
        Claim(statement="  ", unit="x", evidence="observed")
    with pytest.raises(ValueError):
        Claim(statement="x", unit="x", evidence="probably")
    with pytest.raises(ValueError):
        Source("rumour", "someone said", date(2026, 1, 1))
    with pytest.raises(ValueError):
        validate_bundle([])


def test_revising_a_claim_keeps_what_it_used_to_say() -> None:
    """Chapter 11 requires a claim to carry its history, so overwriting has to be impossible."""
    claim = Claim("hiring delay is six weeks", "week", "observed",
                  [Source("record", "ATS export", date(2026, 1, 5))],
                  falsifier="a cohort hired in under four weeks", owner="talent lead")
    claim.revise("hiring delay is four weeks", "observed", date(2026, 6, 1),
                 "process change removed a signoff")
    assert claim.statement == "hiring delay is four weeks"
    assert [r.statement for r in claim.history] == ["hiring delay is six weeks"]
    assert claim.history[0].changed == date(2026, 6, 1)
    assert claim.history[0].reason == "process change removed a signoff"


def test_a_revision_without_a_reason_is_refused() -> None:
    with pytest.raises(ValueError):
        Revision("old", "assumed", date(2026, 6, 1), "   ")


def test_a_claim_cannot_be_overwritten_by_assignment() -> None:
    """revise() is the only way in, or the history guarantee is decoration."""
    claim = Claim("hiring delay is six weeks", "week", "assumed",
                  falsifier="a cohort hired in under four weeks", owner="talent lead")
    with pytest.raises(AttributeError):
        claim.statement = "silently changed"
    with pytest.raises(AttributeError):
        claim.evidence = "observed"
    assert claim.statement == "hiring delay is six weeks"
