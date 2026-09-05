# Chapter 24 pack: interop

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Three strengths of interoperability claim, kept separate on purpose | `interchange.py` | `Claim` |
| Emit only what a generic interchange format can hold | `interchange.py` | `export` |
| What an export drops. Reported per variable so a reviewer can weigh it | `interchange.py` | `semantic_loss` |
| Rebuild a document from an exported payload. Everything local comes back empty | `interchange.py` | `import_document` |
| Export, import, and say precisely what changed | `interchange.py` | `round_trip_report` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_20_model_document`.

Example:

```python
from chapters.chapter_24_interop.code.interchange import Claim
```
