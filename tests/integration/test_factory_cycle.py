from pathlib import Path

from stai.compiler.model import compile_model
from stai.contracts.io import load_yaml
from stai.contracts.model import ExperimentSpec, ModelSpec, PolicyProposal
from stai.contracts.problem import ProblemContract
from stai.contracts.tooling import ToolPolicy
from stai.runtime.stock_flow import simulate

ROOT = Path(__file__).resolve().parents[2]


def test_factory_cycle_is_labeled_as_a_teaching_reconstruction() -> None:
    contract = load_yaml(ROOT / "cases/factory-cycle/problem-contract.yaml", ProblemContract)
    policy = load_yaml(ROOT / "cases/factory-cycle/tool-policy.yaml", ToolPolicy)

    assert contract.evidence_mode.value == "teaching_reconstruction"
    assert policy.allow_external_actions is False
    assert "simulation.run" in policy.allowed_tools


def test_factory_cycle_policy_proposal_stays_non_executable() -> None:
    proposal = load_yaml(ROOT / "cases/factory-cycle/policy-proposal.yaml", PolicyProposal)

    assert proposal.state.value == "proposed"
    assert proposal.external_execution_requested is False
    assert "policy.execute" not in load_yaml(
        ROOT / "cases/factory-cycle/tool-policy.yaml",
        ToolPolicy,
    ).allowed_tools


def test_factory_cycle_runs_without_negative_stocks() -> None:
    model = load_yaml(ROOT / "models/factory-cycle.yaml", ModelSpec)
    experiment = load_yaml(
        ROOT / "cases/factory-cycle/experiments/baseline.yaml",
        ExperimentSpec,
    )

    result = simulate(
        compile_model(model),
        horizon=experiment.horizon,
        parameter_overrides=experiment.parameter_overrides,
    )

    assert result.status == "success"
    assert len(result.rows) > 2
    assert all(
        value >= 0.0
        for row in result.rows
        for key, value in row.items()
        if key in {"inventory", "work_in_process"}
    )
