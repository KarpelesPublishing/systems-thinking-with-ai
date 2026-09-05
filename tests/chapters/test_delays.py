import pytest

from chapters.chapter_16_delays.code.delays import (
    FirstOrderDelay,
    PipelineDelay,
    run_first_order,
    run_pipeline,
    time_to_fraction,
)

STEP = [0.0] * 3 + [10.0] * 40


def test_a_pipeline_returns_the_input_intact_after_its_length() -> None:
    assert run_pipeline([1.0, 2.0, 3.0, 4.0, 5.0], length=2) == [0.0, 0.0, 1.0, 2.0, 3.0]


def test_the_same_mean_delay_gives_very_different_responses() -> None:
    """Four periods of delay either way. The shapes are not comparable."""
    pipeline = run_pipeline(STEP, length=4)
    first_order = run_first_order(STEP, mean=4.0)
    assert pipeline[7] == pytest.approx(10.0)
    assert first_order[7] < 7.0


def test_a_first_order_delay_takes_far_longer_to_finish_arriving() -> None:
    assert time_to_fraction(run_pipeline(STEP, 4), target=10.0, fraction=0.95) == 7
    assert time_to_fraction(run_first_order(STEP, 4.0), target=10.0, fraction=0.95) > 12


def test_a_first_order_delay_starts_responding_immediately() -> None:
    """The pipeline shows nothing for four periods. The tank starts leaking at once."""
    first_order = run_first_order(STEP, mean=4.0)
    pipeline = run_pipeline(STEP, length=4)
    assert first_order[5] > 0.0
    assert pipeline[5] == 0.0


def test_both_delays_hold_material_in_transit() -> None:
    pipeline, tank = PipelineDelay(4), FirstOrderDelay(4.0)
    for _ in range(6):
        pipeline.step(10.0)
        tank.step(10.0)
    assert pipeline.in_transit() > 0.0
    assert tank.in_transit() > 0.0


def test_a_pipeline_length_must_be_whole_periods() -> None:
    with pytest.raises(ValueError):
        PipelineDelay(0)
    with pytest.raises(ValueError):
        PipelineDelay(2.5)  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        FirstOrderDelay(0.0)
