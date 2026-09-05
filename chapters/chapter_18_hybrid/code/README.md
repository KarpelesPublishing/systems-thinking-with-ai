# Chapter 18 pack: hybrid

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| What crosses the boundary, in which direction, and in what unit | `coupling.py` | `Interface` |
| Staff level closes part of the gap to a target derived from observed waiting | `coupling.py` | `AggregateStaffing` |
| Individual patients, first come first served, by however many servers exist | `coupling.py` | `PatientQueue` |
| Run both models, exchanging only what the interface permits | `coupling.py` | `run_coupled` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_18_hybrid.code.coupling import Interface
```
