---
name: st-04-bathtub
description: "Reconstruct a level from inflow and outflow histories, correct bathtub rate-versus-stock errors, and interpret endpoint and interval conservation residuals without claiming record completeness. Runs the chapter's model on the user's own inputs with notebooks/04-bathtub.ipynb."
---

# Chapter 4: The Bathtub Most People Misread

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/04-bathtub.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/04-bathtub/reader.html.

## Method

Require an initial level with its date, separate inflow and outflow rates with common time units, and interval lengths. Compute the net rate in each interval before describing direction. A declining inflow can still increase the stock; compare inflow to outflow, not to its previous value. Multiply a rate by the interval before adding it to a level.

For connected stocks, compute transfers from the same starting state and then update all levels. Evaluate physical bounds explicitly. A numerical floor can conceal a missing mechanism; move to Chapter 12 if availability should constrain a flow.

Audit endpoint conservation first, then interval residuals. Zero at the endpoint only reconciles the net change. Zero in every interval still allows equal omitted inflows and outflows. When completeness matters, reconcile gross flows against the source ledger. Explain what a nonzero discrepancy could mean without assigning a cause from arithmetic alone.

For teaching, ask the reader to predict direction from the net-rate column and reconstruct the full path. Return initial condition, unit convention, path, residuals, and unresolved ledger discrepancies. Use the general update-rule test in Chapter 12 when a rate or ratio may itself be state.

Handoffs: Chapter 11 for source records, Chapter 12 for endpoints and constrained flows, Chapter 19 for integration and time-step behavior.

## Apply it to the user's inputs

1. Open `notebooks/04-bathtub.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `validate_number(value: float, name: str)`: Reject non-numeric or non-finite values used by the teaching functions.
- `net_flow(inflow: float, outflow: float)`: Return the rate at which the stock changes: inflow minus outflow.
- `advance_stock(stock: float, inflow: float, outflow: float, dt: float)`: Advance one stock by its net flow over one time step.
- `integrate(initial: float, inflows: list[float], outflows: list[float], dt: float=1.0)`: Rebuild the whole path of a stock from its initial level and its flow history.
- `conservation_error(path: list[float], inflows: list[float], outflows: list[float], dt: float=1.0)`: Compare the endpoint stock change with total recorded net flow.
- `apply_floor(stock: float, floor: float=0.0)`: Hold a stock at a physical bound. A tank cannot drain past empty.
- `interval_residuals(path: list[float], inflows: list[float], outflows: list[float], dt: float=1.0)`: Compare each interval's stock change with its recorded net flow.

Demonstrations in the notebook, with the chapter's settings:

1. A falling inflow can still fill the tub: `rate_versus_level(inflow_shape='falling', outflow=4.0)`. Settings offered: `inflow_shape` in ['falling', 'rising']; `outflow` in [4.0, 6.0, 8.0, 9.0].
2. The step length turns a rate into an amount: `step_length(dt=1.0, keep_dt='kept')`. Settings offered: `dt` in [1.0, 0.5, 0.25]; `keep_dt` in ['kept', 'dropped'].
3. Read every flow, then write every stock: `two_tubs(drain_fraction=0.5, order='flows first')`. Settings offered: `drain_fraction` in [0.3, 0.5, 0.8]; `order` in ['flows first', 'A first'].
4. A floor is a claim, and conservation can see it: `floor_claim(outflow=9.0, floor='applied')`. Settings offered: `outflow` in [6.0, 9.0, 12.0]; `floor` in ['applied', 'not applied'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Inflow direction falling every minute; Net flow by minute (l/min) 6, 5, 4, 3, 2; Level after 5 minutes (l) 70; Change in level (l) 20
- Demonstration 2: Step length dt (minutes) 1.00; Steps in 5 minutes 5; Litres added per step 6.0; Level after 5 minutes (l) 80
- Demonstration 3: Update order flows first; Flow out of A (l) 50; Flow into B (l) 50; A + B after one step (l) 100; Water created or lost (l) 0
- Demonstration 4: Floor at zero applied; Net flow per minute (-4); Stock after 5 minutes 0; Conservation residual 10

Copyright Jason Karpeles. All rights reserved.
