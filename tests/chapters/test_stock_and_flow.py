import pytest

from chapters.chapter_04_stock_and_flow.code.stock import (
    advance_stock,
    apply_floor,
    conservation_error,
    integrate,
    net_flow,
)


def test_equal_flows_leave_the_stock_unchanged() -> None:
    assert advance_stock(stock=100.0, inflow=25.0, outflow=25.0, dt=1.0) == 100.0


def test_a_falling_inflow_can_still_raise_the_stock() -> None:
    """The chapter's central claim, as an executable test."""
    inflows = [10.0, 9.0, 8.0, 7.0, 6.0]
    outflows = [4.0, 4.0, 4.0, 4.0, 4.0]
    path = integrate(initial=50.0, inflows=inflows, outflows=outflows)
    assert all(inflows[i + 1] < inflows[i] for i in range(len(inflows) - 1))
    assert all(path[i + 1] > path[i] for i in range(len(path) - 1))


def test_a_rising_inflow_can_still_lower_the_stock() -> None:
    path = integrate(initial=50.0, inflows=[1.0, 2.0, 3.0], outflows=[9.0, 9.0, 9.0])
    assert path[-1] < path[0]


def test_reconstructed_path_conserves_its_flow_history() -> None:
    inflows = [3.0, 7.5, 0.0, 12.25]
    outflows = [1.0, 1.0, 6.0, 2.5]
    path = integrate(initial=20.0, inflows=inflows, outflows=outflows, dt=0.5)
    assert conservation_error(path, inflows, outflows, dt=0.5) == pytest.approx(0.0)


def test_conservation_check_catches_a_tampered_path() -> None:
    inflows = [5.0, 5.0]
    outflows = [1.0, 1.0]
    path = integrate(initial=0.0, inflows=inflows, outflows=outflows)
    path[-1] += 10.0
    assert conservation_error(path, inflows, outflows) == pytest.approx(10.0)


def test_net_flow_is_the_rate_not_the_level() -> None:
    assert net_flow(inflow=8.0, outflow=3.0) == 5.0


def test_floor_holds_a_stock_at_a_physical_bound() -> None:
    assert apply_floor(-4.0) == 0.0
    assert apply_floor(12.0) == 12.0
    assert apply_floor(-4.0, floor=-10.0) == -4.0


def test_mismatched_records_are_rejected_rather_than_guessed() -> None:
    with pytest.raises(ValueError):
        integrate(initial=0.0, inflows=[1.0, 2.0], outflows=[1.0])
    with pytest.raises(ValueError):
        integrate(initial=0.0, inflows=[], outflows=[])
    with pytest.raises(ValueError):
        conservation_error([0.0, 1.0, 2.0], [1.0], [0.0])
