# Chapter 32 pack: service_growth

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Customers, workforce, experience, and quality at one moment | `growth.py` | `State` |
| The growth and hiring settings a run is given | `growth.py` | `Policy` |
| Heads weighted by experience. Chapter 17's dilution, in the growth loop | `growth.py` | `effective_capacity` |
| Customers divided by experience-weighted capacity | `growth.py` | `load` |
| One period. All flows read the state at the start, then all stocks are written | `growth.py` | `step` |
| Advance the business and return every period's state | `growth.py` | `run` |
| The few numbers a reader should carry out of a run | `growth.py` | `summary` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_32_service_growth.code.growth import State
```
