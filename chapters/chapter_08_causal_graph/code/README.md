# Chapter 8 pack: causal_graph

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One causal claim: source, target, sign, how it is known, and whether it is delayed | `graph.py` | `Link` |
| Every simple cycle in a directed graph, each reported once from its lowest node | `graph.py` | `simple_cycles` |
| Enumerate every simple feedback loop, each reported once from its lowest node | `graph.py` | `find_loops` |
| Reinforcing when the loop holds an even number of negative links, balancing otherwise | `graph.py` | `loop_polarity` |
| Links resting on assumption or proposal rather than observation or inference | `graph.py` | `unsupported_links` |
| Links where nobody recorded whether the effect is immediate or delayed | `graph.py` | `links_without_time_semantics` |
| Summarize what the diagram is resting on | `graph.py` | `audit` |
| Reject non-numeric or non-finite values used by the teaching functions | `validate_number.py` | `validate_number` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack stands alone and imports no other pack.

Example:

```python
from chapters.chapter_08_causal_graph.code.graph import Link
```
