import pytest

from chapters.chapter_10_boundaries.code.stratified import (
    Group,
    aggregate_wait,
    hidden_spread,
    population_mean,
    spread_ratio,
    stratified_waits,
    worst_served,
)

GROUPS = [Group("routine", 0.8, 0.8), Group("complex", 0.2, 1.8)]


def test_the_aggregate_model_reports_one_number() -> None:
    assert aggregate_wait(arrivals=9.0, servers=10, service_time=1.0) == pytest.approx(0.9)


def test_stratifying_reveals_a_gap_the_aggregate_hides() -> None:
    waits = stratified_waits(9.0, 10, 1.0, GROUPS)
    assert waits["complex"] > waits["routine"]
    assert spread_ratio(waits) > 2.0
    assert hidden_spread(waits) > 0.9


def test_the_worst_served_group_is_the_minority() -> None:
    """The aggregate number sits near the majority, so the minority disappears into it."""
    waits = stratified_waits(9.0, 10, 1.0, GROUPS)
    assert worst_served(waits) == "complex"
    smallest = min(GROUPS, key=lambda g: g.share)
    assert smallest.name == "complex"


def test_the_share_weighted_mean_stays_close_to_the_majority() -> None:
    waits = stratified_waits(9.0, 10, 1.0, GROUPS)
    mean = population_mean(waits, GROUPS)
    assert abs(mean - waits["routine"]) < abs(mean - waits["complex"])


def test_one_group_reduces_to_the_aggregate_case() -> None:
    single = [Group("everyone", 1.0, 1.0)]
    waits = stratified_waits(9.0, 10, 1.0, single)
    assert waits["everyone"] == pytest.approx(aggregate_wait(9.0, 10, 1.0))


def test_shares_that_do_not_sum_to_one_are_rejected() -> None:
    with pytest.raises(ValueError):
        stratified_waits(9.0, 10, 1.0, [Group("a", 0.5, 1.0), Group("b", 0.2, 1.0)])
    with pytest.raises(ValueError):
        Group("bad", 0.0, 1.0)


def test_the_aggregate_model_refuses_to_report_above_full_utilization() -> None:
    with pytest.raises(ValueError):
        aggregate_wait(arrivals=11.0, servers=10, service_time=1.0)


def test_spread_needs_more_than_one_group() -> None:
    with pytest.raises(ValueError):
        hidden_spread({"only": 1.0})
