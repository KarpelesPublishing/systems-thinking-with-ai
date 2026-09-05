#!/usr/bin/env python3
"""Chapter 25, "Scenarios, not predictions": three Bass runs over twenty weeks, and their spread.

The chapter varies word of mouth on Chapter 22's Bass document and prints a table: cautious
(imitation 0.05) ends at 275.9 adopters, base (0.30) at 937.7, aggressive (0.60) at 1000.0, with
the last two breaching a declared ceiling of 900. This figure plots the three paths that produce
those endpoints, with the ceiling as a dashed line and a direct label on each path.

    uv run --group figures python build/figures/fig_scenario_spread.py

Data: chapters.chapter_25_flight_sim.code.scenario.ScenarioRunner(bass, [Constraint("adopters",
high=900.0)]).run(label, {"imitation": value}, RunSettings("euler", 1.0, 20, 0),
report=("adopters",)) for the three values, exactly as tests/chapters/test_flight_sim.py pins
the chapter's table. A record holds only the final value, so the full path of each scenario is
rerun through the same Runtime with the same settings and asserted to end where the record
does. The asserts pin 275.9, 937.7 and 999.97 (the table's 1000.0 rounded to one place) and the
breach count before anything is drawn.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from figstyle import DASHES, figure, save  # noqa: E402

from chapters.chapter_20_model_document.code.document import ModelDocument, Variable  # noqa: E402
from chapters.chapter_22_runtime.code.runtime import RunSettings, Runtime  # noqa: E402
from chapters.chapter_25_flight_sim.code.scenario import Constraint, ScenarioRunner  # noqa: E402

SCENARIOS = (("cautious", 0.05), ("base", 0.30), ("aggressive", 0.60))
CEILING = 900.0


def bass(imitation: float = 0.30) -> ModelDocument:
    return ModelDocument("bass", "1.0.0", horizon=40, variables=[
        Variable("adopters", "stock", "people", value=1.0),
        Variable("total_market", "parameter", "people", value=1000.0),
        Variable("innovation", "parameter", "1/week", value=0.01),
        Variable("imitation", "parameter", "1/week", value=imitation),
        Variable("potential", "auxiliary", "people", "total_market - adopters"),
        Variable("adoption", "flow", "people/week",
                 "(innovation + imitation * adopters / total_market) * potential",
                 target="adopters", sign=1),
    ])


def main():
    settings = RunSettings(solver="euler", dt=1.0, horizon=20, seed=0)
    runner = ScenarioRunner(bass(), [Constraint("adopters", high=CEILING)])
    records = {
        label: runner.run(label, {"imitation": value}, settings, report=("adopters",))
        for label, value in SCENARIOS
    }
    finals = {label: round(r.outputs["adopters"], 2) for label, r in records.items()}
    assert finals == {"cautious": 275.90, "base": 937.70, "aggressive": 999.97}, finals
    assert [len(r.breaches) for r in records.values()] == [0, 1, 1]

    paths = {}
    for label, value in SCENARIOS:
        result = Runtime(bass(value), settings).run()
        assert result.model_hash == records[label].model_hash
        assert abs(result.final("adopters") - records[label].outputs["adopters"]) < 1e-9
        paths[label] = (result.times, result.series["adopters"])

    fig, ax = figure(height_in=2.4)
    for i, (label, _) in enumerate(SCENARIOS):
        t, y = paths[label]
        ax.plot(t, y, color="black", linestyle=DASHES[i])
    ax.axhline(CEILING, color="black", linewidth=0.5, linestyle=DASHES[3])
    ax.text(0.4, CEILING + 22, "declared ceiling, 900", fontsize=6.5, ha="left", va="bottom")

    ax.set_xlim(0, 20)
    ax.set_ylim(0, 1080)
    ax.set_yticks([0, 250, 500, 750, 1000])
    ax.set_xticks([0, 5, 10, 15, 20])
    ax.set_xlabel("week")
    ax.set_ylabel("adopters")

    t, y = paths["aggressive"]
    ax.text(6.3, y[6] + 5, "aggressive, 0.60", fontsize=6.8, ha="right", va="bottom")
    t, y = paths["base"]
    ax.text(12.4, y[12] - 20, "base, 0.30", fontsize=6.8, ha="left", va="top")
    t, y = paths["cautious"]
    ax.text(15.5, y[15] + 25, "cautious, 0.05", fontsize=6.8, ha="right", va="bottom")
    for label, _ in SCENARIOS:
        ax.text(20.2, paths[label][1][-1], f"{records[label].outputs['adopters']:.1f}",
                fontsize=6.3, ha="left", va="center")

    fig.tight_layout()
    save(fig, "scenario-spread")


if __name__ == "__main__":
    main()
