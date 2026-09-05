# Chapter 34 pack: hospital_hybrid

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A patient group with its own share of arrivals and its own service demand | `hospital.py` | `Group` |
| The staffing rule and the scheduling discipline it runs under | `hospital.py` | `StaffingPolicy` |
| Run the coupled system and return outcomes per group, not only in total | `hospital.py` | `run` |
| Worst group's mean wait divided by the best group's. One number, deliberately | `hospital.py` | `equity_gap` |
| Objectives this model must never be optimized against | `hospital.py` | `prohibited_objectives` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_34_hospital_hybrid.code.hospital import Group
```
