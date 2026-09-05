import math
from pathlib import Path

from stai.compiler.model import compile_model
from stai.contracts.common import ToolError, ToolResponse, ToolStatus
from stai.contracts.io import load_yaml
from stai.contracts.model import ExperimentSpec, ModelSpec
from stai.provenance.replay import canonical_hash
from stai.runtime.stock_flow import SimulationResult, simulate
from stai.tools.unique.simulation_run import run_simulation


def _verification_error(summary: str, checks: dict[str, str]) -> ToolResponse:
    return ToolResponse(
        status=ToolStatus.ERROR,
        summary=summary,
        next_actions=["Repair the model or experiment and rerun verification."],
        artifacts=[],
        details={"checks": checks},
        error=ToolError(
            root_cause=summary,
            safe_retry="Repair the model or experiment and rerun verification.",
            stop_condition=(
                "Do not promote this artifact until every required verification check passes."
            ),
        ),
    )


def _stock_values_are_nonnegative(model: ModelSpec, result: SimulationResult) -> bool:
    stock_names = {stock.name for stock in model.stocks}
    return all(
        value >= 0.0
        for row in result.rows
        for name, value in row.items()
        if name in stock_names
    )


def _all_values_are_finite(result: SimulationResult) -> bool:
    return all(math.isfinite(value) for row in result.rows for value in row.values())


def _conservation_holds(model: ModelSpec, result: SimulationResult) -> bool:
    stock_names = {stock.name for stock in model.stocks}
    flows = {flow.name: flow for flow in model.flows}
    for before, after in zip(result.rows, result.rows[1:]):
        observed_delta = sum(after[name] - before[name] for name in stock_names)
        external_delta = 0.0
        for name, flow in flows.items():
            rate = before[name]
            if flow.source is None:
                external_delta += rate * model.time_step
            if flow.target is None:
                external_delta -= rate * model.time_step
        if not math.isclose(observed_delta, external_delta, abs_tol=1e-9):
            return False
    return True


def _extreme_rate_parameter(model: ModelSpec) -> str | None:
    if "order_rate" in model.parameters:
        return "order_rate"
    return next((name for name in sorted(model.parameters) if name.endswith("_rate")), None)


def run_verification(
    model_path: Path,
    experiment_path: Path,
    output_path: Path,
) -> ToolResponse:
    """Run deterministic structural, extreme, conservation, and replay checks."""
    model = load_yaml(model_path, ModelSpec)
    experiment = load_yaml(experiment_path, ExperimentSpec)
    checks = {
        "structural": "not_run",
        "extreme_condition": "not_run",
        "conservation": "not_run",
        "regression": "not_run",
    }
    if experiment.model_id != model.model_id:
        return _verification_error(
            f"Experiment {experiment.experiment_id} targets {experiment.model_id}, which does not "
            f"match model {model.model_id}.",
            checks,
        )
    try:
        compiled = compile_model(model)
    except (SyntaxError, ValueError) as error:
        return _verification_error(f"Structural verification failed: {error}", checks)

    checks["structural"] = "passed"
    baseline = simulate(
        compiled,
        horizon=experiment.horizon,
        parameter_overrides=experiment.parameter_overrides,
    )
    if baseline.status != "success":
        return _verification_error(f"Baseline simulation failed: {baseline.message}", checks)

    rate_parameter = _extreme_rate_parameter(model)
    if rate_parameter is None:
        return _verification_error(
            "Extreme-condition verification requires a stock-flow rate parameter ending in _rate.",
            checks,
        )
    extreme = simulate(
        compiled,
        horizon=experiment.horizon,
        parameter_overrides={**experiment.parameter_overrides, rate_parameter: 0.0},
    )
    if (
        extreme.status != "success"
        or not _stock_values_are_nonnegative(model, extreme)
        or not _all_values_are_finite(extreme)
    ):
        return _verification_error(
            f"Extreme-condition verification failed when {rate_parameter} was set to zero.",
            checks,
        )
    checks["extreme_condition"] = "passed"

    if not _conservation_holds(model, baseline):
        return _verification_error("Conservation verification failed.", checks)
    checks["conservation"] = "passed"

    repeated = simulate(
        compiled,
        horizon=experiment.horizon,
        parameter_overrides=experiment.parameter_overrides,
    )
    if (
        repeated.status != "success"
        or canonical_hash({"rows": baseline.rows}) != canonical_hash({"rows": repeated.rows})
    ):
        return _verification_error(
            "Regression verification failed: replay is not deterministic.",
            checks,
        )
    checks["regression"] = "passed"

    response = run_simulation(model_path, experiment_path, output_path)
    if response.status is ToolStatus.ERROR:
        return response
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary="Structural, extreme-condition, conservation, and regression checks passed.",
        next_actions=["Review the replay record and log unsupported conclusions as defects."],
        artifacts=response.artifacts,
        details={
            **response.details,
            "checks": checks,
            "extreme_parameter": rate_parameter,
        },
    )
