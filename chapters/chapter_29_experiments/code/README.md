# Chapter 29 pack: experiments

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One quantity nobody has pinned down, with the range somebody will defend | `sensitivity.py` | `Uncertainty` |
| Run a model under overrides and return one decision quantity | `sensitivity.py` | `metric` |
| Swing each uncertainty across its range with the others held at midpoint | `sensitivity.py` | `one_at_a_time` |
| Uncertainties ordered by their effect on the decision metric, largest first | `sensitivity.py` | `ranked` |
| Effect on the decision divided by what it would cost to find out. Where to spend | `sensitivity.py` | `value_per_cost` |
| Draw uniformly from every range at once and return the metric for each draw | `sensitivity.py` | `sample` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_20_model_document`, `chapter_22_runtime`.

Example:

```python
from chapters.chapter_29_experiments.code.sensitivity import Uncertainty
```
