---
name: st-03-reference-modes
description: "Describe behavior over time as a reference mode, distinguish the six teaching shapes, and assess sampling, noise, and window limits before proposing a cause. Runs the chapter's model on the user's own inputs with notebooks/03-reference-modes.ipynb."
---

# Chapter 3: Events Are Not Explanations

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/03-reference-modes.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/03-reference-modes/reader.html.

## Method

Obtain the series, quantity and unit, observation dates, sampling interval, reporting changes, and every smoothing or exclusion. Write one reference-mode sentence naming variable, window, direction, and observed turning points. Do not insert a cause into that sentence.

Compare the trace with growth, decay, goal seeking, oscillation, S-shaped growth, and overshoot and collapse. Rank only candidates the record can meaningfully discriminate. For each close rival, name the additional observation needed: a ceiling estimate, a longer window beyond the peak, higher frequency sampling, or a defensible noise model. A mixed trace may need separate segments instead of one label.

For teaching, contrast exponential and logistic growth using identical inputs, or add seeded independent measurement error to a known trace. State that a shape generator is a target or constructed example, not evidence for a real mechanism. A short rising section cannot establish a later collapse. Amplitude below single-observation noise is not automatically undetectable across many observations; the sampling and noise assumptions matter.

Return the behavior record, competing labels, unresolved distinctions, and the next measurement.

Handoffs: Chapter 2 for sparse historical events, Chapter 8 for candidate mechanisms, Chapter 19 for numerical artifacts, Chapter 35 for why fit does not confirm structure.

## Apply it to the user's inputs

1. Open `notebooks/03-reference-modes.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `validate_number(value: float, name: str)`: Reject non-numeric or non-finite values used by the teaching functions.
- `exponential_growth(initial: float, rate: float, steps: int, dt: float=1.0)`: Reinforcing growth: the net flow is proportional to the stock itself.
- `exponential_decay(initial: float, rate: float, steps: int, dt: float=1.0)`: Balancing decay toward zero at a rate proportional to what remains.
- `goal_seeking(initial: float, goal: float, adjustment_time: float, steps: int, dt: float=1.0)`: Balancing approach to a goal, closing a fixed fraction of the gap each step.
- `oscillation(level: float, amplitude: float, period: float, steps: int, dt: float=1.0)`: Repeated overshoot and undershoot around a level, with a fixed period.
- `s_shaped_growth(initial: float, capacity: float, rate: float, steps: int, dt: float=1.0)`: Reinforcing growth that a fixed carrying capacity progressively limits.
- `overshoot_and_collapse(initial: float, capacity: float, rate: float, erosion_rate: float, steps: int, dt: float=1.0)`: S-shaped growth against a capacity that the stock itself erodes.
- `add_observation_noise(path: list[float], sd: float, seed: int)`: Return `path` with independent Gaussian measurement error, reproducible from `seed`.

Demonstrations in the notebook, with the chapter's settings:

1. Growth looks like S-shaped growth until the ceiling bites: `growth_or_s_shape(steps_shown=20, capacity=100.0)`. Settings offered: `steps_shown` in [10, 15, 20, 25]; `capacity` in [100.0, 50.0].
2. Decay is goal seeking with the goal at zero: `goal_or_decay(goal=40.0, adjustment_time=4.0)`. Settings offered: `goal` in [0.0, 40.0, 70.0]; `adjustment_time` in [4.0, 8.0].
3. One erosion rate turns a ceiling into a collapse: `erosion(erosion_rate=0.02, rate=0.4)`. Settings offered: `erosion_rate` in [0.0, 0.01, 0.02, 0.05]; `rate` in [0.2, 0.4].
4. Noise hides a slow approach first: `noisy_goal(adjustment_time=4.0, sd=5.0)`. Settings offered: `adjustment_time` in [4.0, 12.0]; `sd` in [1.0, 5.0, 20.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Steps shown 20; Growth level 190.0; S-shaped level 72.4; S-shaped level as a fraction of the ceiling 0.72; Growth level as a fraction of the ceiling 1.90
- Demonstration 2: Goal 40; Adjustment time (steps) 4; Goal seeking after step 1 85.0; Decay after step 1 75.0; Goal seeking after step 30 40.01; Decay after step 30 0.02; Same curve no
- Demonstration 3: Erosion rate 0.02; Growth rate 0.4; Highest level 87.6; Turning point (step) 20; Level at step 200 1.99
- Demonstration 4: Adjustment time (steps) 4; Noise standard deviation 5; Move at step 1 (clean) 25.00; Move at step 10 (clean) 1.88; Steps whose clean move exceeds the noise sd 6 of 60

Copyright Jason Karpeles. All rights reserved.
