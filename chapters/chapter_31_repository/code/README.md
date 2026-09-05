# Chapter 31 pack: repository

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One attempted action, named at the stage it belongs to | `permissions.py` | `Request` |
| A refusal, recorded so that attempts are visible rather than only blocked | `permissions.py` | `Denial` |
| Allow or deny one request, and say which rule decided | `permissions.py` | `check` |
| Split a batch into what proceeds and what is refused | `permissions.py` | `gate` |
| The order local checks run in, cheapest and most-specific first | `permissions.py` | `ci_sequence` |
| Report the first failing stage. Later stages are not evidence if an earlier one failed | `permissions.py` | `run_ci` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_31_repository.code.permissions import Request
```
