from pathlib import Path

from stai.contracts.io import load_yaml
from stai.contracts.model import ModelSpec
from stai.contracts.problem import ProblemContract
from stai.contracts.tooling import ToolCatalog
from stai.tools.unique.evidence_validate import validate_evidence
from stai.tools.unique.model_compile import compile_model_file
from stai.tools.unique.model_validate import validate_model_file
from stai.tools.unique.policy_validate import validate_policy_proposal
from stai.tools.unique.problem_validate import validate_problem_contract
from stai.tools.unique.simulation_run import run_simulation
from stai.tools.unique.verification_run import run_verification

ROOT = Path(__file__).resolve().parents[2]


def test_each_catalog_tool_has_an_individually_importable_module() -> None:
    functions = (
        validate_problem_contract,
        validate_evidence,
        validate_model_file,
        compile_model_file,
        validate_policy_proposal,
        run_simulation,
        run_verification,
    )

    assert all(callable(function) for function in functions)


def test_unique_problem_tool_preserves_teaching_reconstruction_boundary() -> None:
    contract = load_yaml(ROOT / "cases/factory-cycle/problem-contract.yaml", ProblemContract)

    response = validate_problem_contract(contract)

    assert response.status.value == "success"
    assert "teaching_reconstruction" in response.details["evidence_mode"]


def test_unique_model_tools_use_the_checked_in_factory_cycle_model() -> None:
    model_path = ROOT / "models/factory-cycle.yaml"

    validation = validate_model_file(model_path)
    compilation = compile_model_file(model_path)

    assert validation.status.value == "success"
    assert compilation.status.value == "success"
    assert load_yaml(model_path, ModelSpec).model_id == "factory-cycle"


def test_catalog_points_to_each_unique_tool_implementation() -> None:
    catalog = load_yaml(ROOT / "tooling/catalog.yaml", ToolCatalog)

    for definition in catalog.tools:
        implementation = ROOT / definition.implementation_path
        assert implementation.is_file()
        assert str(definition.tool_id.replace(".", "_")) in implementation.stem
