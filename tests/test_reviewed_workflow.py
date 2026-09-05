"""Executable acceptance checks for the offline teaching workflow."""

import importlib
import importlib.util
import subprocess
import sys
from dataclasses import asdict, replace
from io import StringIO

import pytest


@pytest.mark.parametrize("defect", ["missing", "misspelled", "duplicate", "unexpected"])
def test_input_row_ids_must_match_exactly(monkeypatch, defect):
    workflow = load_workflow()
    lines = (workflow.FIXTURES / "synthetic_inputs.csv").read_text().splitlines()
    if defect == "missing":
        del lines[1]
    elif defect == "misspelled":
        lines[1] = lines[1].replace("productive,", "productiv,")
    elif defect == "duplicate":
        lines.append(lines[1])
    else:
        lines.append("extra,1,assumed,Unexpected input")
    monkeypatch.setattr(workflow.Path, "open", lambda *a, **kw: StringIO("\n".join(lines)))
    with pytest.raises(ValueError, match="row IDs"):
        workflow.build_model()


def test_unexpected_review_field_is_rejected_before_construction():
    workflow = load_workflow()
    source = workflow.build_model()
    before = source.canonical()
    patch = workflow.Patch(source.hash(), [workflow.Edit(
        "change", "aggression", "Unexpected field", {"value": 0.1, "surprise": 1},
    )])
    decision = workflow.review(source, patch)
    assert decision["simulation_authorized"] is False
    assert decision["packet"]["applied"] is False
    assert "Only the recruiting response parameter is in scope" in decision["reasons"]
    assert source.canonical() == before


@pytest.mark.parametrize("balance", ["productive_balance_error", "trainee_balance_error"])
def test_balances_use_document_initial_state(monkeypatch, balance):
    workflow = load_workflow()
    source = workflow.build_model()
    source = replace(source, variables=[
        replace(v, value=25.0) if v.id == "productive" else
        replace(v, value=2.0) if v.id == "arriving" else v
        for v in source.variables
    ])
    monkeypatch.setattr(workflow, "build_model", lambda: source)
    for row in workflow.run_workflow()["runs"]:
        assert row[balance] == 0.0


def test_52_week_report_matches_independent_euler_recurrence():
    workflow = load_workflow()
    for row, aggression in zip(workflow.run_workflow()["runs"], [0.25, 0.1], strict=True):
        productive, trainees, peak = 20.0, 0.0, 20.0
        recruited = joined = departed = 0.0
        for _ in range(52):
            recruiting = max(0.0, 40.0 - productive) * aggression
            joining = trainees / 8.0
            leaving = productive * 0.01
            productive, trainees = (
                productive + joining - leaving,
                trainees + recruiting - joining,
            )
            peak = max(peak, productive)
            recruited += recruiting
            joined += joining
            departed += leaving
        expected = {
            "final_productive_people": productive,
            "peak_productive_people": peak,
            "final_trainees_people": trainees,
            "recruited_people": recruited,
            "joined_people": joined,
            "departed_people": departed,
            "recruiting_cost_usd": recruited * 1000,
        }
        for key, value in expected.items():
            assert row[key] == pytest.approx(value, rel=0, abs=0.00000051)


def load_workflow():
    assert importlib.util.find_spec("examples.reviewed_workflow") is not None, (
        "The offline reviewed workflow has not been implemented"
    )
    return importlib.import_module("examples.reviewed_workflow")


def test_deterministic_replay_and_recorded_cli():
    workflow = load_workflow()
    first = workflow.run_workflow()
    assert first == workflow.run_workflow()
    output = subprocess.check_output(
        [sys.executable, "-m", "examples.reviewed_workflow"], text=True
    )
    assert output == workflow.render_report(first)
    assert output == (workflow.FIXTURES / "expected_report.json").read_text()


def test_source_unchanged_and_stale_hash_rejected():
    workflow = load_workflow()
    source = workflow.build_model()
    before = source.canonical()
    patch = workflow.corrected_proposal(source)
    candidate = workflow.apply_patch(source, patch)
    assert source.canonical() == before
    assert candidate.hash() != source.hash()
    with pytest.raises(ValueError, match="written against"):
        workflow.apply_patch(candidate, patch)


def test_evidence_and_human_review():
    workflow = load_workflow()
    source = workflow.build_model()
    assert source.by_id("productive").evidence == "synthetic"
    assert all(v.evidence != "observed" for v in source.variables)
    flawed = workflow.flawed_proposal(source)
    assert workflow.review_packet(source, flawed)["valid"] is True
    decision = workflow.review(source, flawed)
    assert decision["simulation_authorized"] is False
    assert len(decision["reasons"]) == 2
    corrected = workflow.corrected_proposal(source)
    candidate = workflow.apply_patch(source, corrected)
    assert candidate.by_id("aggression").evidence == "proposed"
    assert workflow.review(source, corrected)["simulation_authorized"] is True
    promoted = workflow.Patch(source.hash(), [workflow.Edit(
        "change", "aggression", "Unsupported promotion",
        {"value": 0.1, "evidence": "observed"},
    )])
    assert workflow.review(source, promoted)["simulation_authorized"] is False


def test_numeric_results_balances_and_corrected_parameter():
    workflow = load_workflow()
    source = workflow.build_model()
    corrected = workflow.apply_patch(source, workflow.corrected_proposal(source))
    for model, aggression in [(source, 0.25), (corrected, 0.1)]:
        result = workflow.Runtime(model, workflow.settings()).run()
        assert asdict(result.settings) == {
            "solver": "euler", "dt": 1.0, "horizon": 52.0, "seed": 0,
        }
        assert result.times == list(range(53))
        assert set(result.series["aggression"]) == {aggression}
        assert result.series["productive"][:3] == pytest.approx([20, 19.8,
            19.8 + 20 * aggression / 8 - 0.198])
        dt = result.settings.dt
        recruited = sum(result.series["recruiting"][:-1]) * dt
        joined = sum(result.series["joining"][:-1]) * dt
        left = sum(result.series["leaving"][:-1]) * dt
        assert result.final("productive") == pytest.approx(20 + joined - left)
        assert result.final("arriving__level") == pytest.approx(recruited - joined)
        assert min(result.series["productive"]) >= 0
        if aggression == 0.25:
            assert max(result.series["productive"]) > 40
        else:
            assert max(result.series["productive"]) < 40
    report = workflow.run_workflow()
    for row in report["runs"]:
        assert row["recruiting_cost_usd"] == pytest.approx(
            row["recruited_people"] * 1000, abs=0.001
        )


def test_no_external_authority_and_bounded_scope():
    workflow = load_workflow()
    source = workflow.build_model()
    for patch in [workflow.flawed_proposal(source), workflow.corrected_proposal(source)]:
        decision = workflow.review(source, patch)
        assert decision["external_action_authorized"] is False
        assert decision["deployment_authorized"] is False
    for value in [-1, 0, 0.51, float("nan"), float("inf")]:
        patch = workflow.Patch(source.hash(), [workflow.Edit(
            "change", "aggression", "Out of bounds", {"value": value},
        )])
        assert workflow.review(source, patch)["simulation_authorized"] is False
    patch = workflow.Patch(source.hash(), [workflow.Edit(
        "change", "target", "Outside authorized lever", {"value": 50},
    )])
    assert workflow.review(source, patch)["simulation_authorized"] is False
    report = workflow.run_workflow()
    assert report["costs"]["api_calls"] == 0
    assert report["costs"]["api_cost_usd"] == 0
