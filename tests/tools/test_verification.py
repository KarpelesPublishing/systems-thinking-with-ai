from pathlib import Path

import yaml

from stai.contracts.common import ToolStatus
from stai.tools.simulation import run_simulation
from stai.tools.verification import run_verification

ROOT = Path(__file__).resolve().parents[2]


def test_factory_verification_runs_required_deterministic_checks(tmp_path: Path) -> None:
    output_path = tmp_path / "factory-cycle-verification.json"

    response = run_verification(
        ROOT / "models/factory-cycle.yaml",
        ROOT / "cases/factory-cycle/experiments/baseline.yaml",
        output_path,
    )

    assert response.status is ToolStatus.SUCCESS
    assert response.details["checks"] == {
        "structural": "passed",
        "extreme_condition": "passed",
        "conservation": "passed",
        "regression": "passed",
    }
    assert output_path.exists()


def test_simulation_rejects_an_experiment_for_another_model(tmp_path: Path) -> None:
    experiment_path = tmp_path / "wrong-experiment.yaml"
    experiment_path.write_text(
        yaml.safe_dump(
            {
                "experiment_id": "wrong-model",
                "model_id": "another-model",
                "horizon": 24.0,
                "parameter_overrides": {},
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )

    response = run_simulation(
        ROOT / "models/factory-cycle.yaml",
        experiment_path,
        tmp_path / "result.json",
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "does not match" in response.error.root_cause.lower()
