---
name: st-15-lookups
description: "Teach or check nonlinear lookup curves, interpolation bounds, extrapolation refusals, and shape sensitivity in Chapter 15; use when a fitted function claims more than its observed domain supports. Runs the chapter's model on the user's own inputs with notebooks/15-lookups.ipynb."
---

# Chapter 15: Nonlinearity and Lookup Functions

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/15-lookups.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/15-lookups/reader.html.

## Method

### Inputs and workflow

Collect paired input and output values with units, evidence status, domain, date or regime, physical bounds, intended direction, and the decision region. Distinguish measured points from illustrative or assumed ones.

1. Name the relevant shape and mechanism: saturation, threshold, congestion, diminishing marginal gain, or network effect. Shapes may overlap; a static network curve becomes feedback only when a return path exists.
2. State the supported input domain before fitting. Check duplicate inputs, bounds, and the intended direction explicitly; is_monotonic accepts decreasing curves too.
3. Interpolate inside the domain. For a requested value outside it, identify the missing evidence and offer a declared assumption, new measurement, or restricted question. Do not quietly extend the polynomial or clamp an input.
4. Compare alternative shapes with shared endpoints when the policy depends on the shoulder or threshold. Return the lookup record: points, units, domain, interpolation rule, shape constraints, evidence, and review trigger.

### Limits and handoffs

A bounded lookup is not proof that its observations or mechanism are correct. Saturation and diminishing returns are not exclusive classes. A chord beneath a concave curve understates the interior level, while its slope can understate or overstate marginal gain depending on location.

Use Chapter 11 for evidence and staleness, Chapter 10 for the domain boundary, Chapter 14 for changing loop strength, and Chapter 39 for a congestion application.

## Apply it to the user's inputs

1. Open `notebooks/15-lookups.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class OutsideDomain`: Raised when a lookup is asked about a region no observation covers.
- `class Lookup`: Piecewise-linear interpolation over observed points, with a closed domain.
- `fit_polynomial(points: list[tuple[float, float]], degree: int)`: Least-squares polynomial coefficients, lowest order first. Deliberately naive.
- `evaluate_polynomial(coefficients: list[float], x: float)`: A fit will answer any question asked of it. That is the problem.

Demonstrations in the notebook, with the chapter's settings:

1. Inside the data, a lookup and a fit agree: `inside_the_data(load=2.5, degree=5)`. Settings offered: `load` in [1.5, 2.5, 3.5, 4.5]; `degree` in [2, 5].
2. Outside the data, the fit answers and the lookup refuses: `outside_the_data(asked=12.0, degree=5)`. Settings offered: `asked` in [5.0, 6.0, 8.0, 12.0]; `degree` in [3, 5].
3. Monotonic and bounded are claims, so test them: `claims_as_tests(second_value=0.6, last_value=0.93)`. Settings offered: `second_value` in [0.6, 0.8]; `last_value` in [0.85, 0.88, 0.93, 1.04].
4. Does the conclusion survive a change of shape?: `shape_test(shape='curve', load=3.0)`. Settings offered: `shape` in ['line', 'curve', 'threshold']; `load` in [3.0, 4.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Lookup reading 0.690; Fit reading 0.699; Fit minus lookup 0.009
- Demonstration 2: Load asked 12.0; Lookup refuses (OutsideDomain); Fit 47.76; Fit within 0 to 1 no
- Demonstration 3: Monotonic True; Bounded between 0 and 1 True; Smallest step 0.05; Largest value 0.93
- Demonstration 4: Shape chosen Gentle curve; Reading at this load 0.780; Meets 0.60 yes; Shapes that meet 0.60 1 of 3; Do the three shapes agree no

Copyright Jason Karpeles. All rights reserved.
