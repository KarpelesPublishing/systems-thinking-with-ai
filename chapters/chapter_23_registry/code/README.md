# Chapter 23 pack: registry

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One callable, with everything a reviewer needs to judge it | `registry.py` | `ApprovedFunction` |
| The set of functions a model is permitted to call, with a version of its own | `registry.py` | `Registry` |
| Evaluate an expression against this registry rather than the default table | `registry.py` | `evaluate_with` |
| The registry as the table Chapter 13's evaluator calls | `registry.py` | `callable_table` |
| The functions this book's models are permitted to use | `registry.py` | `standard_registry` |
| What a human has to settle before a proposed function is approved | `registry.py` | `review_request` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_13_expressions`.

Example:

```python
from chapters.chapter_23_registry.code.registry import ApprovedFunction
```
