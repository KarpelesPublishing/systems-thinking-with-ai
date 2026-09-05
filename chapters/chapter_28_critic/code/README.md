# Chapter 28 pack: critic

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| One defect, with the category that says which kind of check found it | `critic.py` | `Finding` |
| The document as Chapter 12's stock-and-flow system | `critic.py` | `as_system` |
| Chapter 12's structural rules, applied to a document through `as_system` | `critic.py` | `conservation_findings` |
| Loops that cannot resolve, and variables nothing reads | `critic.py` | `structural_findings` |
| Unit defects a shallow check can reach | `critic.py` | `dimensional_findings` |
| Run the model from an extreme start and see whether it behaves impossibly | `critic.py` | `extreme_condition_findings` |
| Compare named outputs against recorded values from an accepted run | `critic.py` | `regression_findings` |
| Group findings by category so a human can dispose of them in batches | `critic.py` | `defect_report` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack builds on `chapter_12_stocks_flows`, `chapter_20_model_document`, `chapter_21_compiler`,
`chapter_22_runtime`.

Example:

```python
from chapters.chapter_28_critic.code.critic import Finding
```
