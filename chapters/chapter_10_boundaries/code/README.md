# Chapter 10 pack: boundaries

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A population with its own share of arrivals and its own service demand | `stratified.py` | `Group` |
| Mean wait for one undifferentiated population, from queueing approximation | `stratified.py` | `aggregate_wait` |
| Mean wait per group when each group's service demand differs | `stratified.py` | `stratified_waits` |
| The gap the aggregate number conceals: worst group minus best | `stratified.py` | `hidden_spread` |
| The share-weighted mean, which is what the aggregate model reports | `stratified.py` | `population_mean` |
| Name the group that carries the cost. The aggregate model has no such function | `stratified.py` | `worst_served` |
| How many times longer the worst-served group waits than the best-served | `stratified.py` | `spread_ratio` |
| Mean, spread, and worst-served group, reported together | `stratified.py` | `summarize` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_10_boundaries.code.stratified import Group
```
