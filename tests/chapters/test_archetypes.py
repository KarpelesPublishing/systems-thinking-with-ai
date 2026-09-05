import pytest

from chapters.chapter_09_archetypes.code.limits import (
    eroding_limit,
    fixed_limit,
    peaks_then_falls,
    settles,
)


def test_a_fixed_limit_settles_at_the_limit() -> None:
    path = fixed_limit(initial=1.0, capacity=100.0, rate=0.3, steps=120)
    assert settles(path)
    assert path[-1] == pytest.approx(100.0, abs=1.0)


def test_an_eroding_limit_peaks_and_collapses() -> None:
    """Same archetype, same growth engine. Only the boundary changed."""
    path, _ = eroding_limit(
        initial=1.0, capacity=100.0, rate=0.4, erosion_rate=0.02, steps=200
    )
    assert peaks_then_falls(path)
    assert not settles(path)
    assert max(path) < 100.0


def test_zero_erosion_reduces_boundary_b_to_boundary_a() -> None:
    """The two are one model with one parameter set to zero."""
    fixed = fixed_limit(initial=1.0, capacity=100.0, rate=0.3, steps=150)
    eroded, capacity = eroding_limit(
        initial=1.0, capacity=100.0, rate=0.3, erosion_rate=0.0, steps=150
    )
    assert eroded == pytest.approx(fixed)
    assert capacity[-1] == pytest.approx(100.0)


def test_the_capacity_path_is_returned_because_it_is_a_model_variable() -> None:
    _, capacity = eroding_limit(
        initial=1.0, capacity=100.0, rate=0.4, erosion_rate=0.02, steps=200
    )
    assert capacity[-1] < capacity[0]
    assert all(capacity[i + 1] <= capacity[i] for i in range(len(capacity) - 1))


def test_both_boundaries_reject_impossible_arguments() -> None:
    with pytest.raises(ValueError):
        fixed_limit(initial=1.0, capacity=0.0, rate=0.3, steps=10)
    with pytest.raises(ValueError):
        eroding_limit(initial=1.0, capacity=100.0, rate=0.3, erosion_rate=-1.0, steps=10)
    with pytest.raises(ValueError):
        fixed_limit(initial=1.0, capacity=100.0, rate=0.3, steps=0)
