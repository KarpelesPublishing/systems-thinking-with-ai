# Chapter 5 pack: beer_game

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Peak-to-trough range of a series | `amplification.py` | `swing` |
| Return the stage's order swing divided by the customer's | `amplification.py` | `amplification_ratio` |
| Standard deviation of each stage's order stream, retailer first | `amplification.py` | `stage_variability` |
| Ship what is asked for, or everything on hand. What is missed becomes backlog | `chain.py` | `ship` |
| Advance every stage by one week and return the new state plus the orders placed | `chain.py` | `step_chain` |
| Run the chain over a demand history and return every stage's weekly record | `chain.py` | `run_chain` |
| One link in the chain: what it holds, what it owes, and what is in transit to it | `models.py` | `Stage` |
| One policy, applied identically at every stage | `models.py` | `ChainParameters` |
| Update a stage's belief about demand by closing part of the gap to what it just saw | `policy.py` | `smooth_demand` |
| Replace expected demand, correct the inventory gap, and discount the supply line | `policy.py` | `order_quantity` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_05_beer_game.code.amplification import swing
```
