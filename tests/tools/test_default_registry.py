from pathlib import Path

from stai.contracts.common import ToolStatus
from stai.contracts.io import load_yaml
from stai.contracts.tooling import ToolPolicy
from stai.tools.defaults import build_default_registry

ROOT = Path(__file__).resolve().parents[2]


def test_default_registry_uses_catalog_policy_and_typed_request() -> None:
    policy = load_yaml(ROOT / "cases/factory-cycle/tool-policy.yaml", ToolPolicy)

    response = build_default_registry(ROOT).execute(
        "model.validate",
        {"model_path": str(ROOT / "models/factory-cycle.yaml")},
        policy,
    )

    assert response.status is ToolStatus.SUCCESS
    assert response.artifacts == [str(ROOT / "models/factory-cycle.yaml")]


def test_default_registry_rejects_unrecognized_payload_fields() -> None:
    policy = load_yaml(ROOT / "cases/factory-cycle/tool-policy.yaml", ToolPolicy)

    response = build_default_registry(ROOT).execute(
        "model.validate",
        {
            "model_path": str(ROOT / "models/factory-cycle.yaml"),
            "unrecognized": "must not be silently ignored",
        },
        policy,
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "input payload" in response.error.root_cause.lower()


def test_default_registry_validates_a_non_executable_policy_proposal() -> None:
    policy = load_yaml(ROOT / "cases/factory-cycle/tool-policy.yaml", ToolPolicy)

    response = build_default_registry(ROOT).execute(
        "policy.validate",
        {"proposal_path": str(ROOT / "cases/factory-cycle/policy-proposal.yaml")},
        policy,
    )

    assert response.status is ToolStatus.SUCCESS
    assert response.details["external_execution_requested"] is False


def test_default_registry_refuses_a_case_disallowed_tool() -> None:
    response = build_default_registry(ROOT).execute(
        "simulation.run",
        {
            "model_path": str(ROOT / "models/factory-cycle.yaml"),
            "experiment_path": str(ROOT / "cases/factory-cycle/experiments/baseline.yaml"),
            "output_path": str(ROOT / "experiments/factory-cycle/baseline.json"),
        },
        ToolPolicy(
            case_id="factory-cycle",
            allowed_tools=["model.validate"],
            write_roots=["experiments/factory-cycle"],
            allow_external_actions=False,
        ),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "not allowed" in response.error.root_cause.lower()


def test_default_registry_refuses_writes_outside_the_case_root(tmp_path: Path) -> None:
    policy = load_yaml(ROOT / "cases/factory-cycle/tool-policy.yaml", ToolPolicy)

    response = build_default_registry(ROOT).execute(
        "simulation.run",
        {
            "model_path": str(ROOT / "models/factory-cycle.yaml"),
            "experiment_path": str(ROOT / "cases/factory-cycle/experiments/baseline.yaml"),
            "output_path": str(tmp_path / "outside-policy.json"),
        },
        policy,
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "outside the case policy write roots" in response.error.root_cause.lower()


def test_default_registry_refuses_a_case_policy_that_escapes_the_repository() -> None:
    response = build_default_registry(ROOT).execute(
        "simulation.run",
        {
            "model_path": str(ROOT / "models/factory-cycle.yaml"),
            "experiment_path": str(ROOT / "cases/factory-cycle/experiments/baseline.yaml"),
            "output_path": str(ROOT / "experiments/factory-cycle/baseline.json"),
        },
        ToolPolicy(
            case_id="factory-cycle",
            allowed_tools=["simulation.run"],
            write_roots=["../outside-repository"],
            allow_external_actions=False,
        ),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "outside the repository" in response.error.root_cause.lower()
