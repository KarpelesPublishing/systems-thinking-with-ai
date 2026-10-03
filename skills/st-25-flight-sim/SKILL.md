---
name: st-25-flight-sim
description: "Teach or audit management flight-simulator scenarios, retained constraints, reproducible records, and evidence-limited narratives in Chapter 25. Runs the chapter's model on the user's own inputs with notebooks/25-flight-sim.ipynb."
---

# Chapter 25: Turn Models into Management Flight Simulators

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/25-flight-sim.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/25-flight-sim/reader.html.

## Method

### Inputs and workflow

Obtain the base document, named policy levers, uncertainty ranges, fixed constraints, requested output names, effective settings, and scenario labels. Keep policy choices separate from uncertain assumptions and outcome targets.

1. Check all output and constraint names before running. Require finite ordered bounds with at least one endpoint. Scenarios may override parameters and starting stocks; setting an auxiliary outcome is not a policy experiment.
2. Compare named scenarios under common numerical settings and retain each scenario's overrides, effective model hash, requested outputs, all constraints including satisfied ones, and breaches across the path.
3. For replay, preserve the base document and implementation alongside the record. Omitted settings use document dt and horizon, Euler, and seed zero; the record snapshots effective settings so later caller mutation does not rewrite it.
4. Constrain explanations to available quantities and the strength of the evidence. Return a traceable comparison with visible breaches and a clear decision question; distinguish assumption scenarios from probabilities or stochastic sampling distributions.

### Limits and handoffs

The record contains named endpoint outputs and path-based breach messages, not the full trajectory. supported_by_record checks supplied variable names, not the truth of a free-form narrative. An unknown constraint must not silently disappear, and satisfying a bound does not validate the model or authorize a real intervention.

Use Chapter 7 for the decision, Chapter 19 for numerical tolerances, Chapter 22 for runtime records, Chapter 30 for robust policy comparisons, and Chapter 40 for the capstone workflow.

## Apply it to the user's inputs

1. Open `notebooks/25-flight-sim.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Constraint`: A bound the scenario is not permitted to violate, checked after the run.
- `class ScenarioRecord`: A run record to retain with its preserved model document and implementation version.
- `class ScenarioRunner`: Runs named scenarios against one model and logs each one.
- `supported_by_record(statement_variables: set[str], record: ScenarioRecord)`: Which variables in a proposed narrative the replay record cannot support.

Demonstrations in the notebook, with the chapter's settings:

1. Three scenarios against a declared ceiling: `scenario_spread(imitation=0.3, ceiling=900.0)`. Settings offered: `imitation` in [0.05, 0.3, 0.6]; `ceiling` in [900.0, 1100.0].
2. The settings belong in the record: `replay_settings(solver='euler', dt=1.0)`. Settings offered: `solver` in ['euler', 'rk4']; `dt` in [1.0, 0.25].
3. Averaging scenarios shows a path nobody ran: `averaged_lines(pair='ba', week=20)`. Settings offered: `pair` in ['cb', 'ca', 'ba']; `week` in [10, 20].
4. A narrative may cite only the record: `narrative_check(mention='b', overrides='one')`. Settings offered: `mention` in ['a', 'b', 'c', 'd']; `overrides` in ['one', 'two'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Scenario Base (imitation 0.30); Adopters at week 20 937.7; Highest adopters 937.7; Ceiling 900; Constraint breaches 1
- Demonstration 2: A settings euler, step 1.00; A adopters 937.70; B adopters (euler, step 1.00) 939.87; B minus A as read 2.17; B minus A at equal settings 2.17; Model hash A 05bc66d66e9fe2a0; Model hash B d8a46a6f96bf7fa6
- Demonstration 3: Scenarios averaged base and aggressive; Week read 20; Base at that week 937.7; Aggressive at that week 1000.0; Average 968.8; Nearest scenario Base (937.7) and Aggressive (1000.0) (a tie); Distance to nearest scenario 31.1
- Demonstration 4: Record holds adopters, imitation; Narrative names adopters, marketing_spend; Flagged as unsupported marketing_spend

Copyright Jason Karpeles. All rights reserved.
