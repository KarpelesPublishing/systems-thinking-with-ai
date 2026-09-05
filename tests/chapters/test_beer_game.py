import pytest

from chapters.chapter_05_beer_game.code.amplification import (
    amplification_ratio,
    stage_variability,
    swing,
)
from chapters.chapter_05_beer_game.code.chain import run_chain, ship, step_chain
from chapters.chapter_05_beer_game.code.models import ChainParameters, Stage
from chapters.chapter_05_beer_game.code.policy import order_quantity, smooth_demand

STEP_DEMAND = [4.0] * 5 + [8.0] * 45


def test_a_steady_chain_stays_steady() -> None:
    history = run_chain([4.0] * 30)
    first, last = history["orders"][2], history["orders"][-1]
    assert first == pytest.approx(last, abs=1e-6)
    assert max(max(week) for week in history["backlog"]) == pytest.approx(0.0)


def test_order_swings_grow_with_distance_from_the_customer() -> None:
    """The bullwhip: each stage upstream orders more erratically than the one below it."""
    history = run_chain(STEP_DEMAND)
    spread = stage_variability(history)
    assert all(spread[i + 1] > spread[i] for i in range(len(spread) - 1))


def test_a_small_customer_step_becomes_a_large_factory_swing() -> None:
    history = run_chain(STEP_DEMAND)
    factory = [week[3] for week in history["orders"]]
    assert amplification_ratio(STEP_DEMAND, factory) > 10.0


def test_counting_the_supply_line_reduces_factory_amplification() -> None:
    """The policy fix. Ignoring what you already ordered is what drives the overshoot."""
    ignored = run_chain(STEP_DEMAND, ChainParameters(supply_line_weight=0.0))
    counted = run_chain(STEP_DEMAND, ChainParameters(supply_line_weight=1.0))
    factory_ignored = [week[3] for week in ignored["orders"]]
    factory_counted = [week[3] for week in counted["orders"]]
    assert swing(factory_counted) < swing(factory_ignored)
    assert max(factory_counted) < max(factory_ignored)


def test_the_fix_helps_the_factory_far_more_than_the_retailer() -> None:
    """Why no single stage discovers it: the benefit lands somewhere else."""
    ignored = run_chain(STEP_DEMAND, ChainParameters(supply_line_weight=0.0))
    counted = run_chain(STEP_DEMAND, ChainParameters(supply_line_weight=1.0))
    retailer_change = swing([w[0] for w in counted["orders"]]) / swing(
        [w[0] for w in ignored["orders"]]
    )
    factory_change = swing([w[3] for w in counted["orders"]]) / swing(
        [w[3] for w in ignored["orders"]]
    )
    assert factory_change < 0.7
    assert retailer_change > factory_change


def test_a_stage_never_ships_more_than_it_holds() -> None:
    assert ship(Stage(inventory=3.0, backlog=0.0), requested=10.0) == 3.0
    assert ship(Stage(inventory=30.0, backlog=2.0), requested=10.0) == 12.0


def test_unmet_orders_become_backlog_rather_than_disappearing() -> None:
    stages = [Stage(inventory=0.0) for _ in range(4)]
    updated, _ = step_chain(stages, customer_order=9.0, parameters=ChainParameters())
    assert updated[0].backlog == pytest.approx(9.0)


def test_smoothing_moves_belief_toward_what_was_observed() -> None:
    assert smooth_demand(4.0, 8.0, 4.0) == pytest.approx(5.0)
    assert smooth_demand(4.0, 4.0, 4.0) == pytest.approx(4.0)


def test_orders_never_go_negative_and_weights_are_bounded() -> None:
    assert (
        order_quantity(
            expected_demand=4.0,
            inventory=500.0,
            backlog=0.0,
            supply_line=0.0,
            target_inventory=12.0,
            inventory_adjustment_time=4.0,
        )
        == 0.0
    )
    with pytest.raises(ValueError):
        order_quantity(
            expected_demand=4.0,
            inventory=12.0,
            backlog=0.0,
            supply_line=0.0,
            target_inventory=12.0,
            inventory_adjustment_time=4.0,
            supply_line_weight=1.5,
        )


def test_amplification_is_undefined_when_the_customer_never_varies() -> None:
    with pytest.raises(ValueError):
        amplification_ratio([4.0] * 10, [4.0] * 10)


def test_longer_pipelines_raise_amplification() -> None:
    """Chapter 5 tells the reader to lengthen the pipelines, so the lever has to exist."""
    demand = [4.0] * 5 + [8.0] * 45
    ratios = []
    for weeks in (1, 2, 3):
        history = run_chain(demand, ChainParameters(supply_line_weight=0.0, pipeline_weeks=weeks))
        factory = [week[3] for week in history["orders"]]
        ratios.append(amplification_ratio(demand, factory))
    assert ratios == sorted(ratios)
    assert ratios[0] < ratios[-1]


def test_a_pipeline_shorter_than_a_week_is_refused() -> None:
    with pytest.raises(ValueError):
        ChainParameters(pipeline_weeks=0)
