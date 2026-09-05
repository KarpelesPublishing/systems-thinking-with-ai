import pytest

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime


def bass() -> ModelDocument:
    return ModelDocument("bass", "1.0.0", horizon=40, variables=[
        Variable("adopters", "stock", "people", value=1.0),
        Variable("total_market", "parameter", "people", value=1000.0),
        Variable("innovation", "parameter", "1/week", value=0.01),
        Variable("imitation", "parameter", "1/week", value=0.30),
        Variable("potential", "auxiliary", "people", "total_market - adopters"),
        Variable("adoption", "flow", "people/week",
                 "(innovation + imitation * adopters / total_market) * potential",
                 target="adopters", sign=1),
    ])


def test_the_first_step_matches_a_hand_calculation() -> None:
    """(0.01 + 0.30 * 1/1000) * 999 = 10.2897, so adopters go 1.0 -> 11.2897."""
    result = Runtime(bass(), RunSettings("euler", dt=1.0, horizon=40)).run()
    assert result.series["adoption"][0] == pytest.approx(10.2897, abs=1e-4)
    assert result.series["adopters"][1] == pytest.approx(11.2897, abs=1e-4)


def test_adoption_saturates_at_the_market() -> None:
    result = Runtime(bass(), RunSettings("rk4", dt=0.5, horizon=40)).run()
    assert result.final("adopters") == pytest.approx(1000.0, abs=1.0)
    assert max(result.series["adopters"]) <= 1000.5


def test_the_result_carries_the_hash_and_the_settings_that_produced_it() -> None:
    settings = RunSettings("euler", dt=0.25, horizon=10)
    result = Runtime(bass(), settings).run()
    assert result.model_hash == bass().hash()
    assert result.settings is settings


def test_two_runs_of_the_same_model_and_settings_agree() -> None:
    a = Runtime(bass(), RunSettings("euler", 1.0, 40)).run()
    b = Runtime(bass(), RunSettings("euler", 1.0, 40)).run()
    assert a.series["adopters"] == b.series["adopters"]


def test_the_runtime_refuses_a_model_that_does_not_validate() -> None:
    broken = bass()
    broken.variables[-1] = Variable("adoption", "flow", "people/week", "potential * 0.1")
    with pytest.raises(ValueError):
        Runtime(broken)


def test_a_checkpoint_holds_the_whole_state() -> None:
    runtime = Runtime(bass())
    assert set(runtime.checkpoint()) == {"adopters"}
    runtime.restore({"adopters": 500.0})
    assert runtime.derivatives({"adopters": 500.0})["adopters"] > 0
    with pytest.raises(ValueError):
        runtime.restore({"wrong": 1.0})


def test_a_negative_sign_flow_removes_from_its_stock() -> None:
    document = bass()
    document.variables[-1] = Variable(
        "churn", "flow", "people/week", "adopters * 0.1", target="adopters", sign=-1)
    result = Runtime(document, RunSettings("euler", 1.0, 10)).run()
    assert result.final("adopters") < 1.0


def test_bad_run_settings_are_refused() -> None:
    with pytest.raises(ValueError):
        RunSettings(solver="magic")
    with pytest.raises(ValueError):
        RunSettings(dt=0.0)


def test_a_failure_during_a_run_names_the_time_it_happened_at() -> None:
    """A trajectory-dependent failure cannot be caught before the run, so it carries the time."""
    document = ModelDocument("divider", "1.0.0", horizon=4, variables=[
        Variable("level", "stock", "units", value=2.0),
        Variable("drain", "flow", "units/week", "1.0", target="level", sign=-1),
        Variable("ratio", "auxiliary", "1/units", "1.0 / level"),
    ])
    with pytest.raises(RuntimeError, match=r"run failed at time 2: "):
        Runtime(document, RunSettings("euler", dt=1.0, horizon=4)).run()


def saturating() -> ModelDocument:
    """A load-dependent effectiveness curve, expressed in the document itself."""
    return ModelDocument("saturating", "1.0.0", horizon=10, variables=[
        Variable("work", "stock", "items", value=10.0),
        Variable("capacity", "parameter", "items/week", value=5.0),
        Variable("load", "auxiliary", "dimensionless", "work / capacity"),
        Variable("effectiveness", "lookup", "dimensionless", "load",
                 points=((0.0, 1.0), (1.0, 0.8), (2.0, 0.5), (5.0, 0.2))),
        Variable("done", "flow", "items/week", "capacity * effectiveness",
                 target="work", sign=-1),
    ])


def test_a_lookup_is_a_variable_the_runtime_can_evaluate() -> None:
    """Chapter 15's shape, carried in the document instead of beside it."""
    result = Runtime(saturating(), RunSettings("euler", dt=1.0, horizon=2)).run()
    # load starts at 2.0, so effectiveness starts on the curve's 0.5 point.
    assert result.series["effectiveness"][0] == pytest.approx(0.5)
    assert result.series["done"][0] == pytest.approx(2.5)
    assert result.series["work"][1] == pytest.approx(7.5)
    # Work drains, load falls, and effectiveness rises along the curve.
    assert result.series["effectiveness"][1] > result.series["effectiveness"][0]


