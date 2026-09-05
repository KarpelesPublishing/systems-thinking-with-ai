from pathlib import Path

from stai.cli import main

ROOT = Path(__file__).resolve().parents[1]


def test_validate_model_command_returns_zero(capsys) -> None:
    code = main(["validate-model", str(ROOT / "models/factory-cycle.yaml")])
    output = capsys.readouterr().out

    assert code == 0
    assert '"status": "success"' in output


def test_simulate_command_writes_replay_record(tmp_path: Path, capsys) -> None:
    output_path = tmp_path / "factory-cycle-replay.json"
    code = main(
        [
            "simulate",
            str(ROOT / "models/factory-cycle.yaml"),
            str(ROOT / "cases/factory-cycle/experiments/baseline.yaml"),
            str(output_path),
        ]
    )
    capsys.readouterr()

    assert code == 0
    assert output_path.exists()


def test_validate_model_command_returns_a_typed_error_for_a_missing_file(
    tmp_path: Path,
    capsys,
) -> None:
    code = main(["validate-model", str(tmp_path / "missing.yaml")])
    output = capsys.readouterr().out

    assert code == 1
    assert '"status": "error"' in output
    assert '"stop_condition"' in output
