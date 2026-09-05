# Chapter 25 pack: flight_sim

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A bound the scenario is not permitted to violate, checked after the run | `scenario.py` | `Constraint` |
| Everything needed to replay a scenario and to check what was claimed about it | `scenario.py` | `ScenarioRecord` |
| Runs named scenarios against one model and logs each one | `scenario.py` | `ScenarioRunner` |
| Which variables in a proposed narrative the replay record cannot support | `scenario.py` | `supported_by_record` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_20_model_document`, `chapter_22_runtime`.

Example:

```python
from chapters.chapter_25_flight_sim.code.scenario import Constraint
```
