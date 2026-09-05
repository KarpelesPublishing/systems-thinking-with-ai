# Chapter 21 pack: compiler

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| What each variable reads, derived from its equation rather than declared | `compiler.py` | `edges` |
| Edges someone wrote down that the equations do not support, and the reverse | `compiler.py` | `declared_versus_inferred` |
| Tarjan's algorithm. Every group of nodes that can all reach each other | `compiler.py` | `strongly_connected` |
| Cycles with no stateful node, unsupported by this explicit runtime | `compiler.py` | `algebraic_loops` |
| The graph the other way round: what each variable affects, not what it reads | `compiler.py` | `influence` |
| Every feedback loop in the model, enumerated from the equations | `compiler.py` | `feedback_loops` |
| Topological order for everything computed within a step | `compiler.py` | `evaluation_order` |
| Compiler output written to teach rather than to scold | `compiler.py` | `diagnostics` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_08_causal_graph`, `chapter_13_expressions`,
`chapter_20_model_document`.

Example:

```python
from chapters.chapter_21_compiler.code.compiler import edges
```
