# Chapter 37 pack: hiring_pipeline

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| Heads, vacancies, and an experience coflow as three separate stocks, unfitted | `model.py` | `document` |
| The exported artifact: capability over time, not headcount | `model.py` | `effective_capability` |
| Capability over headcount, the number no payroll report carries | `model.py` | `capability_share` |
| The committed JOLTS and CES record as Series objects | `calibrate.py` | `record` |
| Hires minus separations against the change in employment, two surveys, one identity | `calibrate.py` | `identity_gap` |
| The three knobs the fit may move and the ranges searched | `calibrate.py` | `knobs` |
| Hires and quits over the fit window with their tolerances | `calibrate.py` | `targets` |
| The same targets over 2022 to 2024, which the fit never sees | `calibrate.py` | `holdout_targets` |
| Grid fit on the fit window, holdout error recorded in the same object | `calibrate.py` | `fit` |
| The document with fitted values marked inferred | `calibrate.py` | `fitted_document` |
| Model against record at named months | `calibrate.py` | `against_record` |
| Fit error along the ramp axis, refitting the other knobs at each point | `calibrate.py` | `ramp_profile` |
| Chapter 28's four families of findings, then the defect report | `calibrate.py` | `defects` |
| Headcount and capability at month 24 under each hiring rule | `calibrate.py` | `headline` |
| The three hiring rules as Chapter 30 policies | `calibrate.py` | `policies` |
| Chapter 30's compare run per bounded metric, merged, and recommend | `calibrate.py` | `comparison` |
| Which uncertainty moves month 24 capability most | `calibrate.py` | `ranking` |
| Month 20 capability across 200 draws of every uncertainty at once | `calibrate.py` | `envelope` |
| The hire-harder rule pushed to a one-month gap-closing time | `calibrate.py` | `overshoot` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service.

This pack imports the model document (Chapter 20), the runtime (Chapter 22), the critic
(Chapter 28), sensitivity (Chapter 29), policy search (Chapter 30), and calibration (Chapter 35).
It reads `data/bls_jolts/jolts_monthly.csv` and nothing else on disk.

Example:

```python
from chapters.chapter_37_hiring_pipeline.code.calibrate import fit, headline
```
