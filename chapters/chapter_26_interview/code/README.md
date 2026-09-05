# Chapter 26 pack: interview

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One part of the interview, accepted or not by a human | `interview.py` | `Section` |
| A transcript with a question budget and a human gate per section | `interview.py` | `Interview` |
| Convert an accepted interview into Chapter 7's contract. Refuses if unaccepted | `interview.py` | `to_contract` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_07_decision_contract`.

Example:

```python
from chapters.chapter_26_interview.code.interview import Section
```
