from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_24_interop.code.interchange import (
    Claim,
    export,
    import_document,
    round_trip_report,
    semantic_loss,
)


def document() -> ModelDocument:
    return ModelDocument("factory", "2.1.0", horizon=52, variables=[
        Variable("inventory", "stock", "units", value=12.0),
        Variable("order_rate", "parameter", "units/week", value=10.0,
                 evidence="observed", note="billing system, 2026-08-01"),
        Variable("production", "flow", "units/week", "order_rate * 1.1",
                 target="inventory", sign=1),
    ])


def test_an_export_carries_the_portable_fields() -> None:
    payload = export(document())
    assert {v["id"] for v in payload["variables"]} == {"inventory", "order_rate", "production"}
    assert payload["variables"][0].keys() >= {"id", "kind", "unit"}


def test_the_export_drops_evidence_and_notes() -> None:
    payload = export(document())
    assert all("evidence" not in v for v in payload["variables"])


def test_semantic_loss_names_what_will_not_survive() -> None:
    losses = semantic_loss(document())
    assert "order_rate" in losses
    assert any("evidence" in item for item in losses["order_rate"])


def test_a_round_trip_changes_the_hash_because_meaning_was_lost() -> None:
    """The equations survive. The provenance does not, and the hash says so."""
    report = round_trip_report(document())
    assert report["hash_preserved"] is False
    assert report["claim_supported"] == Claim.FILE


def test_a_document_with_nothing_local_round_trips_unchanged() -> None:
    plain = ModelDocument("plain", "1.0.0", variables=[
        Variable("s", "stock", "u", value=1.0),
        Variable("f", "flow", "u/w", "s * 0.1", target="s", sign=1),
    ])
    assert round_trip_report(plain)["hash_preserved"] is True


def test_an_imported_document_still_runs_the_same_equations() -> None:
    restored = import_document(export(document()), version="2.1.0")
    assert restored.by_id("production").equation == "order_rate * 1.1"
    assert restored.by_id("production").target == "inventory"


def test_the_three_claims_are_distinct() -> None:
    assert Claim.FILE != Claim.SEMANTIC != Claim.RUNTIME


def test_a_non_default_horizon_unit_survives_the_round_trip() -> None:
    """horizon_unit is portable, so a model in months must not come back in weeks."""
    document = ModelDocument("monthly", "1.0.0", horizon=12, horizon_unit="month", variables=[
        Variable("level", "stock", "units", value=1.0),
        Variable("fill", "flow", "units/month", "1.0", target="level", sign=1),
    ])
    report = round_trip_report(document)
    assert report["semantic_loss"] == {}
    assert report["hash_preserved"] is True


def test_a_lookup_and_a_delay_survive_the_round_trip() -> None:
    """The schema grew, so the interchange format had to learn the new fields."""
    document = ModelDocument("mixed", "1.0.0", horizon=10, variables=[
        Variable("level", "stock", "units", value=1.0),
        Variable("rate", "parameter", "units/week", value=2.0),
        Variable("curve", "lookup", "dimensionless", "level",
                 points=((0.0, 1.0), (5.0, 0.4))),
        Variable("lagged", "delay", "units/week", "rate", delay_time=3.0),
        Variable("fill", "flow", "units/week", "lagged", target="level", sign=1),
    ])
    report = round_trip_report(document)
    assert report["hash_preserved"] is True
    assert report["semantic_loss"] == {}
    restored = import_document(export(document))
    assert restored.by_id("curve").points == ((0.0, 1.0), (5.0, 0.4))
    assert restored.by_id("lagged").delay_time == 3.0
