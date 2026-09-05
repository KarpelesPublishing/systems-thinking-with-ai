import pytest

from chapters.chapter_19_integration.code.solvers import (
    apply_floor,
    converged,
    integrate,
    logistic,
    seeded_noise,
    sequential_pair,
    simultaneous_pair,
    step_refinement,
)

STIFF = logistic(rate=2.6, capacity=100.0)


def test_three_solvers_disagree_wildly_at_a_coarse_step() -> None:
    """Same equations, same step, same start. Answers of 113, 57, and 100."""
    ends = {s: integrate(STIFF, 1.0, 1.0, 20, s)[-1] for s in ("euler", "heun", "rk4")}
    assert ends["euler"] > 110.0
    assert ends["heun"] < 60.0
    assert ends["rk4"] == pytest.approx(100.0, abs=0.5)


def test_euler_breaks_the_carrying_capacity_it_was_given() -> None:
    """A conservation violation produced entirely by the solver."""
    assert max(integrate(STIFF, 1.0, 1.0, 20, "euler")) > 100.0
    assert max(integrate(STIFF, 1.0, 0.0625, 20, "euler")) <= 100.01


def test_every_solver_agrees_once_the_step_is_small_enough() -> None:
    for solver in ("euler", "heun", "rk4"):
        assert integrate(STIFF, 1.0, 0.0625, 20, solver)[-1] == pytest.approx(100.0, abs=0.01)


def test_refinement_exposes_a_coarse_step_that_was_wrong() -> None:
    """The whole value of the stress test: the dt=1.0 answer moves by 13 on the first halving."""
    ends = step_refinement(STIFF, 1.0, 20, "euler", steps=(1.0, 0.5, 0.25))
    assert abs(ends[1] - ends[0]) > 10.0
    assert converged(ends, tolerance=0.1)


def test_a_step_that_never_settles_is_reported_as_unconverged() -> None:
    assert not converged([50.0, 70.0, 90.0], tolerance=0.1)


def test_update_order_changes_the_answer() -> None:
    """Sequential update lets a change cross the model inside one step."""
    assert sequential_pair(100.0, 0.0, 1.0, 0.3) != simultaneous_pair(100.0, 0.0, 1.0, 0.3)


def test_simultaneous_update_conserves_a_closed_transfer() -> None:
    a, b = simultaneous_pair(100.0, 0.0, 1.0, 0.3)
    assert a + b == pytest.approx(100.0)


def test_sequential_update_does_not_conserve_it() -> None:
    a, b = sequential_pair(100.0, 0.0, 1.0, 0.3)
    assert a + b != pytest.approx(100.0)


def test_bad_solver_settings_are_refused() -> None:
    with pytest.raises(ValueError):
        integrate(STIFF, 1.0, 1.0, 20, "magic")
    with pytest.raises(ValueError):
        integrate(STIFF, 1.0, 0.0, 20, "euler")
    with pytest.raises(ValueError):
        logistic(1.0, 0.0)
    with pytest.raises(ValueError):
        converged([1.0, 1.0], tolerance=0.1)


def test_a_bounded_state_never_goes_below_its_floor() -> None:
    """One of the four acceptance tests the chapter names for a runtime."""
    assert apply_floor(-4.0) == 0.0
    assert apply_floor(12.0) == 12.0
    assert apply_floor(-4.0, floor=-10.0) == -4.0


def test_two_runs_with_the_same_seed_produce_identical_output() -> None:
    """The fourth acceptance test: reproducibility from the recorded settings."""
    clean = integrate(STIFF, 1.0, 0.25, 20, "rk4")
    assert seeded_noise(clean, sd=1.0, seed=7) == seeded_noise(clean, sd=1.0, seed=7)
    assert seeded_noise(clean, sd=1.0, seed=7) != seeded_noise(clean, sd=1.0, seed=8)
    assert seeded_noise(clean, sd=0.0, seed=1) == clean


def test_a_stochastic_function_refuses_impossible_settings() -> None:
    with pytest.raises(ValueError):
        seeded_noise([1.0], sd=-1.0, seed=1)
    with pytest.raises(ValueError):
        seeded_noise([1.0], sd=1.0, seed="x")  # type: ignore[arg-type]
