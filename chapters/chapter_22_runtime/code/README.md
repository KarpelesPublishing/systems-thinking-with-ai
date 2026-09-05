# Chapter 22 pack: runtime

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| The semantics of a run | `runtime.py` | `RunSettings` |
| Everything needed to reproduce and to audit a run | `runtime.py` | `Result` |
| Runs one model document | `runtime.py` | `Runtime` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_13_expressions`, `chapter_15_lookups`, `chapter_20_model_document`,
`chapter_21_compiler`.

Example:

```python
from chapters.chapter_22_runtime.code.runtime import RunSettings
```
