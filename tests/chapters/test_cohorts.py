import pytest

from chapters.chapter_17_cohorts.code.cohorts import (
    Band,
    advance,
    average_experience,
    effective_capacity,
    headcount,
    total_experience,
)

START = [Band(20, 40.0), Band(30, 150.0), Band(50, 500.0)]
POLICY = {"maturation": [0.25, 0.2, 0.0], "attrition": [0.10, 0.06, 0.04]}


def surge(steps: int = 3, hires: float = 40.0) -> list[Band]:
    bands = START
    for _ in range(steps):
        bands = advance(bands, hires=hires, **POLICY)
    return bands


def test_a_band_reports_years_per_person() -> None:
    assert Band(20, 40.0).average() == pytest.approx(2.0)
    assert Band(0, 0.0).average() == 0.0


def test_hiring_raises_headcount() -> None:
    assert headcount(surge()) > headcount(START)


def test_hiring_lowers_average_experience_in_the_junior_band() -> None:
    """People arrive with none, so the band they arrive into gets diluted."""
    assert surge()[0].average() < START[0].average()


def test_headcount_overstates_the_capacity_gain() -> None:
    """The chapter's argument: heads and capability do not grow together."""
    after = surge()
    head_growth = headcount(after) / headcount(START)
    capacity_growth = effective_capacity(after, 4.0) / effective_capacity(START, 4.0)
    assert head_growth > capacity_growth
    assert head_growth > 1.8
    assert capacity_growth < 1.6


def test_experience_leaves_with_the_people_who_leave() -> None:
    """Attrition cannot strip people out and leave their experience behind.

    Run at a short step so ageing contributes little and the coflow is isolated.
    """
    after = advance(
        START, hires=0.0, maturation=[0, 0, 0], attrition=[0.5, 0.0, 0.0], dt=0.01
    )
    assert after[0].people == pytest.approx(19.9)
    assert after[0].average() == pytest.approx(START[0].average(), abs=0.02)


def test_a_frozen_workforce_still_accumulates_experience() -> None:
    still = advance(START, hires=0.0, maturation=[0, 0, 0], attrition=[0, 0, 0])
    assert headcount(still) == pytest.approx(headcount(START))
    assert total_experience(still) > total_experience(START)
    assert average_experience(still) > average_experience(START)


def test_impossible_bands_and_rates_are_rejected() -> None:
    with pytest.raises(ValueError):
        Band(-1, 0.0)
    with pytest.raises(ValueError):
        advance(START, hires=1.0, maturation=[0.2], attrition=[0.1, 0.1, 0.1])
    with pytest.raises(ValueError):
        advance(START, hires=1.0, maturation=[1.5, 0, 0], attrition=[0, 0, 0])
    with pytest.raises(ValueError):
        effective_capacity(START, ramp_years=0.0)
