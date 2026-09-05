"""Offline teaching reconstruction: review a proposal, then simulate two policies."""

import csv
import json
import math
from dataclasses import asdict, replace
from pathlib import Path

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime
from chapters.chapter_27_compiler_agent.code.patch import Edit, Patch, apply_patch, review_packet
from examples.hiring_pipeline import hiring_pipeline

FIXTURES = Path(__file__).with_name("workflow")


def build_model() -> ModelDocument:
    """Reuse hiring structure, replacing fictional provenance with fixture labels."""
    with (FIXTURES / "synthetic_inputs.csv").open(newline="") as handle:
        rows = {row["variable_id"]: row for row in csv.DictReader(handle)}
    variables: list[Variable] = []
    for variable in hiring_pipeline().variables:
        if variable.id in rows:
            row = rows[variable.id]
            variable = replace(variable, value=float(row["value"]),
                               evidence=row["evidence"], note=row["note"])
        variables.append(variable)
    return ModelDocument("reviewed_synthetic_hiring", "1.0.0", variables,
                         horizon=52, horizon_unit="week", time_step=1.0)


def settings() -> RunSettings:
    return RunSettings(solver="euler", dt=1.0, horizon=52.0, seed=0)


def _proposal(source: ModelDocument, key: str) -> Patch:
    fields = json.loads((FIXTURES / "proposals.json").read_text())[key]
    rationale = fields.pop("rationale")
    return Patch(source.hash(), [Edit("change", "aggression", rationale, fields)])


def flawed_proposal(source: ModelDocument) -> Patch:
    return _proposal(source, "flawed")


def corrected_proposal(source: ModelDocument) -> Patch:
    return _proposal(source, "corrected")


def review(source: ModelDocument, patch: Patch) -> dict:
    """Replay a teaching review rule, not a real person's signature or permission."""
    packet = review_packet(source, patch)
    reasons = []
    if not packet.get("valid", False):
        reasons.append("Patch does not apply or pass document validation")
    if len(patch.edits) != 1 or any(
        e.operation != "change" or e.variable_id != "aggression"
        or set(e.fields) - {"value", "evidence", "note"} for e in patch.edits
    ):
        reasons.append("Only the recruiting response parameter is in scope")
    for edit in patch.edits:
        value = edit.fields.get("value")
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not 0 < value <= 0.5):
            reasons.append("Response must be finite and within (0, 0.5] per week")
        if edit.fields.get("evidence", "proposed") != "proposed":
            reasons.append("A suggestion cannot claim empirical evidence")
    return {
        "reviewer": "Illustrative human review replay",
        "simulation_authorized": not reasons,
        "deployment_authorized": False,
        "external_action_authorized": False,
        "reasons": reasons,
        "packet": packet,
    }


def run_workflow() -> dict:
    source = build_model()
    before = source.canonical()
    flawed = flawed_proposal(source)
    corrected = corrected_proposal(source)
    decisions = {"flawed": review(source, flawed), "corrected": review(source, corrected)}
    if not decisions["corrected"]["simulation_authorized"]:
        raise ValueError("Corrected proposal was not authorized for simulation")
    candidate = apply_patch(source, corrected)
    runs = []
    for label, model in [("baseline", source), ("corrected", candidate)]:
        result = Runtime(model, settings()).run()
        dt = result.settings.dt
        recruited = sum(result.series["recruiting"][:-1]) * dt
        joined = sum(result.series["joining"][:-1]) * dt
        left = sum(result.series["leaving"][:-1]) * dt
        final = result.final("productive")
        trainees = result.final("arriving__level")
        numeric = {
            "aggression_per_week": result.final("aggression"),
            "final_productive_people": final,
            "peak_productive_people": max(result.series["productive"]),
            "final_trainees_people": trainees,
            "recruited_people": recruited,
            "joined_people": joined,
            "departed_people": left,
            "recruiting_cost_usd": recruited * 1000,
            "productive_balance_error": final - (20 + joined - left),
            "trainee_balance_error": trainees - (recruited - joined),
        }
        runs.append({"policy": label, "model_hash": model.hash(),
                     **{k: round(v, 6) if abs(v) > 1e-10 else 0.0
                        for k, v in numeric.items()}})
    return {
        "status": "Synthetic teaching reconstruction; simulation only",
        "source_unchanged": source.canonical() == before,
        "settings": asdict(settings()),
        "reviews": decisions,
        "runs": runs,
        "costs": {"api_calls": 0, "api_cost_usd": 0,
                  "recruiting_cost_per_person_usd_assumed": 1000,
                  "excluded": "Wages, training, vacancies, review labor, local compute"},
        "limitations": [
            "No real organization data or live AI output; no deployment approval",
            "Illustrative review is not authentication or an external authorization system",
            "First-order eight-week mean delay, not a fixed eight-week cohort delay",
            "Continuous people; empty initial pipeline; fixed target and attrition",
            "No capacity constraint, selection quality, fairness or labor-market feedback",
            "Euler dt=1 week only; no convergence, calibration or uncertainty study",
            "Validation checks structure, not dimensional consistency or empirical truth",
            "Lower recruiting cost is partial accounting, not a net-benefit recommendation",
        ],
    }


def render_report(report: dict) -> str:
    return json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"


if __name__ == "__main__":
    print(render_report(run_workflow()), end="")
