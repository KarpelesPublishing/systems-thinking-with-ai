import json
from pathlib import Path

from stai.compiler.model import compile_model
from stai.contracts.common import ToolError, ToolResponse, ToolStatus
from stai.contracts.io import load_yaml
from stai.contracts.model import ExperimentSpec, ModelSpec
from stai.provenance.replay import create_replay_record
from stai.runtime.stock_flow import simulate


def _simulation_error(summary: str) -> ToolResponse:
    return ToolResponse(
        status=ToolStatus.ERROR,
        summary=summary,
        next_actions=["Repair the model or experiment before rerunning."],
        artifacts=[],
        error=ToolError(
            root_cause=summary,
            safe_retry="Repair the model or experiment before rerunning.",
            stop_condition="Do not review or promote a simulation result that failed at runtime.",
        ),
    )


def run_simulation(
    model_path: Path,
    experiment_path: Path,
    output_path: Path,
) -> ToolResponse:
    """Simulate locally and emit a deterministic replay record."""
    model = load_yaml(model_path, ModelSpec)
    experiment = load_yaml(experiment_path, ExperimentSpec)
    if experiment.model_id != model.model_id:
        return _simulation_error(
            f"Experiment {experiment.experiment_id} targets {experiment.model_id}, which does not "
            f"match model {model.model_id}."
        )
    result = simulate(
        compile_model(model),
        horizon=experiment.horizon,
        parameter_overrides=experiment.parameter_overrides,
    )
    if result.status != "success":
        return _simulation_error(result.message)

    replay = create_replay_record(
        model_payload=model.model_dump(mode="json"),
        experiment_payload=experiment.model_dump(mode="json"),
        result_payload={"rows": result.rows},
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(
            {
                "model_hash": replay.model_hash,
                "input_hash": replay.input_hash,
                "result_hash": replay.result_hash,
                "rows": result.rows,
            },
            allow_nan=False,
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary="Simulation completed and replay record written.",
        next_actions=["Run verification before reviewing a policy proposal."],
        artifacts=[str(output_path)],
        details={
            "model_hash": replay.model_hash,
            "input_hash": replay.input_hash,
            "result_hash": replay.result_hash,
        },
    )
