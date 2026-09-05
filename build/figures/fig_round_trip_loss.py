#!/usr/bin/env python3
"""Chapter 24, "The round trip": document to interchange file to document, and what did not survive.

The chapter exports the factory document whose order_rate carries evidence='observed' and
note='billing system, 2026-08-01', imports it again, and reads the report: the hash changed,
so `hash_preserved` is False; `semantic_loss` names order_rate's evidence and note; and the
claim the trip supports is only that the file opens in the other tool. This figure draws that
trip: the document with its hash before, the interchange file that holds only the portable
fields, the document with its hash after, and the two local fields dropped into a sink on the
way.

    uv run --group figures python build/figures/fig_round_trip_loss.py

Data: chapters.chapter_24_interop.code.interchange.round_trip_report on the document that
tests/chapters/test_interop.py builds, which is the one whose semantic_loss the chapter prints.
The hashes drawn are read from the report, not typed in. Placement is a layout choice.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import figure, save  # noqa: E402
from sdvocab import cloud, link, stock  # noqa: E402

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable  # noqa: E402
from chapters.chapter_24_interop.code.interchange import (  # noqa: E402
    LOCAL_FIELDS,
    PORTABLE_FIELDS,
    Claim,
    round_trip_report,
)


def document() -> ModelDocument:
    return ModelDocument("factory", "2.1.0", horizon=52, variables=[
        Variable("inventory", "stock", "units", value=12.0),
        Variable("order_rate", "parameter", "units/week", value=10.0,
                 evidence="observed", note="billing system, 2026-08-01"),
        Variable("production", "flow", "units/week", "order_rate * 1.1",
                 target="inventory", sign=1),
    ])


def main():
    report = round_trip_report(document())
    assert report["hash_preserved"] is False, report
    assert report["hash_before"] != report["hash_after"]
    assert report["semantic_loss"] == {
        "order_rate": ["evidence='observed'", "note='billing system, 2026-08-01'"]
    }, report["semantic_loss"]
    assert report["claim_supported"] == Claim.FILE
    assert LOCAL_FIELDS == ("evidence", "note")

    fig, ax = figure(height_in=2.5)
    ax.set_xlim(-0.3, 9.3)
    ax.set_ylim(-2.75, 1.55)
    ax.set_aspect("equal")
    ax.axis("off")

    w, h = 2.3, 0.85
    stock(ax, 1.2, 0.6, "model document", w=w, h=h, sublabel=f"hash {report['hash_before']}")
    stock(ax, 4.5, 0.6, "interchange file", w=w, h=h, sublabel="portable fields only")
    stock(ax, 7.8, 0.6, "model document", w=w, h=h, sublabel=f"hash {report['hash_after']}")
    link(ax, (1.2 + w / 2, 0.6), (4.5 - w / 2, 0.6), polarity="", curve=0.0, shrinkA=2.0,
         shrinkB=2.0, label="export")
    link(ax, (4.5 + w / 2, 0.6), (7.8 - w / 2, 0.6), polarity="", curve=0.0, shrinkA=2.0,
         shrinkB=2.0, label="import")

    ax.text(4.5, 1.35, "survives: " + ", ".join(PORTABLE_FIELDS), ha="center", va="center",
            fontsize=6.2)

    # The local fields leave the model on the way out.
    cloud(ax, 2.85, -1.25, r=0.28)
    link(ax, (2.85, 0.6 - h / 2), (2.85, -0.9), polarity="", curve=0.0, shrinkA=2.0,
         shrinkB=2.0, linestyle=(0, (3.0, 2.0)))
    lost = report["semantic_loss"]["order_rate"]
    ax.text(3.35, -1.1, "lost, order_rate:", ha="left", va="center", fontsize=6.4,
            style="italic")
    for i, item in enumerate(lost):
        ax.text(3.35, -1.42 - 0.3 * i, item, ha="left", va="center", fontsize=6.2,
                family="monospace")

    ax.text(4.5, -2.45,
            f"hash_preserved: {report['hash_preserved']}. claim supported: {Claim.FILE}",
            ha="center", va="center", fontsize=6.4)

    fig.tight_layout()
    save(fig, "round-trip-loss")


if __name__ == "__main__":
    main()
