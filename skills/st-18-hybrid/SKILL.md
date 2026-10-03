---
name: st-18-hybrid
description: "Teach or audit a hybrid model boundary, variable ownership, feedback sampling, and batch residence statistics in Chapter 18; distinguish the teaching backlog proxy from a discrete-event patient queue. Runs the chapter's model on the user's own inputs with notebooks/18-hybrid.ipynb."
---

# Chapter 18: Events, Queues, Agents, and Hybrid Models

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/18-hybrid.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/18-hybrid/reader.html.

## Method

### Inputs and workflow

Name the decision each regime answers, fields crossing in each direction, units, owners, both directional exchange schedules, held values, arrival rules, and the exact feedback statistic.

1. Justify coupling by a specific failure of a single regime. Choose aggregate, discrete event, or agent detail from the mechanism that the decision requires.
2. Declare the interface before equations: fields, directions, units, sampling times, ownership, and what stays fixed between samples. Check undeclared payload fields and double counting.
3. For the chapter code, identify mean_residence as arrival-to-batch-clearance time. It includes boundary waiting, omits unfinished patients, and is zero for an empty cleared batch. Staffing crosses hourly; exchange_every only samples feedback to staffing.
4. Compare the same arrivals and seed under alternative feedback intervals. Report finite-run staffing variability and the averaging denominator, then test the two halves and the seam separately. Return the boundary contract and explicit proxy limitations.

### Limits and handoffs

The chapter code rounds hourly clearance capacity and sorts arrivals oldest first. It schedules no individual service starts or completions. Its mean of hourly batch means is not patient-weighted waiting time, and sixty-hour variability does not establish steady-state stability.

Use Chapter 6 for regime choice, Chapter 10 for queue aggregation, Chapter 16 for information delay, Chapter 24 for cross-tool claim strength, and Chapter 34 for patient-level flow.

## Apply it to the user's inputs

1. Open `notebooks/18-hybrid.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Interface`: What crosses the boundary, in which direction, and in what unit.
- `class AggregateStaffing`: Staff level closes part of the gap to a target derived from observed residence.
- `class PatientQueue`: A batch-clearing backlog proxy with arrival-to-clearance residence times.
- `run_coupled(periods: int, interface: Interface | None=None, seed: int=3)`: Send staffing every hour and sample backlog feedback at the declared interval.

Demonstrations in the notebook, with the chapter's settings:

1. Exchange frequency is a modeling decision: `exchange_frequency(exchange_every=8)`. Settings offered: `exchange_every` in [1, 2, 4, 8].
2. Nine patients per period become nine arrival events: `queue_alone(servers=9, arrivals=9.0)`. Settings offered: `servers` in [7, 8, 9]; `arrivals` in [9.0, 10.0].
3. The staffing rule alone has an equilibrium: `aggregate_alone(wait=0.75, adjustment_time=4.0)`. Settings offered: `wait` in [0.25, 0.5, 0.75, 2.0]; `adjustment_time` in [4.0, 8.0].
4. Does the frequency finding survive another seed?: `seed_check(seed=5, periods=60)`. Settings offered: `seed` in [3, 5, 7, 9]; `periods` in [30, 60].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Exchange every (periods) 8; Staffing volatility 4.75; Staff range 6.6 to 27.7; Mean residence (hours) 0.61; Volatility against exchanging every period 5.42
- Demonstration 2: Arrivals per period 9; Servers 9; Patients waiting after 12 periods 0; Mean residence in the last period (hours) 0.50; Mean residence in the first period (hours) 0.31
- Demonstration 3: Staff the rule aims at 15.0; Staff after 1 period 11.25; Staff after 40 periods 15.00; Gap still open after 40 periods 0.00
- Demonstration 4: Volatility, every period 0.88; Volatility, every 8 periods 4.75; Ratio 5.42; Chapter's seed 5 over 60 periods 0.88 and 4.75

Copyright Jason Karpeles. All rights reserved.
