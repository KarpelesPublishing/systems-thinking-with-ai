---
name: st-09-archetypes
description: "Use systems archetypes as competing hypothesis templates, distinguish fixed from eroding limits, and turn a recognizable story into observations that could challenge it. Runs the chapter's model on the user's own inputs with notebooks/09-archetypes.ipynb."
---

# Chapter 9: System Archetypes as Hypothesis Templates

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/09-archetypes.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/09-archetypes/reader.html.

## Method

Identify the persistent behavior and attempted fixes before selecting a template. Instantiate plausible archetypes with actual quantities and units: limits to growth, shifting the burden, fixes that fail, and tragedy of the commons. State which candidates fit poorly and why instead of forcing every story into a template.

For each serious candidate, record the boundary, horizon, predicted behavior, observed record, side effect, nearest rival, and falsifier. The useful output is the measurement that would distinguish explicit mechanisms. If no observed record exists, keep the result as a proposed investigation. Mechanisms may coexist or dominate at different times; they need not be mutually exclusive.

For limits to growth, determine whether the limiting capacity is fixed outside the model or erodes inside it. When comparing the supplied engines, hold initial value, capacity, growth rate, step, and horizon equal. The chapter's two illustrative calls differ in rate and duration, so those raw numbers alone do not isolate erosion.

Use leverage-point language to generate possible interventions, then test their actual effects. A named information-flow intervention has no universal effect-size advantage. Return rival hypotheses, distinguishing observations, and their evidence status, rather than an archetype diagnosis or policy verdict.

Handoffs: Chapter 3 for behavior targets, Chapter 8 for links, Chapter 10 for boundary tradeoffs, Chapter 17 for training cohorts, Chapter 38 for construction-delay mechanisms.

## Apply it to the user's inputs

1. Open `notebooks/09-archetypes.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `validate_number(value: float, name: str)`: Reject non-numeric or non-finite values used by the teaching functions.
- `fixed_limit(initial: float, capacity: float, rate: float, steps: int, dt: float=1.0)`: Boundary A: the limit is exogenous. Growth approaches it and stops.
- `eroding_limit(initial: float, capacity: float, rate: float, erosion_rate: float, steps: int, dt: float=1.0)`: Boundary B: the limit is endogenous, consumed by the growth it constrains.
- `settles(path: list[float], tolerance: float=0.01)`: True when the path stops moving. The observable that separates the two boundaries.
- `peaks_then_falls(path: list[float], margin: float=0.05)`: True when the path rises to a peak and ends meaningfully below it.

Demonstrations in the notebook, with the chapter's settings:

1. An early limit is easy to dismiss: `limit_multiplier(load_share=0.02, rate=0.3)`. Settings offered: `load_share` in [0.02, 0.1, 0.5, 0.9]; `rate` in [0.3, 0.4].
2. Same engine, two boundaries: `two_boundaries(rate=0.4, horizon=200)`. Settings offered: `rate` in [0.3, 0.4]; `horizon` in [60, 120, 200].
3. The window decides what the record can show: `window_reading(erosion=0.02, window=60)`. Settings offered: `erosion` in [0.005, 0.02]; `window` in [30, 60, 100, 200].
4. One parameter turns B into A: `zero_erosion(erosion_rate=0.0, rate=0.4)`. Settings offered: `erosion_rate` in [0.0, 0.005, 0.02, 0.04]; `rate` in [0.3, 0.4].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Load (units of 100) 2.0; Share of unconstrained rate 0.98; Growth with no limit (per step) 0.60; Growth with the limit (per step) 0.59; Shortfall (per step) 0.01
- Demonstration 2: A: value at the end 100.0; B: peak 87.6; B: step of the peak 20; B: value at the end 2.0; B: capacity at the end 1.9
- Demonstration 3: Peak 87.6; End of record 39.1; 95% of peak 83.2; Last step change (-0.84); Settles no; Peaks then falls yes
- Demonstration 4: Erosion rate 0.000; Largest gap between B and A 0.00; B: value at the end 100.0; B: capacity at the end 100.0; Same path as A yes (tie)

Copyright Jason Karpeles. All rights reserved.
