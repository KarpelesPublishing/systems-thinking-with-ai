# Chapter 9 pack: archetypes

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Boundary A: the limit is exogenous. Growth approaches it and stops | `limits.py` | `fixed_limit` |
| Boundary B: the limit is endogenous, consumed by the growth it constrains | `limits.py` | `eroding_limit` |
| True when the path stops moving. The observable that separates the two boundaries | `limits.py` | `settles` |
| True when the path rises to a peak and ends meaningfully below it | `limits.py` | `peaks_then_falls` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_09_archetypes.code.limits import fixed_limit
```
