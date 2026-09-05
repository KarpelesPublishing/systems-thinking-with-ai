# Chapter 27 pack: compiler_agent

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One change to one variable, with the reason attached to the change itself | `patch.py` | `Edit` |
| A set of edits proposed against one model version | `patch.py` | `Patch` |
| Produce a new document. Refuses a patch written against a different version | `patch.py` | `apply_patch` |
| What a human sees. Never the prose summary, always the diff and the problems | `patch.py` | `review_packet` |
| Compile the same narrative twice and measure how much the structure moved | `patch.py` | `structural_variance` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_20_model_document`.

Example:

```python
from chapters.chapter_27_compiler_agent.code.patch import Edit
```
