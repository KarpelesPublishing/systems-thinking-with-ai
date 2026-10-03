---
name: st-29-experiments
description: "Screen decision-relevant uncertainty, compare output swing per measurement cost, and design informative studies using Chapter 29; distinguish sensitivity from expected value of information. Runs the chapter's model on the user's own inputs with notebooks/29-experiments.ipynb."
---

# Chapter 29: The AI as Experiment Designer

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/29-experiments.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/29-experiments/reader.html.

## Method

### Inputs and decision

Identify the decision, feasible policies, chosen metric and horizon, uncertain parameters with defended ranges, study costs, attainable precision, deadline, and any critic findings. If only one output is available, label the result an output screen rather than a policy-choice result.

### Work the question

1. Rank one-at-a-time output swings with other quantities at midpoint. State the metric, horizon and settings; `ranked` accepts settings, while `value_per_cost` and `sample` use the teaching metric defaults of 20 time units at step 1.
2. Divide by positive stated cost only as a screening heuristic. Report the units and do not rename it expected value of information; no study-result probabilities, attainable precision, or utility are computed.
3. Examine joint combinations and interior values near constraint boundaries. A wider joint spread alone does not prove interaction. Compare one parameter's effect at different settings of another.
4. Ask whether the uncertainty concerns magnitude or mechanism. Use an independently supported calibration for a hidden magnitude, a rival structure for a mechanism dispute, and a proposed pilot only for a remaining decision-relevant gap.
5. Record question, kind, attainable precision, possible results and policy changes, cost including whose time, affected-party risk, stopping rule, result, and disposition. Explain what further precision could change before recommending collection.
6. State coverage and remaining gaps when stopping. Equal policy rankings at two endpoints are insufficient unless a justified property rules out interior reversals.

### Limits to preserve

Sensitivity changes no empirical evidence. A uniform range sample is not a probability model of the world. Contrasting busy and quiet teams suggests a learning hypothesis but does not identify a causal load effect. Keep an unexecuted study labeled proposed.

### Connected chapters

Use Chapter 9 for competing mechanisms, Chapter 28 for findings and falsifiers, Chapter 30 for actual constrained policy comparison, Chapter 35 for calibration, and Chapter 37 for learning-curve measurement.

## Apply it to the user's inputs

1. Open `notebooks/29-experiments.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Uncertainty`: One quantity nobody has pinned down, with the range somebody will defend.
- `metric(document: ModelDocument, overrides: dict[str, float], name: str, settings: RunSettings | None=None)`: Run a model under overrides and return one decision quantity.
- `one_at_a_time(document: ModelDocument, uncertainties: list[Uncertainty], decision_metric: str, settings: RunSettings | None=None)`: Swing each uncertainty across its range with the others held at midpoint.
- `ranked(document: ModelDocument, uncertainties: list[Uncertainty], decision_metric: str, settings: RunSettings | None=None)`: Uncertainties ordered by their effect on the decision metric, largest first.
- `value_per_cost(document: ModelDocument, uncertainties: list[Uncertainty], decision_metric: str)`: Output swing divided by stated measurement cost, a screen rather than information value.
- `sample(document: ModelDocument, uncertainties: list[Uncertainty], decision_metric: str, draws: int, seed: int)`: Draw uniformly from every range at once and return the metric for each draw.

Demonstrations in the notebook, with the chapter's settings:

1. Rank uncertainties by their swing: `ranking_by_effect(market='wide', imitation='wide')`. Settings offered: `market` in ['wide', 'mid', 'narrow']; `imitation` in ['wide', 'narrow'].
2. Rank by what it costs to find out: `ranking_by_cost(cost_market=20.0, cost_innovation=1.0)`. Settings offered: `cost_market` in [20.0, 5.0, 2.0]; `cost_innovation` in [1.0, 4.0].
3. One at a time against a joint sample: `joint_sample(draws=20, seed=1)`. Settings offered: `draws` in [5, 20, 60]; `seed` in [1, 2].
4. Endpoints can miss a reversal: `interior_reversal(a_score=0.2, p=0.5)`. Settings offered: `a_score` in [0.2, 0.75]; `p` in [0.0, 0.25, 0.5, 1.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Ranked first Market size; Swing, market size 572.1; Swing, imitation 526.3; Swing, innovation 127.2; Ranges market 700 to 1300, imitation 0.1 to 0.5, innovation 0.005 to 0.02
- Demonstration 2: First by effect Market size; First by effect per cost Innovation; Order reversed yes; Per cost, innovation 127.2; Per cost, imitation 105.3; Per cost, market size 28.6
- Demonstration 3: Draws and seed 20 draws, seed 1; Imitation swing 526.3; Innovation swing 127.2; Lowest sampled 358.3; Highest sampled 998.9; Joint spread 640.6
- Demonstration 4: A score 0.20; B score at the point checked 1.00; Winner at the point checked B wins; B score at p = 0 and p = 1 0.00; Winner at both endpoints A

Copyright Jason Karpeles. All rights reserved.
