import pytest

from chapters.chapter_03_reference_modes.code.library import reference_mode_library
from chapters.chapter_03_reference_modes.code.modes import (
    exponential_decay,
    exponential_growth,
    goal_seeking,
    oscillation,
    overshoot_and_collapse,
    s_shaped_growth,
)
from chapters.chapter_03_reference_modes.code.observe import add_observation_noise


def test_library_names_all_six_reference_modes() -> None:
    assert set(reference_mode_library()) == {
        "growth",
        "decay",
        "goal seeking",
        "oscillation",
        "s-shaped growth",
        "overshoot and collapse",
    }


def test_growth_rises_and_decay_falls_every_step() -> None:
    rising = exponential_growth(initial=10.0, rate=0.1, steps=20)
    falling = exponential_decay(initial=10.0, rate=0.1, steps=20)
    assert all(rising[i + 1] > rising[i] for i in range(len(rising) - 1))
    assert all(falling[i + 1] < falling[i] for i in range(len(falling) - 1))


def test_goal_seeking_approaches_the_goal_from_either_side() -> None:
    from_below = goal_seeking(initial=0.0, goal=100.0, adjustment_time=4.0, steps=60)
    from_above = goal_seeking(initial=200.0, goal=100.0, adjustment_time=4.0, steps=60)
    assert from_below[-1] == pytest.approx(100.0, abs=0.5)
    assert from_above[-1] == pytest.approx(100.0, abs=0.5)


def test_oscillation_returns_to_its_level_after_one_full_period() -> None:
    path = oscillation(level=50.0, amplitude=10.0, period=12.0, steps=12)
    assert path[0] == pytest.approx(50.0)
    assert path[12] == pytest.approx(50.0)
    assert max(path) == pytest.approx(60.0, abs=0.2)


def test_s_shaped_growth_stops_at_capacity_and_never_exceeds_it() -> None:
    path = s_shaped_growth(initial=1.0, capacity=100.0, rate=0.3, steps=120)
    assert path[-1] == pytest.approx(100.0, abs=1.0)
    assert max(path) <= 100.5


def test_overshoot_and_collapse_peaks_then_ends_below_its_peak() -> None:
    path = overshoot_and_collapse(
        initial=1.0, capacity=100.0, rate=0.4, erosion_rate=0.02, steps=200
    )
    peak = max(path)
    assert peak > path[0]
    assert path[-1] < peak


def test_noise_is_reproducible_from_its_seed_and_differs_across_seeds() -> None:
    clean = exponential_growth(initial=10.0, rate=0.05, steps=30)
    assert add_observation_noise(clean, sd=1.0, seed=7) == add_observation_noise(
        clean, sd=1.0, seed=7
    )
    assert add_observation_noise(clean, sd=1.0, seed=7) != add_observation_noise(
        clean, sd=1.0, seed=8
    )


def test_zero_noise_leaves_the_path_untouched() -> None:
    clean = exponential_growth(initial=10.0, rate=0.05, steps=10)
    assert add_observation_noise(clean, sd=0.0, seed=1) == clean


def test_generators_reject_impossible_arguments() -> None:
    with pytest.raises(ValueError):
        exponential_growth(initial=10.0, rate=0.1, steps=0)
    with pytest.raises(ValueError):
        s_shaped_growth(initial=1.0, capacity=0.0, rate=0.3, steps=10)
    with pytest.raises(ValueError):
        oscillation(level=1.0, amplitude=1.0, period=0.0, steps=10)
    with pytest.raises(ValueError):
        goal_seeking(initial=0.0, goal=1.0, adjustment_time=0.0, steps=10)
