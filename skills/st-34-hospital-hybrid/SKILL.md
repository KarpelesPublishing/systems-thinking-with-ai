---
name: st-34-hospital-hybrid
description: "Audit hospital or service-queue subgroup outcomes using Chapter 34, including completed versus standardized means, unserved patients, priority rules, equity gaps, and the limitations of the batch staffing model. Runs the chapter's model on the user's own inputs with notebooks/34-hospital-hybrid.ipynb."
---

# Chapter 34: Hybrid Case: Hospital Capacity and Patient Flow

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/34-hospital-hybrid.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/34-hospital-hybrid/reader.html.

## Method

### Inputs and decision

Obtain group definitions and arrival shares, scheduling and staffing rules, run horizon and seed, completed counts and waits per group, unfinished elapsed waits, objective definitions, and proposed subgroup constraints.

### Work the question

1. Keep identical arrivals and seeds when comparing FIFO and shortest-first. Explain that the chapter code clears a period-end batch with a service limit from staffing divided by a weighted multiplier; it is not individual clinicians completing visits.
2. Report completed count, completed mean, high percentile, and unfinished count and elapsed wait for every group. If a group has no completions, report the mean as unavailable; the helper zero is not evidence of zero waiting.
3. Distinguish pooled completed-patient mean from the arrival-share-standardized mean of group completed means. Neither includes eventual waits of unfinished patients. State the denominator whenever quoting an overall mean.
4. Inspect the feedback statistic separately: staffing reads each period's served mean, and averaging those reports weights periods rather than patients. The chapter code does not implement complex-group p90 feedback.
5. Identify the staffing target's dependence on current staffing and the absence of an establishment anchor. Do not attribute every difference to subgroup scheduling or claim the watched overall mean improves in this run.
6. Present group outcomes beside any throughput objective, define prohibited objectives and protected tails with the affected decision owners, and retain all unserved observations. A computed gap does not determine what inequality is acceptable.

### Limits to preserve

This is an unfitted teaching approximation with synthetic groups, not a clinical staffing recommendation. The two overall completed means worsen under shortest-first, while routine waiting improves. A zero or missing group outcome makes an unqualified equity-gap ratio misleading.

### Connected chapters

Use Chapter 1 for the opening policy-effect case, Chapter 10 for aggregation and omitted groups, Chapter 18 for the anchored staffing example, Chapter 30 for shared-draw constraints, and Chapter 40 for accountable decision review.

## Apply it to the user's inputs

1. Open `notebooks/34-hospital-hybrid.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Group`: A patient group with its own share of arrivals and its own service demand.
- `class StaffingPolicy`: The staffing rule and the scheduling discipline it runs under.
- `run(policy: StaffingPolicy, periods: int=60, arrivals: float=18.0, groups: tuple[Group, ...]=DEFAULT_GROUPS, seed: int=5)`: Run the coupled system and return outcomes per group, not only in total.
- `equity_gap(outcome: dict[str, object])`: Worst group's mean wait divided by the best group's. One number, deliberately.
- `prohibited_objectives()`: Objectives this model must never be optimized against.

Demonstrations in the notebook, with the chapter's settings:

1. The policy that improves the average: `policy_by_group(priority='fifo', complex_share=0.25)`. Settings offered: `priority` in ['fifo', 'shortest_first']; `complex_share` in [0.1, 0.25, 0.5].
2. The staffing rule swings and does not settle: `staffing_loop(priority='fifo', adjustment_time=4.0)`. Settings offered: `priority` in ['fifo', 'shortest_first']; `adjustment_time` in [2.0, 4.0, 8.0].
3. A mean can hide the tail: `mean_versus_tail(statistic='mean', priority='fifo')`. Settings offered: `statistic` in ['mean', 'p90']; `priority` in ['fifo', 'shortest_first'].
4. Stress the arrivals until a group disappears: `arrival_stress(arrivals=18, priority='fifo')`. Settings offered: `arrivals` in [12, 18, 24, 36]; `priority` in ['fifo', 'shortest_first'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Scheduling First come, first served; Complex share of arrivals 0.25; Routine mean wait 1.23; Complex mean wait 1.17; Population mean wait 1.22; Equity gap 1.05; Patients never served 0
- Demonstration 2: Scheduling First come, first served; Adjustment time 4; Lowest staff 8.6; Highest staff 28.7; Mean staff, last 20 periods 21.3; Patients never served 0
- Demonstration 3: Scheduling First come, first served; Statistic shown Mean wait; Routine 1.23; Complex 1.17; Gap (worst over best) 1.05; Complex 90th percentile 2.15
- Demonstration 4: Arrivals per period 18; Scheduling First come, first served; Routine served 811; Complex served 269; Left in the queue 0; Equity gap 1.05

Copyright Jason Karpeles. All rights reserved.
