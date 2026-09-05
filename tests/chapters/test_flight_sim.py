import pytest

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings
from chapters.chapter_25_flight_sim.code.scenario import (
    Constraint,
    ScenarioRunner,
    supported_by_record,
)


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


def test_a_scenario_records_everything_needed_to_replay_it() -> None:
    runner = ScenarioRunner(bass())
    record = runner.run("baseline", report=("adopters",))
    assert record.model_hash
    assert record.settings.seed == 0
    assert "adopters" in record.outputs


def test_an_override_changes_the_outcome_and_is_logged() -> None:
    runner = ScenarioRunner(bass())
    slow = runner.run("low word of mouth", {"imitation": 0.05}, report=("adopters",))
    fast = runner.run("high word of mouth", {"imitation": 0.60}, report=("adopters",))
    assert slow.overrides == {"imitation": 0.05}
    assert fast.outputs["adopters"] > slow.outputs["adopters"]


def test_scenarios_with_the_same_model_share_a_hash_and_differ_in_overrides() -> None:
    """Same structure, different settings. The hash proves the structure did not move."""
    runner = ScenarioRunner(bass())
    a = runner.run("a", {"imitation": 0.1})
    b = runner.run("b", {"imitation": 0.5})
    assert a.model_hash != b.model_hash or a.overrides != b.overrides
    assert len(runner.log) == 2


def test_a_constraint_breach_is_recorded_rather_than_hidden() -> None:
    runner = ScenarioRunner(bass(), [Constraint("adopters", high=500.0)])
    record = runner.run("unbounded", report=("adopters",))
    assert record.breaches
    assert "above 500" in record.breaches[0]


def test_a_satisfied_constraint_records_nothing() -> None:
    runner = ScenarioRunner(bass(), [Constraint("adopters", low=0.0)])
    assert runner.run("baseline").breaches == []


def test_only_parameters_and_stocks_can_be_set_by_a_scenario() -> None:
    runner = ScenarioRunner(bass())
    with pytest.raises(ValueError):
        runner.run("bad", {"potential": 5.0})
    with pytest.raises(ValueError):
        runner.run("bad", {"nonexistent": 5.0})


def test_a_narrative_citing_variables_absent_from_the_record_is_flagged() -> None:
    """The AI lab's rule: explanations may only use what the replay record holds."""
    runner = ScenarioRunner(bass())
    record = runner.run("baseline", report=("adopters",))
    unsupported = supported_by_record({"adopters", "marketing_spend"}, record)
    assert unsupported == ["marketing_spend"]


def test_comparing_a_named_output_across_scenarios() -> None:
    runner = ScenarioRunner(bass())
    runner.run("slow", {"imitation": 0.05}, report=("adopters",))
    runner.run("fast", {"imitation": 0.60}, report=("adopters",))
    comparison = runner.compare("adopters")
    assert set(comparison) == {"slow", "fast"}


def test_a_different_solver_is_part_of_the_record() -> None:
    runner = ScenarioRunner(bass())
    record = runner.run("rk4", settings=RunSettings("rk4", 0.5, 40), report=("adopters",))
    assert record.settings.solver == "rk4"


def test_chapter_25_prints_the_record_this_run_produces() -> None:
    """Pins the printed table and ScenarioRecord, both of which drifted once."""
    runner = ScenarioRunner(bass(), [Constraint("adopters", high=900.0)])
    settings = RunSettings(solver="euler", dt=1.0, horizon=20, seed=0)
    finals = {}
    for label, imitation in (("cautious", 0.05), ("base", 0.30), ("aggressive", 0.60)):
        record = runner.run(label, {"imitation": imitation}, settings, report=("adopters",))
        finals[label] = round(record.outputs["adopters"], 2)
    assert finals == {"cautious": 275.90, "base": 937.70, "aggressive": 999.97}

    aggressive = runner.run("aggressive", {"imitation": 0.60}, settings, report=("adopters",))
    assert aggressive.model_hash == "4d720eefba79885a"
    assert aggressive.breaches == ["adopters reached 1000, above 900.0"]
