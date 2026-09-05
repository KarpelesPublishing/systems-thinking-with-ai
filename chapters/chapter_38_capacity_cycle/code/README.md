# Chapter 38 pack: capacity_cycle

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Capacity as a stock, margins through a lookup, two delays, demand held constant | `model.py` | `document` |
| Utilization once a month from a run, at any step size or solver | `model.py` | `utilization_path` |
| The utilization record, 1990-01 to 2019-12, read from the committed CSV | `calibrate.py` | `record` |
| Dominant period from the autocorrelation of the detrended series | `calibrate.py` | `cycle_period` |
| Peak-to-trough range of the detrended series | `calibrate.py` | `amplitude` |
| The two custom errors the fit scores, period and amplitude, never the path | `calibrate.py` | `period_error`, `amplitude_error` |
| The three knobs: two parameters and the construction delay | `calibrate.py` | `knobs`, `CONSTRUCTION_GRID` |
| The grid search, a minute of runs; and the values it last produced | `calibrate.py` | `fit`, `PINNED_FIT` |
| The document with every fitted value marked inferred | `calibrate.py` | `fitted_document` |
| The 1972 to 1989 window the fit never saw, scored the same way | `calibrate.py` | `holdout_targets`, `holdout_errors` |
| Chapter 28's four checks on the fitted document | `calibrate.py` | `critic_report` |
| Chapter 19's step-size check on the period | `calibrate.py` | `step_refinement` |
| Period and amplitude as the construction delay moves | `calibrate.py` | `construction_delay_sweep` |
| What the model can say about the date of the next trough | `calibrate.py` | `phase_envelope` |
| The fitted rule and three alternatives, with bounds, over uncertainty draws | `calibrate.py` | `policies`, `compare_policies`, `recommendation` |
| Which uncertainty moves steadiness most, Chapter 29's ranking | `calibrate.py` | `sensitivity_ranking` |
| Every number the chapter prints | `calibrate.py` | `summary` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack imports the model document (Chapter 20), the runtime (Chapter 22), the solvers
(Chapter 19), the critic (Chapter 28), sensitivity (Chapter 29), policies (Chapter 30), and
calibration (Chapter 35). It reads `data/fred_capacity/capacity_monthly.csv`.

Example:

```python
from chapters.chapter_38_capacity_cycle.code.calibrate import amplitude, cycle_period, record
```
