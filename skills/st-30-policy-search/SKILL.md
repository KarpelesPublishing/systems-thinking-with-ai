---
name: st-30-policy-search
description: "Compare named policies across shared uncertainty draws with hard bounds, inspect every exclusion, and rank admissible policies by the declared criterion using Chapter 30. Runs the chapter's model on the user's own inputs with notebooks/30-policy-search.ipynb."
---

# Chapter 30: The AI as Policy Searcher

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/30-policy-search.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/30-policy-search/reader.html.

## Method

### Inputs and decision

Collect the model, named actionable policies with owners and reversibility, objective and direction, defended uncertainty ranges, every bound with reason and source, explicit run settings, draw count, and seed.

### Work the question

1. Declare bounds before comparing candidates, including protected outcomes that differ from the objective. Confirm all variable names exist and bounds are finite and ordered. Include the status quo as a candidate.
2. Use identical sampled parameters and draw IDs for every policy. Preserve both sampled and effective values because policy settings override draws on the same parameter.
3. Read the objective and every bound from the same runtime result for each draw. The core code reads final variables; path extrema require explicit path statistics or correctly defined counters. A terminal bound is not an all-time guarantee.
4. Treat runtime failure, nonfinite outcomes, or any bound violation as exclusion. Keep the exact failing draw IDs, outcomes, settings, and reason. Multiple failed bounds on one draw remain separate violations.
5. Report mean and worst outcome for all policies, including exclusions. `recommend` maximizes the smallest sampled objective; reversibility breaks ties within one percent. For a smaller-is-better metric, define the score accordingly or compare with an explicit different ranking.
6. If none is admissible, report no recommendation. Consider additional candidates, model revisions, or openly reviewed constraint changes; do not relax a bound to manufacture a winner.

### Limits to preserve

The worst sampled draw is not a global worst case and range draws do not establish event probabilities. Robustness within one structure cannot address an omitted mechanism. An actionable recommendation still needs the decision owner and omitted-cost review.

### Connected chapters

Use Chapter 7 for decision authority and levers, Chapter 10 for affected parties, Chapter 25 for scenario records, Chapter 29 for range selection, and Chapter 38 for a path-amplitude bound.

## Apply it to the user's inputs

1. Open `notebooks/30-policy-search.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Policy`: A named set of settings, with an owner and whether it can be undone.
- `class Bound`: A constraint that a policy must satisfy in every draw, not on average.
- `class Evaluation`: What a policy did across every draw, including where it failed.
- `evaluate(document: ModelDocument, policy: Policy, uncertainties: list[Uncertainty], objective: str, bounds: list[Bound], draws: int, seed: int, settings: RunSettings | None=None)`: Read the objective and every constraint from the same run for each shared draw.
- `compare(document: ModelDocument, policies: list[Policy], uncertainties: list[Uncertainty], objective: str, bounds: list[Bound], draws: int=40, seed: int=7, settings: RunSettings | None=None)`: Every policy against the same draws, with every bound checked on each run.
- `recommend(evaluations: list[Evaluation])`: Rank by worst case among admissible policies, and say what was excluded and why.

Demonstrations in the notebook, with the chapter's settings:

1. The best average is excluded: `best_average(ceiling=1100.0, draws=25)`. Settings offered: `ceiling` in [1000.0, 1100.0, 1300.0]; `draws` in [10, 25].
2. Every draw, not the average: `draw_or_average(ceiling=1100.0, check='draw')`. Settings offered: `ceiling` in [900.0, 1100.0, 1300.0]; `check` in ['draw', 'average'].
3. Same draws, every policy: `shared_draws(draws=25, design='shared')`. Settings offered: `draws` in [5, 25]; `design` in ['shared', 's8', 's9', 's10'].
4. When no policy is admissible: `no_admissible(candidates='two', ceiling=1100.0)`. Settings offered: `candidates` in ['two', 'three']; `ceiling` in [600.0, 800.0, 1100.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Push: mean, worst case 934.1, 722.4; Push: draws above the ceiling 4 of 25; Steady: mean, worst case 911.9, 705.5; Steady: draws above the ceiling 4 of 25; Hold: mean, worst case 533.6, 413.6; Hold: draws above the ceiling 0 of 25; Recommendation Hold
- Demonstration 2: Judged on every draw; Push excluded; Steady excluded; Hold admissible; Recommendation Hold; First violation message draw 13: adopters=1196 above 1100.0 (support capacity ceiling)
- Demonstration 3: Draws 25; Draw design shared seed 7; Push mean 934.1; Steady mean 911.9; Push minus steady 22.2
- Demonstration 4: Candidates Push, Steady; Ceiling 1100; Push: draws above the ceiling 4 of 25; Steady: draws above the ceiling 4 of 25; Recommendation none: every policy violated a stated constraint

Copyright Jason Karpeles. All rights reserved.
