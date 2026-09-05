import hashlib
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

MAX_CANONICAL_DEPTH = 64


def _canonicalize(
    value: Any,
    *,
    ancestors: set[int] | None = None,
    depth: int = 0,
) -> Any:
    if depth > MAX_CANONICAL_DEPTH:
        raise ValueError("Canonical JSON exceeds the maximum nesting depth.")
    active_ancestors = ancestors if ancestors is not None else set()
    if isinstance(value, Mapping):
        marker = id(value)
        if marker in active_ancestors:
            raise ValueError("Canonical JSON cannot contain a cycle.")
        active_ancestors.add(marker)
        try:
            normalized: dict[str, Any] = {}
            for key, nested_value in value.items():
                if not isinstance(key, str):
                    raise ValueError("Canonical JSON object keys must be strings.")
                normalized[key] = _canonicalize(
                    nested_value,
                    ancestors=active_ancestors,
                    depth=depth + 1,
                )
            return normalized
        finally:
            active_ancestors.remove(marker)
    if isinstance(value, list | tuple):
        marker = id(value)
        if marker in active_ancestors:
            raise ValueError("Canonical JSON cannot contain a cycle.")
        active_ancestors.add(marker)
        try:
            return [
                _canonicalize(
                    nested_value,
                    ancestors=active_ancestors,
                    depth=depth + 1,
                )
                for nested_value in value
            ]
        finally:
            active_ancestors.remove(marker)
    return value


def canonical_hash(payload: Mapping[str, Any]) -> str:
    try:
        serialized = json.dumps(
            _canonicalize(payload),
            allow_nan=False,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        )
    except (RecursionError, TypeError, ValueError) as error:
        raise ValueError(f"Payload is not canonical JSON: {error}") from error
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ReplayRecord:
    model_hash: str
    input_hash: str
    result_hash: str


def create_replay_record(
    model_payload: dict[str, Any],
    experiment_payload: dict[str, Any],
    result_payload: dict[str, Any],
) -> ReplayRecord:
    return ReplayRecord(
        model_hash=canonical_hash(model_payload),
        input_hash=canonical_hash(experiment_payload),
        result_hash=canonical_hash(result_payload),
    )
