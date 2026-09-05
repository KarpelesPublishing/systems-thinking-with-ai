# Chapter 4 pack: stock_and_flow

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Return the rate at which the stock changes: inflow minus outflow | `stock.py` | `net_flow` |
| Advance one stock by its net flow over one time step | `stock.py` | `advance_stock` |
| Rebuild the whole path of a stock from its initial level and its flow history | `stock.py` | `integrate` |
| Return how far a path departs from the total net flow that should have produced it | `stock.py` | `conservation_error` |
| Hold a stock at a physical bound. A tank cannot drain past empty | `stock.py` | `apply_floor` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_04_stock_and_flow.code.stock import net_flow
```
