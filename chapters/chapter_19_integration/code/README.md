# Chapter 19 pack: integration

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One Euler step. Assumes the derivative at the start holds across the whole step | `solvers.py` | `euler` |
| Second-order: take an Euler step, then average the slopes at both ends | `solvers.py` | `heun` |
| Fourth-order Runge-Kutta: four slope samples across the step | `solvers.py` | `rk4` |
| Run one state variable to the horizon and return the whole path | `solvers.py` | `integrate` |
| The Bass-like growth used throughout this book, as a derivative | `solvers.py` | `logistic` |
| Update stock A, then compute B's flow from A's NEW value. The bug | `solvers.py` | `sequential_pair` |
| Read both flows from the state at the start of the step, then write both | `solvers.py` | `simultaneous_pair` |
| Endpoint of the same run at successively halved steps | `solvers.py` | `step_refinement` |
| True when halving the step has stopped moving the answer | `solvers.py` | `converged` |
| Hold a state at a physical bound after a step. A tank cannot drain past empty | `solvers.py` | `apply_floor` |
| Add reproducible measurement noise. Two runs with one seed are identical | `solvers.py` | `seeded_noise` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_19_integration.code.solvers import euler
```
