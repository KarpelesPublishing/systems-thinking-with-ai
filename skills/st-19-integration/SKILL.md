---
name: st-19-integration
description: "Teach or diagnose numerical integration, Euler artifacts, solver discrepancies, simultaneous updates, and step refinement in Chapter 19; use before interpreting a simulated oscillation. Runs the chapter's model on the user's own inputs with notebooks/19-integration.ipynb."
---

# Chapter 19: Numerical Integration Is Part of the Model

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/19-integration.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/19-integration/reader.html.

## Method

### Inputs and workflow

Obtain equations, initial conditions, physical horizon, solver, time step, update order, random seeds, discontinuity treatment, expected invariants, and decision-metric tolerances.

1. Reproduce a minimal discrepancy with the same physical model. Compare seeds, time steps, transfer bookkeeping, solver, and only then equations. Do not alter a substantive parameter to hide a numerical artifact.
2. Compute all stock transfers from the intended shared state or shared transfer amount. Use closed-total invariants to detect inconsistent recomputation after a stock has changed.
3. Run at dt, dt/2, and dt/4 over the same horizon. Compare the whole trajectory, invariant violations, extrema, and decision metrics as well as endpoints against declared tolerances.
4. Classify remaining trouble as approximation error, an event-placement issue, or fast and slow timescale separation. Record the accepted step and actual results, or keep the behavior numerically unresolved. A smooth plot is not an acceptance test.

### Limits and handoffs

The converged helper compares only the final two endpoints. That result does not validate the coarsest run or intermediate path. The integration code offers Euler, Heun, and RK4; the document runtime in Chapter 22 supports Euler and RK4. Bounds, conservation, and external validity are different checks.

Use Chapter 16 for delay units, Chapter 18 for coupling timescales, Chapter 22 for runtime semantics, and Chapter 38 for a cycle whose fit required refinement.

## Apply it to the user's inputs

1. Open `notebooks/19-integration.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `euler(derivative: Callable[[float, float], float], state: float, t: float, dt: float)`: One Euler step. Assumes the derivative at the start holds across the whole step.
- `heun(derivative: Callable[[float, float], float], state: float, t: float, dt: float)`: Second-order: take an Euler step, then average the slopes at both ends.
- `rk4(derivative: Callable[[float, float], float], state: float, t: float, dt: float)`: Fourth-order Runge-Kutta: four slope samples across the step.
- `integrate(derivative: Callable[[float, float], float], initial: float, dt: float, horizon: float, solver: str='euler')`: Run one state variable to the horizon and return the whole path.
- `logistic(rate: float, capacity: float)`: The Bass-like growth used throughout this book, as a derivative.
- `sequential_pair(a: float, b: float, dt: float, k: float)`: Update stock A, then compute B's flow from A's NEW value. The bug.
- `simultaneous_pair(a: float, b: float, dt: float, k: float)`: Read both flows from the state at the start of the step, then write both.
- `step_refinement(derivative: Callable[[float, float], float], initial: float, horizon: float, solver: str, steps: tuple[float, ...]=(1.0, 0.5, 0.25))`: Endpoint of the same run at successively halved steps.
- `converged(endpoints: list[float], tolerance: float)`: True when halving the step has stopped moving the answer.
- `apply_floor(state: float, floor: float=0.0)`: Hold a state at a physical bound after a step. A tank cannot drain past empty.
- `seeded_noise(values: list[float], sd: float, seed: int)`: Add reproducible measurement noise. Two runs with one seed are identical.

Demonstrations in the notebook, with the chapter's settings:

1. Three answers from one model: `three_solvers(solver='euler', dt=1.0)`. Settings offered: `solver` in ['euler', 'heun', 'rk4']; `dt` in [1.0, 0.0625].
2. What Euler assumes about the rate: `euler_assumption(dt=1.0, rate=2.6)`. Settings offered: `dt` in [1.0, 0.5, 0.25]; `rate` in [1.5, 2.6].
3. Sequential update is a different model: `update_order(k=0.3, order='simultaneous')`. Settings offered: `k` in [0.1, 0.3, 0.5]; `order` in ['simultaneous', 'sequential'].
4. The refinement test: `refinement(case='euler', tolerance=0.1)`. Settings offered: `case` in ['euler', 'heun', 'rk4', 'moving']; `tolerance` in [0.1, 25.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Solver Euler; Step 1.0000; Final value 113.40; Highest value reached 123.35; Final value minus capacity 13.40
- Demonstration 2: Growth rate 2.6; Step 1.00; Rate used for the first step 2.574; Euler value after one step 3.5740; Exact value at that time 11.9716; Highest Euler value 123.35; Final Euler value 113.40
- Demonstration 3: Update rule simultaneous; Stock A after one step 70.0; Stock B after one step 30.0; Total after one step 100.0; Quantity created or lost 0.0
- Demonstration 4: Runs Euler endpoints at steps 1, 0.5, 0.25; First gap 13.40; Last gap 0.00; Tolerance 0.10; Verdict converged

Copyright Jason Karpeles. All rights reserved.