def test_a_lookup_refuses_an_input_outside_its_observed_domain() -> None:
    document = saturating()
    document.variables[0] = Variable("work", "stock", "items", value=100.0)
    with pytest.raises(RuntimeError, match="run failed at time 0"):
        Runtime(document, RunSettings("euler", dt=1.0, horizon=4)).run()


def delayed() -> ModelDocument:
    """A first-order delay between an order and its arrival."""
    return ModelDocument("delayed", "1.0.0", horizon=20, variables=[
        Variable("stock", "stock", "units", value=0.0),
        Variable("ordering", "parameter", "units/week", value=10.0),
        Variable("arriving", "delay", "units/week", "ordering", delay_time=4.0),
        Variable("inflow", "flow", "units/week", "arriving", target="stock", sign=1),
    ])


def test_a_delay_carries_its_own_level_through_the_solver() -> None:
    """Chapter 16's first-order delay, as a document the ordinary runtime advances."""
    result = Runtime(delayed(), RunSettings("euler", dt=1.0, horizon=40)).run()
    assert result.series["arriving"][0] == pytest.approx(0.0)
    # It approaches the input rate it is fed, and never overshoots it.
    assert result.series["arriving"][-1] == pytest.approx(10.0, abs=0.05)
    assert max(result.series["arriving"]) <= 10.0


def test_a_cycle_through_a_delay_is_legitimate() -> None:
    """A delay closes over a time step, so a loop through one is not an algebraic loop."""
    document = ModelDocument("controlled", "1.0.0", horizon=10, variables=[
        Variable("level", "stock", "units", value=0.0),
        Variable("target", "parameter", "units", value=100.0),
        Variable("gap", "auxiliary", "units", "target - level"),
        Variable("ordered", "delay", "units/week", "gap / 10.0", delay_time=3.0),
        Variable("filling", "flow", "units/week", "ordered", target="level", sign=1),
    ])
    result = Runtime(document, RunSettings("euler", dt=1.0, horizon=60)).run()
    assert result.final("level") > 50.0


def test_a_field_at_its_default_is_not_inside_the_hash() -> None:
    """Adding a schema field must not change what an older document hashes to."""
    spelled_out = Variable("x", "auxiliary", "units", "1.0", value=None, evidence="assumed",
                           note="", target="", sign=1, points=(), delay_time=None)
    implied = Variable("x", "auxiliary", "units", "1.0")
    one = ModelDocument("m", "1.0.0", horizon=1, variables=[
        Variable("s", "stock", "units", value=0.0),
        Variable("f", "flow", "units/week", "1.0", target="s"), spelled_out])
    two = ModelDocument("m", "1.0.0", horizon=1, variables=[
        Variable("s", "stock", "units", value=0.0),
        Variable("f", "flow", "units/week", "1.0", target="s"), implied])
    assert one.hash() == two.hash()


def test_the_document_delay_matches_chapter_15s_own_delay() -> None:
    """The document expresses Chapter 16's law, so Chapter 16's pack is the oracle."""
    from chapters.chapter_16_delays.code.delays import run_first_order

    result = Runtime(delayed(), RunSettings("euler", dt=1.0, horizon=10)).run()
    from_document = [round(x, 9) for x in result.series["arriving"]]
    from_pack = [round(x, 9) for x in run_first_order([10.0] * 11, mean=4.0)]
    assert from_document == from_pack


def test_the_runtime_takes_its_step_and_horizon_from_the_document() -> None:
    """A semantic choice recorded in the document and ignored by the runtime is decoration."""
    document = ModelDocument("quarterly", "1.0.0", horizon=8, time_step=0.25, variables=[
        Variable("level", "stock", "units", value=0.0),
        Variable("fill", "flow", "units/week", "1.0", target="level", sign=1),
    ])
    result = Runtime(document).run()
    assert result.settings.dt == 0.25
    assert result.settings.horizon == 8.0
    assert result.times[1] == pytest.approx(0.25)
    assert result.final("level") == pytest.approx(8.0)


def test_explicit_settings_still_win_over_the_document() -> None:
    """A run may override, and then it has said so on the record."""
    document = ModelDocument("quarterly", "1.0.0", horizon=8, time_step=0.25, variables=[
        Variable("level", "stock", "units", value=0.0),
        Variable("fill", "flow", "units/week", "1.0", target="level", sign=1),
    ])
    result = Runtime(document, RunSettings("euler", dt=1.0, horizon=4)).run()
    assert result.settings.dt == 1.0
    assert result.times[1] == pytest.approx(1.0)
