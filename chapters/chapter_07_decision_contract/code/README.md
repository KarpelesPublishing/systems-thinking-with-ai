# Chapter 7 pack: decision_contract

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A named variable with the unit it is measured in and how it is known | `contract.py` | `Quantity` |
| What decision this model informs, over what horizon, inside what boundary | `contract.py` | `DecisionContract` |
| Return the parts a contract needs before modeling should start | `contract.py` | `missing_pieces` |
| A contract is ready when nothing on the checklist is missing | `contract.py` | `is_ready` |
| Report names used twice with different units, the commonest framing defect | `contract.py` | `unit_conflicts` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_07_decision_contract.code.contract import Quantity
```
