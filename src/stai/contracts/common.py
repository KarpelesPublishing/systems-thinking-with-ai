from __future__ import annotations

from collections.abc import Iterable, Iterator, Mapping, Sequence
from enum import Enum
from math import isfinite
from typing import Annotated, Any, Generic, Self, TypeVar, get_args

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    GetCoreSchemaHandler,
    JsonValue,
    field_validator,
    model_validator,
)
from pydantic_core import core_schema

NonEmptyStr = Annotated[str, Field(min_length=1)]
ItemT = TypeVar("ItemT")
KeyT = TypeVar("KeyT")
ValueT = TypeVar("ValueT")


class FrozenList(Sequence[ItemT], Generic[ItemT]):
    """A read-only sequence that compares naturally with lists."""

    __slots__ = ("_items",)

    def __init__(self, values: Iterable[ItemT] = ()) -> None:
        self._items = tuple(values)

    @staticmethod
    def _immutable(*args: Any, **kwargs: Any) -> None:
        raise TypeError("immutable contract list")

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        type_arguments = get_args(source_type)
        item_type = type_arguments[0] if type_arguments else Any
        list_schema = handler.generate_schema(list[item_type])
        return core_schema.no_info_after_validator_function(
            cls,
            list_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                deep_thaw,
                return_schema=list_schema,
            ),
        )

    def __getitem__(self, index: int | slice) -> ItemT | FrozenList[ItemT]:
        result = self._items[index]
        if isinstance(index, slice):
            return FrozenList(result)
        return result

    def __iter__(self) -> Iterator[ItemT]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __repr__(self) -> str:
        return repr(list(self._items))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FrozenList):
            return self._items == other._items
        if isinstance(other, Sequence) and not isinstance(other, (str, bytes, bytearray)):
            return list(self._items) == list(other)
        return False

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        memo[id(self)] = self
        return self

    def copy(self) -> Self:
        return self

    __setitem__ = _immutable
    __delitem__ = _immutable
    __iadd__ = _immutable
    __imul__ = _immutable
    append = _immutable
    clear = _immutable
    extend = _immutable
    insert = _immutable
    pop = _immutable
    remove = _immutable
    reverse = _immutable
    sort = _immutable


class FrozenDict(Mapping[KeyT, ValueT], Generic[KeyT, ValueT]):
    """A read-only mapping that compares naturally with dictionaries."""

    __slots__ = ("_values",)

    def __init__(self, values: Mapping[KeyT, ValueT] | Iterable[tuple[KeyT, ValueT]] = ()) -> None:
        self._values = dict(values)

    @staticmethod
    def _immutable(*args: Any, **kwargs: Any) -> None:
        raise TypeError("immutable contract dict")

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: GetCoreSchemaHandler,
    ) -> core_schema.CoreSchema:
        type_arguments = get_args(source_type)
        key_type, value_type = type_arguments if type_arguments else (Any, Any)
        dict_schema = handler.generate_schema(dict[key_type, value_type])
        return core_schema.no_info_after_validator_function(
            cls,
            dict_schema,
            serialization=core_schema.plain_serializer_function_ser_schema(
                deep_thaw,
                return_schema=dict_schema,
            ),
        )

    def __getitem__(self, key: KeyT) -> ValueT:
        return self._values[key]

    def __iter__(self) -> Iterator[KeyT]:
        return iter(self._values)

    def __len__(self) -> int:
        return len(self._values)

    def __repr__(self) -> str:
        return repr(self._values)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Mapping):
            return dict(self._values) == dict(other)
        return False

    def __copy__(self) -> Self:
        return self

    def __deepcopy__(self, memo: dict[int, Any]) -> Self:
        memo[id(self)] = self
        return self

    def copy(self) -> Self:
        return self

    __setitem__ = _immutable
    __delitem__ = _immutable
    __ior__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable


def deep_freeze(value: Any) -> Any:
    """Recursively freeze mutable JSON-like containers."""
    if isinstance(value, FrozenList):
        return FrozenList(deep_freeze(item) for item in value)
    if isinstance(value, FrozenDict):
        return FrozenDict((key, deep_freeze(item)) for key, item in value.items())
    if isinstance(value, list):
        return FrozenList(deep_freeze(item) for item in value)
    if isinstance(value, dict):
        return FrozenDict((key, deep_freeze(item)) for key, item in value.items())
    if isinstance(value, tuple):
        return tuple(deep_freeze(item) for item in value)
    if isinstance(value, set):
        return frozenset(deep_freeze(item) for item in value)
    return value


def deep_thaw(value: Any) -> Any:
    """Return ordinary serializable containers without exposing canonical state."""
    if isinstance(value, FrozenList):
        return [deep_thaw(item) for item in value]
    if isinstance(value, FrozenDict):
        return {key: deep_thaw(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [deep_thaw(item) for item in value]
    if isinstance(value, frozenset):
        return [deep_thaw(item) for item in value]
    return value


def reject_nonfinite_json_values(value: Any) -> None:
    """Reject values that cannot appear in canonical JSON."""
    if isinstance(value, float) and not isfinite(value):
        raise ValueError("details cannot contain non-finite JSON numbers")
    if isinstance(value, Mapping):
        for nested_value in value.values():
            reject_nonfinite_json_values(nested_value)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for nested_value in value:
            reject_nonfinite_json_values(nested_value)


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, str_strip_whitespace=True)

    def _freeze_contract_fields(self) -> None:
        for field_name in type(self).model_fields:
            object.__setattr__(self, field_name, deep_freeze(getattr(self, field_name)))

    def model_post_init(self, __context: Any) -> None:
        self._freeze_contract_fields()

    def model_copy(
        self,
        *,
        update: Mapping[str, Any] | None = None,
        deep: bool = False,
    ) -> Self:
        payload = {
            field_name: deep_thaw(getattr(self, field_name))
            for field_name in type(self).model_fields
        }
        if update is not None:
            payload.update(dict(update))
        return type(self).model_validate(payload)


class ArtifactState(str, Enum):
    DRAFT = "draft"
    PROPOSED = "proposed"
    VERIFIED = "verified"
    APPROVED = "approved"
    SUPERSEDED = "superseded"


class EvidenceMode(str, Enum):
    EMPIRICAL = "empirical"
    TEACHING_RECONSTRUCTION = "teaching_reconstruction"


class ClaimStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    CONTESTED = "contested"


class ToolStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"


class ToolError(ContractModel):
    root_cause: NonEmptyStr
    safe_retry: NonEmptyStr
    stop_condition: NonEmptyStr


class ToolResponse(ContractModel):
    status: ToolStatus
    summary: str
    next_actions: FrozenList[str] = Field(default_factory=FrozenList)
    artifacts: FrozenList[str] = Field(default_factory=FrozenList)
    details: FrozenDict[str, JsonValue] = Field(default_factory=FrozenDict)
    error: ToolError | None = None

    @field_validator("details")
    @classmethod
    def validate_canonical_details(
        cls,
        details: FrozenDict[str, JsonValue],
    ) -> FrozenDict[str, JsonValue]:
        reject_nonfinite_json_values(details)
        return details

    @model_validator(mode="after")
    def validate_error_details(self) -> Self:
        if self.status is ToolStatus.ERROR and self.error is None:
            raise ValueError("ToolError is required when status is error")
        if self.status is not ToolStatus.ERROR and self.error is not None:
            raise ValueError("non-error responses cannot include a ToolError")
        return self
