# Chapter 13 pack: expressions

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Raised when an expression asks for something the whitelist does not permit | `expressions.py` | `UnsafeExpression` |
| Parse an expression and reject every construct outside the whitelist | `expressions.py` | `parse` |
| Every name an expression reads. The model's dependency edges come from here | `expressions.py` | `variables` |
| Evaluate a whitelisted expression against a supplied set of named values | `expressions.py` | `evaluate` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_13_expressions.code.expressions import UnsafeExpression
```
