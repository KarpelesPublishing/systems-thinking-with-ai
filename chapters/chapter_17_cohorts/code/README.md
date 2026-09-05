# Chapter 17 pack: cohorts

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One tenure band: how many people, and how much experience they hold between them | `cohorts.py` | `Band` |
| Move people and their experience one step along the chain | `cohorts.py` | `advance` |
| People across every band, which conservation must preserve | `cohorts.py` | `headcount` |
| Person-years across every band, the coflow's total | `cohorts.py` | `total_experience` |
| Experience per person, the ratio that moves without jumping | `cohorts.py` | `average_experience` |
| Capacity counted in experience-weighted people, not in heads | `cohorts.py` | `effective_capacity` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_17_cohorts.code.cohorts import Band
```
