# Chapter 11 pack: evidence

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Where a claim came from and when it was true | `bundle.py` | `Source` |
| What a claim used to say, and why it stopped saying it | `bundle.py` | `Revision` |
| One causal assertion with its unit, its provenance, and its falsifier | `bundle.py` | `Claim` |
| Return every reason this claim is not yet usable as evidence | `bundle.py` | `validate` |
| Validate every claim and report the problems by statement | `bundle.py` | `validate_bundle` |
| Find pairs where one claim names another as contradicting it | `bundle.py` | `contradictions` |
| The count at each evidence level. One claim has a level; a bundle has this profile | `bundle.py` | `confidence_profile` |
| Claims whose newest source is older than the allowed age | `bundle.py` | `stale` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_11_evidence.code.bundle import Source
```
