"""A hiring pipeline with a training delay, built from the packs.

Chapter 20 for the document, Chapter 16's delay as a document kind, Chapter 21
for the order, Chapter 22 to run it. Nothing here is new code: it is the packs
composed through the model document.
"""

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable


def hiring_pipeline(hiring_aggression: float = 0.25) -> ModelDocument:
    """Recruits become productive only after a training delay."""
    return ModelDocument("hiring_pipeline", "1.0.0", horizon=52, horizon_unit="week", variables=[
        Variable("productive", "stock", "people", value=20.0,
                 evidence="observed", note="headcount system, 2026-08-01"),
        Variable("target", "parameter", "people", value=40.0, evidence="assumed"),
        Variable("attrition_rate", "parameter", "1/week", value=0.01, evidence="inferred",
                 note="from the last four quarters of leavers"),
        Variable("aggression", "parameter", "1/week", value=hiring_aggression, evidence="assumed"),
        Variable("gap", "auxiliary", "people", "target - productive"),
        # The lever: how fast recruiting responds to the gap.
        Variable("recruiting", "auxiliary", "people/week", "max(0.0, gap) * aggression"),
        # Chapter 16's tank, as a document kind. Recruits take eight weeks to land.
        Variable("arriving", "delay", "people/week", "recruiting", delay_time=8.0),
        Variable("joining", "flow", "people/week", "arriving", target="productive", sign=1),
        Variable("leaving", "flow", "people/week", "productive * attrition_rate",
                 target="productive", sign=-1),
    ])
