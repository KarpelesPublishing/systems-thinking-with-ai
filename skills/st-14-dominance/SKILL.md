---
name: st-14-dominance
description: "Teach or audit feedback loop dominance, link-freeze knockout scores, and regime handovers in Chapter 14; distinguish path attribution from the payoff of a proposed intervention. Runs the chapter's model on the user's own inputs with notebooks/14-dominance.ipynb."
---

# Chapter 14: Feedback and Loop Dominance

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/14-dominance.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/14-dominance/reader.html.

## Method

### Inputs and workflow

Obtain the equations or explicit loop paths, starting state, time window, observable, link to freeze, reference value, and candidate interventions with costs. A drawing alone supports hypotheses rather than a numerical dominance ranking.

1. Derive or trace the influence paths, including flow targets. Separate feedback through a stock or delay from an algebraic cycle that the explicit runtime cannot order.
2. For teaching, calculate the full adoption rate and each zero-reference knockout at the same adopter state. For an audit, record the actual cut and freeze convention before comparing magnitudes.
3. Compare early and late windows along the same scenario. Report the handover state, time, absolute observable, and any sensitivity to the reference choice. Shared loops need not have additive scores.
4. To answer a policy question, turn each action into an explicit parameter or rule change and compare trajectories under a common objective, cost, and horizon. Return the dominance table and the separate intervention comparison, or state which comparison remains unexecuted.

### Limits and handoffs

A leading finite knockout score is not a marginal return, a percentage share of causation, or evidence that a weaker loop can be removed. A delayed balancing loop can oscillate without a two-loop handover. Numerical rankings apply to the model and path that produced them.

Use Chapter 8 to review causal support, Chapter 21 for dependency-derived loop enumeration, Chapter 19 to test numerical behavior, and Chapters 29 and 30 to compare interventions.

## Apply it to the user's inputs

1. Open `notebooks/14-dominance.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Diffusion`: Adoption driven by outside influence and by contact with existing adopters.
- `run(model: Diffusion, steps: int, initial: float=1.0, dt: float=1.0)`: The adopter path with both loops live.
- `contributions(model: Diffusion, path: list[float])`: Finite rate differences under zero-reference link freezes, not policy payoffs.
- `dominant_loop(model: Diffusion, path: list[float])`: The loop with the larger contribution at each point.
- `handover_step(model: Diffusion, path: list[float])`: The step where dominance changes hands. None when it never does.

Demonstrations in the notebook, with the chapter's settings:

1. Two loops through one stock: `adoption_path(imitation=0.3, innovation=0.01)`. Settings offered: `imitation` in [0.15, 0.3, 0.45]; `innovation` in [0.01, 0.03].
2. Knockout at one state: `knockout_rates(adopters=500.0, imitation=0.3)`. Settings offered: `adopters` in [100.0, 300.0, 500.0, 800.0]; `imitation` in [0.15, 0.3].
3. The handover: `handover(imitation=0.3, steps=40)`. Settings offered: `imitation` in [0.1, 0.3, 0.5]; `steps` in [10, 40].
4. The same intervention in two regimes: `intervention_by_regime(step=4, intervention='referral')`. Settings offered: `step` in [4, 12, 25]; `intervention` in ['referral', 'market'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Adopters at step 10 340; Adopters at step 20 938; Adopters at step 40 1000; Peak adoption rate 80.1 at step 12
- Demonstration 2: Rate, both loops live 80.0; Rate, word of mouth cut 5.0; Rate, saturation cut 160.0; Contribution of word of mouth 75.0; Contribution of saturation 80.0; Leading loop saturation
- Demonstration 3: Handover step 12; Leader at the start word of mouth; Leader at the end saturation; Peak of word of mouth 75.0; Largest saturation 310.0
- Demonstration 4: Adopters at this step 63; Leading loop word of mouth; Baseline rate 27.1; Rate with the intervention 33.0; Change in the rate 5.9

Copyright Jason Karpeles. All rights reserved.
