# Atomic functions

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Stock balance | `advance_stock.py` | `advance_stock` |
| Target inventory | `desired_inventory.py` | `desired_inventory` |
| Inventory discrepancy | `inventory_gap.py` | `inventory_gap` |
| Production starts | `start_production.py` | `start_production` |
| Production completion | `complete_production.py` | `complete_production` |
| Shipments | `ship_orders.py` | `ship_orders` |
| One assembled step | `advance_factory_cycle.py` | `advance_factory_cycle` |
| Repeated direct run | `run_factory_cycle.py` | `run_factory_cycle` |

Each equation file has one primary operation. The composition files import those operations
explicitly. Nothing in this folder requires YAML, the tool registry, an LLM, or an external service.

Example:

```python
from chapters.chapter_02_factory_cycle.code.desired_inventory import desired_inventory

target = desired_inventory(order_rate=10.0, coverage=2.0)
```
