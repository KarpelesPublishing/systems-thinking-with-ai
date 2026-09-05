# Chapter 12 pack: stocks_flows

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A rate moving a quantity from one endpoint to another | `system.py` | `Flow` |
| A set of named stocks and the flows that move quantities between them | `system.py` | `System` |
| Everything currently held inside the boundary | `system.py` | `total_in_system` |
| What entered from sources minus what left to sinks, against the change in total | `system.py` | `conservation_residual` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_12_stocks_flows.code.system import Flow
```
