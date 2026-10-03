---
name: st-12-stocks-flows
description: "Construct and audit stocks, flows, declared sources and sinks, exact unit labels, and constrained transfers. Classify state from initial values and update rules rather than units alone. Runs the chapter's model on the user's own inputs with notebooks/12-stocks-flows.ipynb."
---

# Chapter 12: Stocks, Flows, Sources, and Sinks

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/12-stocks-flows.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/12-stocks-flows/reader.html.

## Method

For each candidate state, ask what initial value is retained, what update changes it, and whether it can be recomputed from current variables. Rate and ratio units do not rule out state: velocity accumulates acceleration and a demand estimate retains memory. A ratio computed from two modeled populations is an auxiliary unless independently evolved with a consistency obligation.

Give each flow two endpoints, either internal stocks or declared boundary sources and sinks. Declare the stock quantity label, flow rate label, and time convention for `dt`. The chapter code compares exact quantity and common time labels; it neither converts units nor performs general dimensional algebra. Convert mismatched time bases before stepping.

Run `check()` before execution and disposition every warning. A cumulative counter without outflow or a reserve without inflow may be intentional. A dangling endpoint is a structural defect. Sources assumed unlimited and sinks assumed to remove work permanently belong in the boundary ledger with review triggers.

Compute availability limits on flows rather than silently clamping stocks after shipping nonexistent goods. Check internal-transfer totals and boundary net residuals each interval. These checks reconcile recorded net accounting; they cannot prove all gross movements were recorded.

Return the state classification, endpoint list, unit convention, warning decisions, and an invariant with a test. Handoffs: Chapter 4 for accumulation residuals, Chapter 10 for boundary assumptions, Chapter 13 for perceptions and auxiliaries, Chapter 19 for the numerical step.

## Apply it to the user's inputs

1. Open `notebooks/12-stocks-flows.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Flow`: A rate moving a quantity from one endpoint to another.
- `class System`: A set of named stocks and the flows that move quantities between them.
- `total_in_system(system: System)`: Everything currently held inside the boundary.
- `conservation_residual(before: System, after: System, rates: dict[str, float], dt: float=1.0)`: What entered from sources minus what left to sinks, against the change in total.

Demonstrations in the notebook, with the chapter's settings:

1. A tub with no drain can only grow: `missing_drain(tap=10.0, drain='present')`. Settings offered: `tap` in [4.0, 10.0, 14.0]; `drain` in ['present', 'missing'].
2. Conservation as an executable claim: `endpoint_accounting(drain=4.0, drain_goes_to='sink')`. Settings offered: `drain` in [4.0, 7.0, 10.0]; `drain_goes_to` in ['sink', 'undeclared'].
3. A clamp hides a mechanism; a limited flow names it: `clamp_or_limit(requested=70.0, method='clamp')`. Settings offered: `requested` in [30.0, 50.0, 70.0]; `method` in ['clamp', 'limit'].
4. Units as a type system: a rate times a time: `rate_times_time(dt=1.0, keep_dt='kept')`. Settings offered: `dt` in [0.5, 1.0, 2.0, 4.0]; `keep_dt` in ['kept', 'dropped'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Structural check no problems; Net flow (l/min) 6; Level after 8 minutes (l) 98
- Demonstration 2: Drain empties into declared sink; Change in the total (l) 6; Net crossing at declared boundary (l) 6; Conservation residual (l) 0; Structural check no problems
- Demonstration 3: Requested shipments (units) 70; Shipped (units) 70; Inventory after the week 0; Unmet orders (units) 0; Conservation residual (units) 20
- Demonstration 4: Step length (weeks) 1.00; Correct inventory (units) 240; Inventory with dt dropped (units) 240; Shown 240; A flow unit of just 'units' refused (no time base)

Copyright Jason Karpeles. All rights reserved.
