# Chapter 30 pack: policy_search

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A named set of settings, with an owner and whether it can be undone | `policies.py` | `Policy` |
| A constraint that a policy must satisfy in every draw, not on average | `policies.py` | `Bound` |
| What a policy did across every draw, including where it failed | `policies.py` | `Evaluation` |
| Run one policy against a fixed set of uncertainty draws | `policies.py` | `evaluate` |
| Every policy against the same draws, so the comparison is like for like | `policies.py` | `compare` |
| Rank by worst case among admissible policies, and say what was excluded and why | `policies.py` | `recommend` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_20_model_document`, `chapter_29_experiments`.

Example:

```python
from chapters.chapter_30_policy_search.code.policies import Policy
```
