# Chapter 3 pack: reference_modes

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Return the six named reference modes used as behavior targets in this book | `library.py` | `reference_mode_library` |
| Reinforcing growth: the net flow is proportional to the stock itself | `modes.py` | `exponential_growth` |
| Balancing decay toward zero at a rate proportional to what remains | `modes.py` | `exponential_decay` |
| Balancing approach to a goal, closing a fixed fraction of the gap each step | `modes.py` | `goal_seeking` |
| Repeated overshoot and undershoot around a level, with a fixed period | `modes.py` | `oscillation` |
| Reinforcing growth that a fixed carrying capacity progressively limits | `modes.py` | `s_shaped_growth` |
| S-shaped growth against a capacity that the stock itself erodes | `modes.py` | `overshoot_and_collapse` |
| Return `path` with independent Gaussian measurement error, reproducible from `seed` | `observe.py` | `add_observation_noise` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_03_reference_modes.code.library import reference_mode_library
```
