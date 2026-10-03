---
name: st-33-technical-debt
description: "Analyze Chapter 33 technical debt as an accumulated stock, compare standing repayment shares across review horizons, and distinguish constructed debt or morale from observable rework and delivery. Runs the chapter's model on the user's own inputs with notebooks/33-technical-debt.ipynb."
---

# Chapter 33: Technical Debt as a Stock

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/33-technical-debt.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/33-technical-debt/reader.html.

## Method

### Inputs and decision

Identify the delivery horizon, pressure and repayment rules, available versus nominal capacity, debt and defect definitions, rework observations, proxy evidence, and any proposed claim about an AI coding intervention.

### Work the question

1. Draw debt inflow from delivery shortcuts and repayment outflow; distinguish debt from discovered defects. Track morale as a state and features delivered as a legitimate cumulative counter.
2. Compare policy paths at the actual decision horizon. The teaching no-repayment policy leads at period 12; 20 percent repayment overtakes it at period 26 and leads by period 60. Do not call the periods years or quarters without a defined time base.
3. Inspect loop polarity from the equations. Reduced capacity lowers delivery and new debt here; no pressure response feeds shortcuts upward. Repayment is stock-limited near zero and capacity-limited later, so its feedback is not always balancing.
4. Put a system of record beside defects, rework and shipped items. Label debt and morale as proxies or constructed levels with scale, uncertainty and possible bias. A plotted numeric proxy does not become a measurement.
5. Sweep the repayment share and horizon, then test drag and shortcut assumptions. A broad conditional optimum does not make 20 or 35 percent a universal rule.
6. For an AI adoption claim, separate a measured before-and-after change from causal attribution. Record task mix, staffing, release-cycle and review changes; propose an appropriate comparison before crediting the tool.

### Limits to preserve

The teaching model has no empirical estimate of AI coding effects. It omits production incidents avoided by better testing and the shortcut response to pressure. A temporary remediation project needs its own duration and restart rule before comparing it with standing repayment.

### Connected chapters

Use Chapter 11 for proxy evidence, Chapter 12 for accumulated stocks, Chapter 29 for sensitivity, Chapter 30 for debt ceilings or capacity floors, and Chapter 31 for review discipline.

## Apply it to the user's inputs

1. Open `notebooks/33-technical-debt.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class State`: Delivery, debt, defects, and morale at one moment.
- `class Policy`: Capacity, pressure, and the share reserved for repayment.
- `available_capacity(state: State, policy: Policy)`: What is left after debt drag and morale. The quantity nobody measures.
- `step(state: State, policy: Policy, dt: float=1.0)`: One period: deliver, accrue debt, surface defects, move morale.
- `run(policy: Policy, periods: int=60, start: State | None=None)`: Advance the team and return every period's state.
- `summary(path: list[State], policy: Policy)`: The few numbers a reader should carry out of a run.
- `observable_measures()`: What can be counted, and what has to stay a proxy.

Demonstrations in the notebook, with the chapter's settings:

1. The review window picks the winner: `review_window(review_period=12, repayment_share=0.2)`. Settings offered: `review_period` in [12, 24, 48, 60]; `repayment_share` in [0.2, 0.35].
2. Capacity is not what the plan says: `capacity_gap(situation='after a year', drag=0.02)`. Settings offered: `situation` in ['fresh', 'after a quarter', 'after a year']; `drag` in [0.01, 0.02].
3. Rework share moves before delivery does: `rework_signal(repayment_share=0.0, period=12)`. Settings offered: `repayment_share` in [0.0, 0.2]; `period` in [6, 12, 26, 60].
4. Test the conclusion against the proxy's range: `drag_range(drag=0.02, horizon=60)`. Settings offered: `drag` in [0.005, 0.01, 0.02, 0.03]; `horizon` in [24, 60].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Review at period 12; Push hard, features 100.1; Repay 20%, features 87.2; Repaying minus push hard (-12.9); Debt under push hard 50.1
- Demonstration 2: Debt carried 115.0; Morale 0.82; Drag coefficient 0.020; Available capacity 6.31; Plan over reality 1.58
- Demonstration 3: Repayment share 0.00; Period read 12; Usable capacity 8.65; Rework share 24.0 percent; Features delivered that period 6.57
- Demonstration 4: Drag coefficient 0.020; Horizon (periods) 60; Push hard, features 230.1; Repay 20%, features 319.0; Repaying minus push hard 88.9

Copyright Jason Karpeles. All rights reserved.
