---
name: st-32-service-growth
description: "Explain or test the Chapter 32 service-growth case: load, quality, churn, attrition replacement, hiring response, and a smooth intake taper that may improve quality while shrinking customers. Runs the chapter's model on the user's own inputs with notebooks/32-service-growth.ipynb."
---

# Chapter 32: Growth Can Destroy the Engine of Growth

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/32-service-growth.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/32-service-growth/reader.html.

## Method

### Inputs and decision

Collect the customer and workforce paths, effective capacity definition, experience and ramp assumptions, intake policy, attrition rate, churn response, horizon and quality constraint. Distinguish an illustrative scenario from measured organizational data.

### Work the question

1. Trace customers through referrals and churn, workforce through hiring and attrition, and quality through lagged load. Compute load from effective capacity and identify which capacity term actually binds in the run.
2. Reproduce the stressed comparison with intake 0.25, churn sensitivity 1.2, hiring aggression 0.10 or 0.25, and 80 periods. Do not rely on the milder `Policy()` defaults to reproduce the chapter opening.
3. Check average experience against the ramp. In the displayed stressed runs it remains above the ramp, so dilution does no work; workforce loss from attrition outrunning hiring explains capacity loss. That replacement failure also exists with zero intake growth.
4. Explain the taper as `max(0, min(1, (quality - floor)/(1 - floor)))`. Its floor is the zero-intake point, not an activation threshold. Compare quality and customer counts together.
5. Examine churn sensitivity, attrition and hiring feasibility before recommending a measurement. Probe alternate churn structures and senior training load rather than treating a parameter sweep as structural robustness.
6. Return the loop diagnosis, observed versus constructed quantities, conditional policy comparison, earliest reliable leading indicator, and omitted costs with owners for follow-up.

### Limits to preserve

The 80-period customer totals are teaching outputs, not growth forecasts. Faster hiring is unconstrained by a labor market or trainer load. An experience coflow existing in the equations does not show it caused this collapse. Period labels do not establish a calendar duration for a real business.

### Connected chapters

Use Chapter 14 for dominance, Chapter 17 for coflows, Chapter 29 for uncertainty screening, Chapter 30 for constrained policy comparisons, and Chapter 37 when a learning ramp actually binds.

## Apply it to the user's inputs

1. Open `notebooks/32-service-growth.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class State`: Customers, workforce, experience, and quality at one moment.
- `class Policy`: The growth and hiring settings a run is given.
- `effective_capacity(state: State, policy: Policy)`: Heads weighted by experience. Chapter 17's dilution, in the growth loop.
- `load(state: State, policy: Policy)`: Customers divided by experience-weighted capacity.
- `step(state: State, policy: Policy, dt: float=1.0)`: One period. All flows read the state at the start, then all stocks are written.
- `run(policy: Policy, periods: int=60, start: State | None=None)`: Advance the business and return every period's state.
- `summary(path: list[State], policy: Policy)`: The few numbers a reader should carry out of a run.

Demonstrations in the notebook, with the chapter's settings:

1. Same growth policy, two hiring speeds: `hiring_speed(hiring_aggression=0.1, intake_rate=0.25)`. Settings offered: `hiring_aggression` in [0.1, 0.15, 0.2, 0.25]; `intake_rate` in [0.15, 0.25].
2. Throttling intake makes the business smaller: `intake_throttle(quality_floor=0.0, hiring_aggression=0.1)`. Settings offered: `quality_floor` in [0.0, 0.6, 0.7]; `hiring_aggression` in [0.1, 0.25].
3. Which parameter decides the outcome: `which_parameter(parameter='churn_sensitivity', setting='low')`. Settings offered: `parameter` in ['churn_sensitivity', 'attrition', 'customers_per_head', 'ramp_years']; `setting` in ['low', 'high'].
4. The load ratio crosses one while the dashboard is green: `load_signal(intake_rate=0.25, hiring_aggression=0.1)`. Settings offered: `intake_rate` in [0.15, 0.25, 0.35]; `hiring_aggression` in [0.1, 0.25].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Hiring aggression 0.10; Referral intake rate 0.25; Peak customers 185.5; Customers after 80 periods 22.3; Lowest quality 0.65
- Demonstration 2: Quality floor none; Hiring aggression 0.10; Peak customers 185; Customers after 80 periods 22.3; Lowest quality 0.65
- Demonstration 3: Parameter moved Churn sensitivity to quality; Value used 0.60; Customers after 80 periods 102.4; Base run, customers after 80 periods 22.3; Change from base 80.1; Smallest experience weight 1.00
- Demonstration 4: Referral intake rate 0.25; Hiring aggression 0.10; Highest load in the run 1.71; First period with load above 1 1; Customers in that period 125.0; Quality in that period 1.00

Copyright Jason Karpeles. All rights reserved.
