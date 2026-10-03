---
name: st-16-delays
description: "Teach or audit material and information delays, pipeline versus first-order responses, time-unit conversion, and the delay inside a feedback loop in Chapter 16. Runs the chapter's model on the user's own inputs with notebooks/16-delays.ipynb."
---

# Chapter 16: Material and Information Delays

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/16-delays.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/16-delays/reader.html.

## Method

### Inputs and workflow

Obtain what enters and leaves, whether identity and ordering survive transit, the delay distribution or evidence, physical time units, time step, initial contents, and any feedback path containing the delay.

1. Classify material versus information by what is held, then pipeline versus mixing by whether items entering together leave together. An information signal can carry dynamic state without belonging in material inventory.
2. Write the accounting boundary for material in transit. For a pipeline, convert physical length into steps; for a first-order delay, retain a mean in physical time units and its initial level.
3. Compare step or pulse responses at equal physical mean. Report onset and time to a stated fraction separately from mean residence; a time constant is not a completion deadline.
4. Test time-step refinement without changing physical delay length. For an oscillation claim, also record correction strength, delay form, and position in the loop. Return a delay ledger and a targeted measurement or refinement plan.

### Limits and handoffs

The pipeline helper length counts steps. The first-order helper is an Euler tank; a step as long as its mean changes the response substantially. Long delay alone does not prove persistent oscillation. An initial sample of twenty transit times cannot guarantee identification of a delay family.

Use Chapter 5 for outstanding orders, Chapter 17 when composition matters during transit, Chapter 19 for solver refinement, and Chapter 37 for hiring and ramp-up distinctions.

## Apply it to the user's inputs

1. Open `notebooks/16-delays.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `validate_number(value: float, name: str)`: Reject non-numeric or non-finite values used by the teaching functions.
- `class PipelineDelay`: A conveyor. What goes in comes out intact, exactly `length` periods later.
- `class FirstOrderDelay`: A well-stirred tank. Output is proportional to what is currently held.
- `run_pipeline(inflows: list[float], length: int, initial: float=0.0)`: Feed a series through a pipeline and return what emerges.
- `run_first_order(inflows: list[float], mean: float, initial_rate: float=0.0)`: Feed a series through a first-order delay and return its output.
- `time_to_fraction(outflows: list[float], target: float, fraction: float)`: First period where the output reaches a fraction of its eventual level.

Demonstrations in the notebook, with the chapter's settings:

1. The conveyor and the tank: `conveyor_and_tank(delay=4, height=10.0)`. Settings offered: `delay` in [2, 4, 6, 8]; `height` in [10.0, 20.0].
2. Chaining tanks walks toward the conveyor: `chained_stages(stages=1, total_mean=4.0)`. Settings offered: `stages` in [1, 2, 4, 8]; `total_mean` in [4.0, 8.0].
3. A tank stepped at its own mean is a conveyor: `step_size(dt=4.0, mean=4.0)`. Settings offered: `dt` in [4.0, 2.0, 1.0, 0.5]; `mean` in [4.0, 8.0].
4. The same delay inside a correction loop: `inside_the_loop(delay=2, gain=0.25)`. Settings offered: `delay` in [1, 2, 4]; `gain` in [0.1, 0.25].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Pipeline at period 5 0.00; Tank at period 5 4.38; Pipeline at period 7 10.00; Tank at period 7 6.84; Period pipeline completes 7; Period tank first reaches 95 percent 14
- Demonstration 2: Stages 1; Mean of each stage 4.00; Output 1 time unit after the step 2.24; Time after the step to reach 95 percent 11.9; Conveyor reaches 95 percent after 4.0
- Demonstration 3: Share of the tank released per step (dt / mean) 1.000; First reading after the first update 10.000; Outflow at time 8 10.000; Outflow at time 8, very small step 8.664; Error at time 8 1.336
- Demonstration 4: First correction 25.0; Pipeline peak 114.1; Tank peak 112.9; Pipeline after 24 periods 100.2; Tank after 24 periods 100.0

Copyright Jason Karpeles. All rights reserved.
