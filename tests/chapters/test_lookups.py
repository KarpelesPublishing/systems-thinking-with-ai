import pytest

from chapters.chapter_15_lookups.code.lookup import (
    Lookup,
    OutsideDomain,
    evaluate_polynomial,
    fit_polynomial,
)

POINTS = [(0, 0), (1, 0.35), (2, 0.6), (3, 0.78), (4, 0.88), (5, 0.93)]


def test_a_lookup_interpolates_between_observed_points() -> None:
    assert Lookup(POINTS)(2.5) == pytest.approx(0.69)


def test_a_lookup_returns_observed_points_exactly() -> None:
    lookup = Lookup(POINTS)
    for x, y in POINTS:
        assert lookup(x) == pytest.approx(y)


def test_a_lookup_refuses_questions_outside_its_evidence() -> None:
    with pytest.raises(OutsideDomain):
        Lookup(POINTS)(9.0)
    with pytest.raises(OutsideDomain):
        Lookup(POINTS)(-0.5)


def test_a_fit_and_a_lookup_agree_inside_the_data() -> None:
    coefficients = fit_polynomial(POINTS, degree=5)
    assert evaluate_polynomial(coefficients, 2.5) == pytest.approx(Lookup(POINTS)(2.5), abs=0.02)


def test_a_fit_answers_outside_the_data_and_the_answer_is_absurd() -> None:
    """Same points, same agreement inside. The fit has no idea it has left the evidence."""
    coefficients = fit_polynomial(POINTS, degree=5)
    assert evaluate_polynomial(coefficients, 12.0) > 40.0
    assert Lookup(POINTS).is_bounded_by(0.0, 1.0)


def test_shape_properties_are_testable() -> None:
    assert Lookup(POINTS).is_monotonic()
    assert not Lookup([(0, 0), (1, 5), (2, 1)]).is_monotonic()
    assert Lookup(POINTS).domain == (0, 5)


def test_a_lookup_needs_two_points_and_one_value_per_input() -> None:
    with pytest.raises(ValueError):
        Lookup([(0, 0)])
    with pytest.raises(ValueError):
        Lookup([(1, 0.2), (1, 0.9)])


def test_an_input_a_hair_past_the_domain_is_arithmetic_not_extrapolation() -> None:
    """A solver landing on a domain end arrives a few epsilons past it."""
    curve = Lookup([(0.0, 1.0), (1.0, 0.5)], name="effectiveness")
    assert curve(-8.858951809952576e-17) == pytest.approx(1.0)
    assert curve(1.0 + 1e-16) == pytest.approx(0.5)


def test_a_real_excursion_past_the_domain_is_still_refused() -> None:
    curve = Lookup([(0.0, 1.0), (1.0, 0.5)], name="effectiveness")
    with pytest.raises(OutsideDomain):
        curve(1.01)
    with pytest.raises(OutsideDomain):
        curve(-0.01)
