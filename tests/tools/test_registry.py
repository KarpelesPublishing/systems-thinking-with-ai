from pathlib import Path

import pytest
import yaml
from pydantic import BaseModel, Field, ValidationError

from stai.contracts.common import ToolResponse, ToolStatus
from stai.contracts.tooling import ToolCatalog, ToolDefinition, ToolPolicy
from stai.tools.registry import ToolRegistry


class ArtifactRequest(BaseModel):
    artifact_id: str = Field(min_length=1)


class OutputRequest(BaseModel):
    output_path: Path


def successful_handler(payload: ArtifactRequest | OutputRequest) -> ToolResponse:
    artifact = getattr(payload, "artifact_id", "output")
    return ToolResponse(
        status=ToolStatus.SUCCESS,
        summary=f"Handled {artifact}.",
        next_actions=["Review the generated artifact."],
        artifacts=["artifacts/example.json"],
    )


def raising_handler(payload: ArtifactRequest) -> ToolResponse:
    raise RuntimeError(f"Cannot handle {payload.artifact_id}.")


def invalid_response_handler(payload: ArtifactRequest) -> object:
    return "not-a-tool-response"


def build_registry(
    *,
    repository_root: Path | None = None,
    handler=successful_handler,
) -> ToolRegistry:
    definition = ToolDefinition(
        tool_id="model.validate",
        is_external=False,
        input_schema="ArtifactRequest",
        output_schema="ToolResponse",
    )
    return ToolRegistry(
        definitions={"model.validate": definition},
        input_models={"model.validate": ArtifactRequest},
        handlers={"model.validate": handler},
        repository_root=repository_root,
    )


def policy(*allowed_tools: str, write_roots: list[str] | None = None) -> ToolPolicy:
    return ToolPolicy(
        case_id="factory-cycle",
        allowed_tools=list(allowed_tools),
        write_roots=write_roots or ["experiments/factory-cycle"],
    )


