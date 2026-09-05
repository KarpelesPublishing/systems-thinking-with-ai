from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import TypeVar

import yaml
from pydantic import BaseModel

ModelT = TypeVar("ModelT", bound=BaseModel)


def load_yaml(path: str | Path, model_type: type[ModelT]) -> ModelT:
    payload = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("YAML payload must be a mapping")
    return model_type.model_validate(dict(payload))


def dump_canonical_json(model: BaseModel) -> str:
    payload = model.model_dump(mode="json", by_alias=True, exclude_none=True)
    try:
        return json.dumps(
            payload,
            allow_nan=False,
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=True,
        )
    except ValueError as error:
        raise ValueError("canonical JSON cannot contain non-finite floats") from error
