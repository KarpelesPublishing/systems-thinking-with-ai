# Unique tool implementations

This directory is the complete AI-visible tool surface for the current release. Each tool has one
implementation module, one catalog entry, and one typed request path through the registry.

| Tool ID | Implementation | Request model | Test surface |
| --- | --- | --- | --- |
| `problem.validate` | `unique/problem_validate.py` | `ProblemContractFileRequest` | `tests/tools/test_problem_evidence_tools.py` |
| `evidence.validate` | `unique/evidence_validate.py` | `ProblemContractFileRequest` | `tests/tools/test_problem_evidence_tools.py` |
| `model.validate` | `unique/model_validate.py` | `ModelFileRequest` | `tests/tools/test_unique_tool_surface.py` |
| `model.compile` | `unique/model_compile.py` | `ModelFileRequest` | `tests/tools/test_unique_tool_surface.py` |
| `policy.validate` | `unique/policy_validate.py` | `PolicyProposalFileRequest` | `tests/tools/test_policy_tool.py` |
| `simulation.run` | `unique/simulation_run.py` | `SimulationRequest` | `tests/tools/test_verification.py` |
| `verification.run` | `unique/verification_run.py` | `SimulationRequest` | `tests/tools/test_verification.py` |

The modules under the parent directory are compatibility imports and registry plumbing. They do
not contain a second implementation. The catalog records each implementation path so an AI or a
human can move from a tool identifier to the source file without searching through YAML.

Direct Python use does not require the registry:

```python
from pathlib import Path

from stai.tools.unique.model_validate import validate_model_file

response = validate_model_file(Path("models/factory-cycle.yaml"))
```

The registry remains useful when an agent needs typed payload validation, case policy enforcement,
write-path controls, and the standard error contract.
