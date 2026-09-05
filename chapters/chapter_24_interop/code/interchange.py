"""Moving a model between tools, and reporting what did not survive the trip."""

from dataclasses import dataclass

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable

# What a minimal stock-and-flow interchange format can carry.
PORTABLE_FIELDS = ("id", "kind", "unit", "equation", "value", "target", "sign",
                   "points", "delay_time")
# What this book's document carries that a generic format has nowhere to put.
LOCAL_FIELDS = ("evidence", "note")


@dataclass(frozen=True)
class Claim:
    """Three strengths of interoperability claim, kept separate on purpose."""

    FILE = "the file opens in the other tool"
    SEMANTIC = "the equations mean the same thing in both tools"
    RUNTIME = "two runtimes exchange state correctly during a run"


def export(document: ModelDocument) -> dict:
    """Emit only what a generic interchange format can hold."""
    return {
        "name": document.name,
        "time_step": document.time_step,
        "horizon": document.horizon,
        "horizon_unit": document.horizon_unit,
        "variables": [
            {f: getattr(v, f) for f in PORTABLE_FIELDS} for v in sorted(
                document.variables, key=lambda v: v.id
            )
        ],
    }


def semantic_loss(document: ModelDocument) -> dict[str, list[str]]:
    """What an export drops. Reported per variable so a reviewer can weigh it."""
    losses: dict[str, list[str]] = {}
    for variable in document.variables:
        dropped = []
        for field in LOCAL_FIELDS:
            value = getattr(variable, field)
            if value and value != "assumed":
                dropped.append(f"{field}={value!r}")
        if dropped:
            losses[variable.id] = dropped
    return losses


def import_document(payload: dict, version: str = "1.0.0") -> ModelDocument:
    """Rebuild a document from an exported payload. Everything local comes back empty."""
    if "variables" not in payload or "name" not in payload:
        raise ValueError("payload is not an interchange document")
    return ModelDocument(
        name=payload["name"],
        version=version,
        horizon=int(payload.get("horizon", 1)),
        horizon_unit=str(payload.get("horizon_unit", "week")),
        time_step=float(payload.get("time_step", 1.0)),
        variables=[Variable(**_restore(v)) for v in payload["variables"]],
    )


def _restore(row: dict) -> dict:
    """One exported variable, back in the types the schema expects.

    A format that carries a lookup's points hands them back as lists, and the
    schema wants tuples, so the round trip has to say so or the hash moves for a
    reason that has nothing to do with the model.
    """
    fields = {f: row[f] for f in PORTABLE_FIELDS if f in row}
    if fields.get("points"):
        fields["points"] = tuple(tuple(point) for point in fields["points"])
    return fields


def round_trip_report(document: ModelDocument) -> dict[str, object]:
    """Export, import, and say precisely what changed."""
    restored = import_document(export(document), version=document.version)
    return {
        "hash_before": document.hash(),
        "hash_after": restored.hash(),
        "hash_preserved": document.hash() == restored.hash(),
        "semantic_loss": semantic_loss(document),
        "claim_supported": Claim.FILE,
    }
