# Chapter 16 pack: delays

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| A conveyor. What goes in comes out intact, exactly `length` periods later | `delays.py` | `PipelineDelay` |
| A well-stirred tank. Output is proportional to what is currently held | `delays.py` | `FirstOrderDelay` |
| Feed a series through a pipeline and return what emerges | `delays.py` | `run_pipeline` |
| Feed a series through a first-order delay and return its output | `delays.py` | `run_first_order` |
| First period where the output reaches a fraction of its eventual level | `delays.py` | `time_to_fraction` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_16_delays.code.delays import PipelineDelay
```
