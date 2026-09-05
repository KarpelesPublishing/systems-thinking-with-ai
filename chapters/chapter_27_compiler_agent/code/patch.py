"""A schema-constrained patch: the only shape in which generated structure may arrive."""

from dataclasses import dataclass, field

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable, diff, validate

OPERATIONS = ("add", "remove", "change")


@dataclass(frozen=True)
class Edit:
    """One change to one variable, with the reason attached to the change itself."""

    operation: str
    variable_id: str
    rationale: str
    fields: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.operation not in OPERATIONS:
            raise ValueError(f"operation must be one of {OPERATIONS}")
        if not self.rationale.strip():
            raise ValueError(f"edit to '{self.variable_id}' carries no rationale")
        if self.operation in ("add", "change") and not self.fields:
            raise ValueError(f"'{self.operation}' needs fields")


@dataclass
class Patch:
    """A set of edits proposed against one model version."""

    against_hash: str
    edits: list[Edit] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.edits:
            raise ValueError("an empty patch is not a proposal")
        ids = [e.variable_id for e in self.edits]
        if len(ids) != len(set(ids)):
            raise ValueError("a patch may touch each variable once")


def _proposed(fields: dict) -> dict:
    """Stamp anything an agent supplied as proposed unless the patch says otherwise.

    The schema's own default is `assumed`, which is the right default for a person
    writing a variable and the wrong one here: an agent has suggested a number and
    nobody has checked it. Leaving the rule to a prompt is what this whole chapter
    argues against, so it is enforced at the point the variable is built.
    """
    return {"evidence": "proposed", **fields}


def apply_patch(document: ModelDocument, patch: Patch) -> ModelDocument:
    """Produce a new document. Refuses a patch written against a different version."""
    if patch.against_hash != document.hash():
        raise ValueError(
            f"patch was written against {patch.against_hash}, document is {document.hash()}"
        )
    variables = {v.id: v for v in document.variables}
    for edit in patch.edits:
        if edit.operation == "remove":
            if edit.variable_id not in variables:
                raise ValueError(f"cannot remove '{edit.variable_id}': it does not exist")
            del variables[edit.variable_id]
        elif edit.operation == "add":
            if edit.variable_id in variables:
                raise ValueError(f"cannot add '{edit.variable_id}': it already exists")
            variables[edit.variable_id] = Variable(id=edit.variable_id, **_proposed(edit.fields))
        else:
            if edit.variable_id not in variables:
                raise ValueError(f"cannot change '{edit.variable_id}': it does not exist")
            current = variables[edit.variable_id].__dict__
            fields = edit.fields
            if {"value", "equation"} & set(fields):
                fields = _proposed(fields)
            variables[edit.variable_id] = Variable(**{**current, **fields})
    return ModelDocument(
        name=document.name, version=document.version, variables=list(variables.values()),
        horizon=document.horizon, horizon_unit=document.horizon_unit,
        time_step=document.time_step,
    )


def review_packet(document: ModelDocument, patch: Patch) -> dict:
    """What a human sees. Never the prose summary, always the diff and the problems."""
    try:
        proposed = apply_patch(document, patch)
    except ValueError as exc:
        return {"applied": False, "reason": str(exc)}
    problems = validate(proposed)
    return {
        "applied": True,
        "valid": not problems,
        "problems": problems,
        "diff": diff(document, proposed),
        "rationales": {e.variable_id: e.rationale for e in patch.edits},
        "hash_before": document.hash(),
        "hash_after": proposed.hash(),
    }


def structural_variance(documents: list[ModelDocument]) -> dict[str, object]:
    """Compile the same narrative twice and measure how much the structure moved."""
    if len(documents) < 2:
        raise ValueError("variance needs at least two compilations")
    sets = [{v.id for v in d.variables} for d in documents]
    common = set.intersection(*sets)
    union = set.union(*sets)
    return {
        "agreed": sorted(common),
        "disputed": sorted(union - common),
        "agreement": len(common) / len(union) if union else 1.0,
        "hashes": [d.hash() for d in documents],
    }