def test_registry_denies_unknown_tool_without_calling_a_handler() -> None:
    response = build_registry().execute(
        "model.compile",
        {"artifact_id": "model"},
        policy("model.compile"),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "unknown tool" in response.error.root_cause.lower()
    assert "do not invoke" in response.error.stop_condition.lower()


def test_registry_denies_unauthorized_tool_before_handler_execution() -> None:
    calls: list[str] = []

    def recording_handler(payload: ArtifactRequest) -> ToolResponse:
        calls.append(payload.artifact_id)
        return successful_handler(payload)

    response = build_registry(handler=recording_handler).execute(
        "model.validate",
        {"artifact_id": "model"},
        policy(),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "not allowed" in response.summary.lower()
    assert "human review" in response.error.safe_retry.lower()
    assert calls == []


def test_registry_denies_external_action_even_when_listed_in_policy() -> None:
    definition = ToolDefinition(
        tool_id="policy.execute",
        is_external=True,
        input_schema="ArtifactRequest",
        output_schema="ToolResponse",
    )
    registry = ToolRegistry(
        definitions={"policy.execute": definition},
        input_models={"policy.execute": ArtifactRequest},
        handlers={"policy.execute": successful_handler},
    )

    response = registry.execute(
        "policy.execute",
        {"artifact_id": "policy"},
        policy("policy.execute"),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "external" in response.summary.lower()


def test_registry_runs_permitted_local_handler() -> None:
    response = build_registry().execute(
        "model.validate",
        {"artifact_id": "model"},
        policy("model.validate"),
    )

    assert response.status is ToolStatus.SUCCESS
    assert response.artifacts == ["artifacts/example.json"]


def test_registry_reports_invalid_typed_payload() -> None:
    response = build_registry().execute("model.validate", {}, policy("model.validate"))

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "input payload" in response.error.root_cause.lower()


def test_registry_converts_handler_exceptions_to_the_error_contract() -> None:
    response = build_registry(handler=raising_handler).execute(
        "model.validate",
        {"artifact_id": "model"},
        policy("model.validate"),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "runtimeerror" in response.error.root_cause.lower()
    assert "do not promote" in response.error.stop_condition.lower()


def test_registry_rejects_a_handler_result_that_is_not_a_tool_response() -> None:
    response = build_registry(handler=invalid_response_handler).execute(
        "model.validate",
        {"artifact_id": "model"},
        policy("model.validate"),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "toolresponse" in response.error.root_cause.lower()


def test_policy_cannot_enable_external_actions() -> None:
    with pytest.raises(ValidationError):
        ToolPolicy(
            case_id="factory-cycle",
            allowed_tools=[],
            write_roots=[],
            allow_external_actions=True,
        )


def test_writing_tool_requires_an_in_repository_authorized_path(tmp_path: Path) -> None:
    definition = ToolDefinition(
        tool_id="simulation.run",
        is_external=False,
        input_schema="OutputRequest",
        output_schema="ToolResponse",
        write_path_fields=["output_path"],
    )
    registry = ToolRegistry(
        definitions={"simulation.run": definition},
        input_models={"simulation.run": OutputRequest},
        handlers={"simulation.run": successful_handler},
        repository_root=tmp_path,
    )
    case_policy = policy("simulation.run")

    allowed = registry.execute(
        "simulation.run",
        {"output_path": "experiments/factory-cycle/baseline.json"},
        case_policy,
    )
    escaped = registry.execute(
        "simulation.run",
        {"output_path": "../outside.json"},
        case_policy,
    )

    assert allowed.status is ToolStatus.SUCCESS
    assert escaped.status is ToolStatus.ERROR
    assert escaped.error is not None
    assert "outside" in escaped.error.root_cause.lower()


def test_writing_tool_passes_a_resolved_in_root_path_to_its_handler(tmp_path: Path) -> None:
    received_paths: list[Path] = []

    def recording_handler(payload: OutputRequest) -> ToolResponse:
        received_paths.append(payload.output_path)
        return successful_handler(payload)

    definition = ToolDefinition(
        tool_id="simulation.run",
        is_external=False,
        input_schema="OutputRequest",
        output_schema="ToolResponse",
        write_path_fields=["output_path"],
    )
    registry = ToolRegistry(
        definitions={"simulation.run": definition},
        input_models={"simulation.run": OutputRequest},
        handlers={"simulation.run": recording_handler},
        repository_root=tmp_path,
    )

    response = registry.execute(
        "simulation.run",
        {"output_path": "experiments/factory-cycle/baseline.json"},
        policy("simulation.run"),
    )

    assert response.status is ToolStatus.SUCCESS
    assert received_paths == [(tmp_path / "experiments/factory-cycle/baseline.json").resolve()]


def test_writing_tool_converts_an_os_invalid_path_to_an_error_response(tmp_path: Path) -> None:
    definition = ToolDefinition(
        tool_id="simulation.run",
        is_external=False,
        input_schema="OutputRequest",
        output_schema="ToolResponse",
        write_path_fields=["output_path"],
    )
    registry = ToolRegistry(
        definitions={"simulation.run": definition},
        input_models={"simulation.run": OutputRequest},
        handlers={"simulation.run": successful_handler},
        repository_root=tmp_path,
    )

    response = registry.execute(
        "simulation.run",
        {"output_path": "\0"},
        policy("simulation.run"),
    )

    assert response.status is ToolStatus.ERROR
    assert response.error is not None
    assert "path" in response.error.root_cause.lower()


def test_writing_tool_rejects_escaped_policy_roots_and_missing_repository_root(
    tmp_path: Path,
) -> None:
    definition = ToolDefinition(
        tool_id="simulation.run",
        is_external=False,
        input_schema="OutputRequest",
        output_schema="ToolResponse",
        write_path_fields=["output_path"],
    )
    with_root = ToolRegistry(
        definitions={"simulation.run": definition},
        input_models={"simulation.run": OutputRequest},
        handlers={"simulation.run": successful_handler},
        repository_root=tmp_path,
    )
    without_root = ToolRegistry(
        definitions={"simulation.run": definition},
        input_models={"simulation.run": OutputRequest},
        handlers={"simulation.run": successful_handler},
    )

    escaped_root = with_root.execute(
        "simulation.run",
        {"output_path": "experiments/factory-cycle/baseline.json"},
        policy("simulation.run", write_roots=["../outside"]),
    )
    missing_root = without_root.execute(
        "simulation.run",
        {"output_path": "experiments/factory-cycle/baseline.json"},
        policy("simulation.run"),
    )

    assert escaped_root.status is ToolStatus.ERROR
    assert escaped_root.error is not None
    assert "outside the repository" in escaped_root.error.root_cause.lower()
    assert missing_root.status is ToolStatus.ERROR
    assert missing_root.error is not None
    assert "repository root" in missing_root.error.root_cause.lower()


def test_catalog_and_permission_manifests_expose_only_local_reviewable_tools() -> None:
    repository_root = Path(__file__).resolve().parents[2]
    catalog_payload = yaml.safe_load((repository_root / "tooling/catalog.yaml").read_text())
    permissions_payload = yaml.safe_load((repository_root / "tooling/permissions.yaml").read_text())
    catalog = ToolCatalog.model_validate(catalog_payload)

    assert [tool.tool_id for tool in catalog.tools] == [
        "problem.validate",
        "evidence.validate",
        "model.validate",
        "model.compile",
        "policy.validate",
        "simulation.run",
        "verification.run",
    ]
    assert all(not tool.is_external for tool in catalog.tools)
    assert catalog.tools[-2].write_path_fields == ["output_path"]
    assert catalog.tools[-1].write_path_fields == ["output_path"]
    for skill_name in ("modeling-interview", "model-compiler", "model-critic"):
        assert permissions_payload["skills"][skill_name]["forbidden_actions"] == [
            "approve_artifact",
            "execute_external_action",
        ]
