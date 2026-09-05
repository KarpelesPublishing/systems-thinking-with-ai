import pytest

from chapters.chapter_06_two_sketches.code.aggregate import mean_wait, run_aggregate
from chapters.chapter_06_two_sketches.code.queueing import (
    run_queue,
    wait_percentile,
    wait_summary,
)

UNDERLOADED = {"arrivals": 9.0, "capacity": 10.0}


def test_the_aggregate_sketch_reports_no_queue_below_capacity() -> None:
    path = run_aggregate([UNDERLOADED["arrivals"]] * 200, UNDERLOADED["capacity"])
    assert max(path) == pytest.approx(0.0)
    assert mean_wait(path, UNDERLOADED["capacity"]) == pytest.approx(0.0)


def test_the_queue_sketch_reports_real_waits_on_the_same_averages() -> None:
    """The chapter's argument: averaging removed the thing that produces the wait."""
    waits = run_queue(
        arrivals_per_period=UNDERLOADED["arrivals"],
        servers=int(UNDERLOADED["capacity"]),
        service_time=1.0,
        periods=200,
        seed=11,
    )
    summary = wait_summary(waits)
    assert summary["mean"] > 0.25
    assert summary["p90"] > 1.0


def test_the_aggregate_sketch_does_build_a_queue_above_capacity() -> None:
    path = run_aggregate([14.0] * 50, 10.0)
    assert path[-1] > path[0]
    assert all(path[i + 1] >= path[i] for i in range(len(path) - 1))


def test_the_queue_run_is_reproducible_from_its_seed() -> None:
    kwargs = {
        "arrivals_per_period": 9.0,
        "servers": 10,
        "service_time": 1.0,
        "periods": 60,
    }
    assert run_queue(seed=3, **kwargs) == run_queue(seed=3, **kwargs)
    assert run_queue(seed=3, **kwargs) != run_queue(seed=4, **kwargs)


def test_adding_a_server_shortens_the_tail_more_than_the_mean() -> None:
    base = {"arrivals_per_period": 9.0, "service_time": 1.0, "periods": 300, "seed": 5}
    tight = wait_summary(run_queue(servers=10, **base))
    loose = wait_summary(run_queue(servers=12, **base))
    assert loose["p99"] < tight["p99"]
    assert (tight["p99"] - loose["p99"]) > (tight["mean"] - loose["mean"])


def test_percentiles_are_ordered() -> None:
    waits = run_queue(
        arrivals_per_period=9.0, servers=10, service_time=1.0, periods=200, seed=7
    )
    assert wait_percentile(waits, 50.0) <= wait_percentile(waits, 90.0)
    assert wait_percentile(waits, 90.0) <= wait_percentile(waits, 99.0)


def test_both_sketches_reject_impossible_configurations() -> None:
    with pytest.raises(ValueError):
        run_aggregate([], 10.0)
    with pytest.raises(ValueError):
        run_queue(arrivals_per_period=9.0, servers=0, service_time=1.0, periods=10, seed=1)
    with pytest.raises(ValueError):
        wait_percentile([1.0, 2.0], 100.0)
