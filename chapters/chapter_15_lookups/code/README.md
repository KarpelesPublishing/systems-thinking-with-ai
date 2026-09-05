# Chapter 15 pack: lookups

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Raised when a lookup is asked about a region no observation covers | `lookup.py` | `OutsideDomain` |
| Piecewise-linear interpolation over observed points, with a closed domain | `lookup.py` | `Lookup` |
| Least-squares polynomial coefficients, lowest order first. Deliberately naive | `lookup.py` | `fit_polynomial` |
| A fit will answer any question asked of it. That is the problem | `lookup.py` | `evaluate_polynomial` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_15_lookups.code.lookup import OutsideDomain
```
