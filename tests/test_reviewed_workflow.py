"""Executable acceptance checks for the offline teaching workflow."""

import importlib
import importlib.util
import subprocess
import sys
from dataclasses import asdict

import pytest


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
