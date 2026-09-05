import pytest

from chapters.chapter_02_factory_cycle.code.advance_factory_cycle import advance_factory_cycle
from chapters.chapter_02_factory_cycle.code.advance_stock import advance_stock
from chapters.chapter_02_factory_cycle.code.complete_production import complete_production
from chapters.chapter_02_factory_cycle.code.desired_inventory import desired_inventory
from chapters.chapter_02_factory_cycle.code.inventory_gap import inventory_gap
from chapters.chapter_02_factory_cycle.code.models import FactoryCycleParameters, FactoryCycleState
from chapters.chapter_02_factory_cycle.code.run_factory_cycle import run_factory_cycle
from chapters.chapter_02_factory_cycle.code.ship_orders import ship_orders
from chapters.chapter_02_factory_cycle.code.start_production import start_production


def test_advance_stock_applies_inflows_and_outflows_for_one_step() -> None:
    assert advance_stock(stock=12.0, inflow=10.0, outflow=10.0, dt=0.25) == 12.0


def test_factory_cycle_atoms_match_the_baseline_equations() -> None:
    assert desired_inventory(order_rate=10.0, coverage=2.0) == 20.0
    assert inventory_gap(desired=20.0, current=12.0) == 8.0
    assert start_production(order_rate=10.0, gap=8.0, adjustment_time=1.0) == 18.0
    assert complete_production(work_in_process=40.0, production_delay=4.0) == 10.0
    assert ship_orders(order_rate=10.0) == 10.0


def test_composition_function_assembles_one_factory_cycle_step() -> None:
    state = FactoryCycleState(inventory=12.0, work_in_process=40.0)
    parameters = FactoryCycleParameters(
        order_rate=10.0,
        desired_coverage=2.0,
        inventory_adjustment_time=1.0,
        production_delay=4.0,
    )

    step = advance_factory_cycle(state, parameters, dt=0.25)

    assert step.state == FactoryCycleState(inventory=12.0, work_in_process=42.0)
    assert step.rates == {
        "start_production": 18.0,
        "complete_production": 10.0,
        "ship_orders": 10.0,
    }


def test_run_factory_cycle_returns_initial_and_final_rows() -> None:
    state = FactoryCycleState(inventory=12.0, work_in_process=40.0)
    parameters = FactoryCycleParameters(
        order_rate=10.0,
        desired_coverage=2.0,
        inventory_adjustment_time=1.0,
        production_delay=4.0,
    )

    rows = run_factory_cycle(state, parameters, horizon=0.5, dt=0.25)

    assert len(rows) == 3
    assert rows[0]["time"] == 0.0
    assert rows[-1]["time"] == 0.5
    assert rows[-1]["inventory"] >= 0.0
    assert rows[-1]["work_in_process"] >= 0.0


@pytest.mark.parametrize(
    ("function", "kwargs"),
    [
        (advance_stock, {"stock": 1.0, "inflow": 1.0, "outflow": 0.0, "dt": -0.1}),
        (start_production, {"order_rate": 1.0, "gap": 0.0, "adjustment_time": 0.0}),
        (complete_production, {"work_in_process": 1.0, "production_delay": 0.0}),
    ],
)
def test_factory_cycle_atoms_reject_invalid_time_inputs(function, kwargs) -> None:
    with pytest.raises(ValueError):
        function(**kwargs)
