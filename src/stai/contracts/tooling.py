from typing import Literal

from pydantic import Field

from .common import ContractModel, FrozenList, NonEmptyStr


class ToolDefinition(ContractModel):
    tool_id: str = Field(pattern=r"^[a-z]+\.[a-z-]+$")
    implementation_path: NonEmptyStr | None = None
    is_external: bool
    input_schema: NonEmptyStr
    output_schema: NonEmptyStr
    permission_level: NonEmptyStr = "case-policy"
    error_contract: NonEmptyStr = "ToolError"
    adapter: NonEmptyStr = "python-registry"
    write_path_fields: FrozenList[NonEmptyStr] = Field(default_factory=FrozenList)


class ToolCatalog(ContractModel):
    tools: FrozenList[ToolDefinition] = Field(min_length=1)


class ToolPolicy(ContractModel):
    case_id: NonEmptyStr
    allowed_tools: FrozenList[NonEmptyStr] = Field(default_factory=FrozenList)
    write_roots: FrozenList[NonEmptyStr] = Field(default_factory=FrozenList)
    allow_external_actions: Literal[False] = False
