# Chapter 6 pack: two_sketches

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Advance the number waiting. Service is capped by capacity and by who is present | `aggregate.py` | `advance_queue` |
| Return the number waiting at the end of each period | `aggregate.py` | `run_aggregate` |
| Little's law, applied to the averages: mean queue divided by throughput | `aggregate.py` | `mean_wait` |
| Serve arriving patients first-come-first-served and return every individual wait | `queueing.py` | `run_queue` |
| Return the wait that the given percentage of patients came in under | `queueing.py` | `wait_percentile` |
| Mean, median, and tail. The aggregate sketch can only produce the first | `queueing.py` | `wait_summary` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_06_two_sketches.code.aggregate import advance_queue
```
