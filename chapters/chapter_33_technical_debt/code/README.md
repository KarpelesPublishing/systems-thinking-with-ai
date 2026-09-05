# Chapter 33 pack: technical_debt

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Delivery, debt, defects, and morale at one moment | `debt.py` | `State` |
| Capacity, pressure, and the share reserved for repayment | `debt.py` | `Policy` |
| What is left after debt drag and morale. The quantity nobody measures | `debt.py` | `available_capacity` |
| One period: deliver, accrue debt, surface defects, move morale | `debt.py` | `step` |
| Advance the team and return every period's state | `debt.py` | `run` |
| The few numbers a reader should carry out of a run | `debt.py` | `summary` |
| What can be counted, and what has to stay a proxy | `debt.py` | `observable_measures` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_33_technical_debt.code.debt import State
```
