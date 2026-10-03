---
name: st-13-expressions
description: "Classify auxiliaries, fixed parameters, stateful perceptions, and decision rules; parse permitted numeric expressions and inspect their dependencies and information assumptions. Runs the chapter's model on the user's own inputs with notebooks/13-expressions.ipynb."
---

# Chapter 13: Auxiliaries, Parameters, and Decision Rules

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/13-expressions.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/13-expressions/reader.html.

## Method

Classify each quantity by its role. An auxiliary is recomputable algebra, a parameter is fixed during a run, a perception carries an initial value and formation rule, and a decision rule describes an actor's action. Do not classify solely from a name or unit. Mark calibrated inputs separately in provenance rather than presenting them as measurements.

For a decision rule, record owner, actual decision frequency, accessible information, constraints, and evidence status. Compare expression dependencies with what the decider can know at decision time. A current true value is not interchangeable with a lagged report. Keep discretionary exceptions visible when they cannot be reduced to algebra.

Parse expressions through the chapter's restricted grammar before evaluation: arithmetic, comparisons, conditional expressions, and default functions min, max, abs, exp, log, sqrt. Missing names are errors. Attribute access, imports, comprehensions, string constants, and unlisted calls are refused. This numeric parser is not a general-purpose sandbox or authority to execute external actions; use trusted numeric inputs and an approved function table.

Test auxiliaries by substitution, perceptions by step responses, and rules at their bounds. For explicit smoothing, monotone approach requires the update step not exceed its positive response time. That response time is not a fixed transport delay.

Return the classified rule, its dependency list, assumptions, and meaningful boundary checks. Handoffs: Chapter 11 for parameter evidence, Chapter 16 for stateful delays, Chapter 21 for algebraic cycles, Chapter 23 for approved function metadata.

## Apply it to the user's inputs

1. Open `notebooks/13-expressions.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class UnsafeExpression`: Raised when an expression asks for something the whitelist does not permit.
- `parse(text: str, functions: dict[str, Callable[..., float]] | None=None)`: Parse an expression and reject every construct outside the whitelist.
- `variables(text: str, functions: dict[str, Callable[..., float]] | None=None)`: Every name an expression reads. The model's dependency edges come from here.
- `evaluate(text: str, values: dict[str, float], functions: dict[str, Callable[..., float]] | None=None)`: Evaluate a whitelisted expression against a supplied set of named values.

Demonstrations in the notebook, with the chapter's settings:

1. A decision rule that never goes negative: `guarded_gap(demand=120.0, adjustment=4.0)`. Settings offered: `demand` in [80.0, 100.0, 120.0, 150.0]; `adjustment` in [4.0, 8.0].
2. A belief that lags the truth: `perception_lag(smoothing_time=4.0, direction='rise')`. Settings offered: `smoothing_time` in [2.0, 4.0, 8.0]; `direction` in ['rise', 'fall'].
3. Dependencies fall out of the parse: `dependency_edges(expression='queue', supply='all')`. Settings offered: `expression` in ['queue', 'gap', 'hiring']; `supply` in ['all', 'one missing'].
4. An auxiliary is tested by arithmetic: `coverage_test(inventory=200.0, shipment_rate=50.0)`. Settings offered: `inventory` in [200.0, 400.0]; `shipment_rate` in [0.0, 50.0, 100.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Gap (demand - capacity) 20; Adjustment rate 5.0; Round(3.7) in a model expression 'round' is not an allowed function
- Demonstration 2: Expected after period 1 105.0; Expected after period 5 115.3; Expected after period 10 118.9; Gap to observed at period 5 4.7; Overshoots the observed value no
- Demonstration 3: Expression backlog / production_delay + safety; Names read (dependency edges) backlog, production_delay, safety; Number of edges 3; Result 25.00
- Demonstration 4: Inventory coverage 4.0 weeks; Target coverage 2 weeks; Against target 2.0 weeks above the target

Copyright Jason Karpeles. All rights reserved.
