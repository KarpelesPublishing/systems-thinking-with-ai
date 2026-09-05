from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError

from stai.contracts.common import ToolError, ToolResponse, ToolStatus
from stai.contracts.tooling import ToolDefinition, ToolPolicy

ToolHandler = Callable[[BaseModel], ToolResponse]


def error_response(
    root_cause: str,
    safe_retry: str,
    stop_condition: str,
) -> ToolResponse:
    return ToolResponse(
        status=ToolStatus.ERROR,
        summary=root_cause,
        next_actions=[safe_retry],
        error=ToolError(
            root_cause=root_cause,
            safe_retry=safe_retry,
            stop_condition=stop_condition,
        ),
    )


class ToolRegistry:
    def __init__(
        self,
        definitions: dict[str, ToolDefinition],
        input_models: dict[str, type[BaseModel]],
        handlers: dict[str, ToolHandler],
        repository_root: Path | None = None,
    ) -> None:
        self.definitions = definitions
        self.input_models = input_models
        self.handlers = handlers
        self.repository_root = repository_root.resolve() if repository_root is not None else None

    def execute(
        self,
        tool_id: str,
        payload: dict[str, Any],
        policy: ToolPolicy,
    ) -> ToolResponse:
        definition = self.definitions.get(tool_id)
        input_model = self.input_models.get(tool_id)
        handler = self.handlers.get(tool_id)

        if definition is None or input_model is None or handler is None:
            return error_response(
                root_cause=f"Unknown tool: {tool_id}.",
                safe_retry="Use a tool listed in tooling/catalog.yaml.",
                stop_condition=(
                    "Do not invoke this identifier until a human adds its catalog entry."
                ),
            )
        if tool_id not in policy.allowed_tools:
            return error_response(
                root_cause=f"Tool {tool_id} is not allowed by the case policy.",
                safe_retry="Request human review before changing the case policy.",
                stop_condition="Do not invoke this tool until human-approved policy permits it.",
            )
        if definition.is_external:
            return error_response(
                root_cause=f"External action is disabled for tool {tool_id}.",
                safe_retry="Prepare a review packet instead of executing an action.",
                stop_condition="Do not invoke external tools in this release.",
            )
        try:
            request = input_model.model_validate(payload)
        except ValidationError:
            return error_response(
                root_cause=f"Input payload does not match {definition.input_schema}.",
                safe_retry="Provide every required field with the documented type.",
                stop_condition="Do not run the tool until the payload validates.",
            )
        normalized_request = self._normalize_write_paths(definition, request, policy)
        if isinstance(normalized_request, ToolResponse):
            return normalized_request
        try:
            response = handler(normalized_request)
        except Exception as error:
            return error_response(
                root_cause=f"Tool {tool_id} failed: {type(error).__name__}: {error}",
                safe_retry="Correct the artifact and rerun the authorized tool.",
                stop_condition="Do not promote or execute an artifact while the tool is failing.",
            )
        if not isinstance(response, ToolResponse):
            return error_response(
                root_cause=(
                    f"Tool {tool_id} returned {type(response).__name__}, not a ToolResponse."
                ),
                safe_retry="Correct the handler to return the documented ToolResponse contract.",
                stop_condition=(
                    "Do not promote or execute an artifact from an invalid tool response."
                ),
            )
        return response

    def _normalize_write_paths(
        self,
        definition: ToolDefinition,
        request: BaseModel,
        policy: ToolPolicy,
    ) -> BaseModel | ToolResponse:
        if not definition.write_path_fields:
            return request
        if self.repository_root is None:
            return error_response(
                root_cause=f"Tool {definition.tool_id} declares writes but has no repository root.",
                safe_retry="Initialize the registry with a repository root before writing.",
                stop_condition="Do not run a writing tool without a verified repository root.",
            )
        permitted_roots = self._resolve_permitted_roots(policy)
        if isinstance(permitted_roots, ToolResponse):
            return permitted_roots
        updates: dict[str, Path] = {}
        for field_name in definition.write_path_fields:
            value = getattr(request, field_name, None)
            if not isinstance(value, Path):
                return error_response(
                    root_cause=f"Tool {definition.tool_id} has no valid Path field {field_name}.",
                    safe_retry="Provide the documented output path as a path-like value.",
                    stop_condition="Do not run the tool until its output path validates.",
                )
            candidate = value if value.is_absolute() else self.repository_root / value
            try:
                resolved = candidate.resolve()
            except (OSError, RuntimeError, ValueError) as error:
                return error_response(
                    root_cause=f"Write path for {field_name} could not be resolved: {error}",
                    safe_retry="Use a valid path beneath an approved case write root.",
                    stop_condition="Do not run a writing tool with an invalid output path.",
                )
            if not any(resolved.is_relative_to(root) for root in permitted_roots):
                return error_response(
                    root_cause=f"Write path {resolved} is outside the case policy write roots.",
                    safe_retry="Choose an output path beneath an approved case write root.",
                    stop_condition=(
                        "Do not write artifacts outside the human-approved case boundary."
                    ),
                )
            updates[field_name] = resolved
        try:
            normalized_payload = request.model_dump(mode="python")
            normalized_payload.update(updates)
            return type(request).model_validate(normalized_payload)
        except ValidationError:
            return error_response(
                root_cause=f"Normalized write paths do not match {definition.input_schema}.",
                safe_retry="Correct the output path and retry the authorized tool.",
                stop_condition="Do not run the tool until normalized paths validate.",
            )

    def _resolve_permitted_roots(self, policy: ToolPolicy) -> list[Path] | ToolResponse:
        assert self.repository_root is not None
        if not policy.write_roots:
            return error_response(
                root_cause="Writing tools require at least one approved case write root.",
                safe_retry=(
                    "Add a repository-relative write root to the human-reviewed case policy."
                ),
                stop_condition="Do not run a writing tool without an approved write root.",
            )
        permitted_roots: list[Path] = []
        for root_text in policy.write_roots:
            try:
                root = (self.repository_root / root_text).resolve()
            except (OSError, RuntimeError, ValueError) as error:
                return error_response(
                    root_cause=f"Case policy write root {root_text} is invalid: {error}",
                    safe_retry="Use a valid repository-relative write root for this case.",
                    stop_condition="Do not run writing tools with an invalid policy write root.",
                )
            if not root.is_relative_to(self.repository_root):
                return error_response(
                    root_cause=f"Case policy write root {root_text} is outside the repository.",
                    safe_retry="Use a repository-relative write root for this case.",
                    stop_condition=(
                        "Do not run writing tools with a policy that escapes the repository."
                    ),
                )
            permitted_roots.append(root)
        return permitted_roots
