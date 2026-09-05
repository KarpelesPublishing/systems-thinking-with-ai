from chapters.chapter_14_dominance.code.dominance import (
    BALANCING,
    REINFORCING,
    Diffusion,
    contributions,
    dominant_loop,
    handover_step,
    run,
)

MODEL = Diffusion()
PATH = run(MODEL, steps=40)


def test_the_reinforcing_loop_dominates_early() -> None:
    assert dominant_loop(MODEL, PATH)[0] == REINFORCING


def test_the_balancing_loop_dominates_late() -> None:
    assert dominant_loop(MODEL, PATH)[-1] == BALANCING


def test_dominance_changes_hands_once_inside_the_run() -> None:
    """Neither loop is 'the' explanation. The answer depends on when you ask."""
    step = handover_step(MODEL, PATH)
    assert step is not None
    assert 0 < step < len(PATH)


def test_knocking_out_a_loop_changes_the_rate_it_was_driving() -> None:
    early = MODEL.adoption_rate(500.0)
    assert MODEL.adoption_rate(500.0, contact_from=0.0) < early
    assert MODEL.adoption_rate(500.0, potential_from=0.0) > early


def test_contribution_of_saturation_grows_as_the_market_fills() -> None:
    c = contributions(MODEL, PATH)[BALANCING]
    assert c[-1] > c[0]


def test_adoption_never_exceeds_the_market() -> None:
    assert max(PATH) <= MODEL.total_market
