---
name: st-17-cohorts
description: "Teach or audit workforce cohorts, aging chains, experience coflows, and headcount versus effective capacity in Chapter 17, including quarterly updates with experience measured in years. Runs the chapter's model on the user's own inputs with notebooks/17-cohorts.ipynb."
---

# Chapter 17: Cohorts, Aging Chains, and Coflows

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/17-cohorts.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/17-cohorts/reader.html.

## Method

### Inputs and workflow

Collect band populations, total person-years per band, hires per quarter, maturation and attrition fractions per quarter, step in quarters, productivity ramp in years, and the decision horizon.

1. Compute average experience as total experience divided by people, retaining the population distribution when nonlinear productivity depends on it. Do not replace unlike people by their mean before applying a cap without checking the bias.
2. Transfer experience with people at the departing band mean, add 0.25 times dt person-years per person present at step start, and scale hires by dt. New hires begin aging on the next update in this simultaneous Euler approximation.
3. Require dt * (maturation + attrition) to be strictly below one for each nonterminal band, with only attrition leaving the terminal band. Reduce the step when the guard fails, then compare refinement at a shared physical horizon.
4. Report headcount, experience distribution, and effective capacity together. Check people and experience balances separately, including created experience. State training overhead and within-band variation as omissions when they are not represented.

### Limits and handoffs

The chapter code approximates capacity from each band mean. Merging bands preserves totals but can change capped capacity. Continuity of average experience is not an invariant because hiring and departures can mix populations abruptly. A four-year capped ramp here is not Chapter 37's exponential time constant.

Use Chapter 12 for conservation, Chapter 16 for transit delays, Chapter 19 for Euler refinement, and Chapter 37 for the full hiring pipeline.

## Apply it to the user's inputs

1. Open `notebooks/17-cohorts.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `validate_number(value: float, name: str)`: Reject non-numeric or non-finite values used by the teaching functions.
- `class Band`: One tenure band: how many people, and how much experience they hold between them.
- `advance(bands: list[Band], hires: float, maturation: list[float], attrition: list[float], dt: float=1.0)`: Move people and their experience one step along the chain.
- `headcount(bands: list[Band])`: People across every band, which conservation must preserve.
- `total_experience(bands: list[Band])`: Person-years across every band, the coflow's total.
- `average_experience(bands: list[Band])`: Experience per person; batched mixing can change the ratio discontinuously.
- `effective_capacity(bands: list[Band], ramp_years: float=2.0)`: Capacity approximated from each band's mean experience.

Demonstrations in the notebook, with the chapter's settings:

1. Experience cannot be left behind: `experience_leaves(attrition=0.5, dt=0.01, model='carried')`. Settings offered: `attrition` in [0.2, 0.5]; `dt` in [0.01, 0.1]; `model` in ['carried', 'parallel'].
2. What the surge does: `surge(hires=40.0, ramp=4.0)`. Settings offered: `hires` in [10.0, 20.0, 40.0, 60.0]; `ramp` in [2.0, 4.0].
3. Read headcount and average experience together: `three_curves(scenario='surge', steps=3)`. Settings offered: `scenario` in ['surge', 'aging', 'exodus']; `steps` in [1, 3].
4. The recommendation that reverses: `per_head(horizon=2, ramp=4.0)`. Settings offered: `horizon` in [1, 2, 3, 4]; `ramp` in [2.0, 4.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: People in the band after 19.90; Total experience after (person-years) 39.85; Average experience after (years) 2.003; Change in the average (years) 0.003; Aging alone would add (years) 0.0025
- Demonstration 2: Headcount 100 to 193.4; Headcount rise (percent) 93; Effective capacity 90.0 to 96.2; Capacity rise (percent) 7; Junior average experience (years) 2.00 to 0.46
- Demonstration 3: Scenario Hiring surge; Headcount 100 to 193.4 (rising); Average experience (years) 6.90 to 3.59 (falling); Reading growing and diluting at once
- Demonstration 4: Heads added by hiring 76.0; Capacity gained 6.53; Capacity per head added 0.09; Shortfall against 1.00 per head 0.91

Copyright Jason Karpeles. All rights reserved.
