# Chapter 14 pack: dominance

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Adoption driven by outside influence and by contact with existing adopters | `dominance.py` | `Diffusion` |
| The adopter path with both loops live | `dominance.py` | `run` |
| How much each loop's removal changes the rate, at every point on the path | `dominance.py` | `contributions` |
| The loop with the larger contribution at each point | `dominance.py` | `dominant_loop` |
| The step where dominance changes hands. None when it never does | `dominance.py` | `handover_step` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_14_dominance.code.dominance import Diffusion
```
