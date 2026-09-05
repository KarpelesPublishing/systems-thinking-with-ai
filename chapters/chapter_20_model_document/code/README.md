# Chapter 20 pack: model_document

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One named quantity, with everything needed to place it in the model | `document.py` | `Variable` |
| The whole model, as data. Nothing here executes | `document.py` | `ModelDocument` |
| Every problem findable without running anything | `document.py` | `validate` |
| What changed between two versions, in the model's own terms | `document.py` | `diff` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_20_model_document.code.document import Variable
```
