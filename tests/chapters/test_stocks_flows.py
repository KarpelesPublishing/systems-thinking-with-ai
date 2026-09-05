import pytest

from chapters.chapter_12_stocks_flows.code.system import (
    SINK,
    SOURCE,
    Flow,
    System,
    conservation_residual,
    total_in_system,
)


def bathtub() -> System:
    return System(
        stocks={"tub": 50.0},
        flows=[Flow("tap", SOURCE, "tub", "litres/minute"),
               Flow("drain", "tub", SINK, "litres/minute")],
        unit="litres",
    )


def test_a_well_formed_system_reports_no_problems() -> None:
    assert bathtub().check() == []


def test_a_stock_with_no_outflow_is_reported() -> None:
    """The missing-sink defect: a stock that can only grow."""
    system = System(stocks={"tub": 50.0}, flows=[Flow("tap", SOURCE, "tub", "litres/minute")],
                    unit="litres")
    assert system.unsunk_stocks() == ["tub"]
    assert any("no outflow" in p for p in system.check())


def test_a_stock_with_no_inflow_is_reported() -> None:
    system = System(stocks={"tub": 50.0}, flows=[Flow("drain", "tub", SINK, "litres/minute")],
                    unit="litres")
    assert system.unsourced_stocks() == ["tub"]


def test_a_flow_to_an_undeclared_endpoint_is_caught_before_running() -> None:
    system = bathtub()
    system.flows = system.flows + [Flow("leak", "tub", "basement", "litres/minute")]
    assert system.dangling() == ["leak"]


def test_a_flow_whose_unit_is_not_a_rate_is_rejected() -> None:
    with pytest.raises(ValueError):
        Flow("tap", SOURCE, "tub", "litres")


def test_a_mismatched_flow_unit_is_reported() -> None:
    system = bathtub()
    system.flows = system.flows + [Flow("spill", "tub", SINK, "gallons/minute")]
    assert any("does not match" in p for p in system.check())


def test_a_closed_transfer_conserves_the_total() -> None:
    system = System(
        stocks={"checking": 100.0, "savings": 0.0},
        flows=[Flow("transfer", "checking", "savings", "dollars/week")],
        unit="dollars",
    )
    after = system.step({"transfer": 25.0})
    assert total_in_system(after) == pytest.approx(total_in_system(system))
    assert conservation_residual(system, after, {"transfer": 25.0}) == pytest.approx(0.0)


def test_flows_crossing_the_boundary_are_accounted_for() -> None:
    system = bathtub()
    rates = {"tap": 10.0, "drain": 4.0}
    after = system.step(rates)
    assert after.stocks["tub"] == pytest.approx(56.0)
    assert conservation_residual(system, after, rates) == pytest.approx(0.0)


def test_stepping_without_every_rate_is_refused() -> None:
    with pytest.raises(ValueError):
        bathtub().step({"tap": 10.0})
