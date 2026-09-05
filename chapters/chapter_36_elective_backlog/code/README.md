# Chapter 36 pack: elective_backlog

Every function this pack exports, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| The waiting list as three stocks, with its levels read from the record at a named month | `model.py` | `build` |
| The level of a monthly flow during the first year of a run, used as its starting value | `model.py` | `first_year_mean` |
| The record as two series: total incomplete pathways and pathways over 52 weeks, in months since April 2016 | `calibrate.py` | `record` |
| The three knobs the fit may move, with the ranges someone will defend | `calibrate.py` | `knobs` |
| The fit targets: total incomplete by MAPE within 0.05, long waiters by shape | `calibrate.py` | `targets` |
| Grid fit on 2016-04 to 2019-12, holdout from 2021-04, both in one Fit | `calibrate.py` | `fit` |
| The document with fitted values marked inferred, stocks reset to any month in the record | `calibrate.py` | `fitted_document` |
| What Chapter 28's critic says about the fitted document | `calibrate.py` | `critic_report` |
| Record, fitted model, and each policy at months 0, 24 and 48 from June 2022 | `calibrate.py` | `headline_table` |
| Chapter 30's comparison with every bound checked on its own metric | `calibrate.py` | `compare_policies` |
| Which of the five uncertainty ranges moves the long-wait stock most | `calibrate.py` | `sensitivity_ranking` |
| Two hundred draws across the five uncertainty ranges, as a low, median, and high | `calibrate.py` | `uncertainty_envelope` |
| The first month a run's list falls to a threshold, or None. The exported artifact | `calibrate.py` | `recovery_date` |
| The number of free knobs, held at three by a test | `calibrate.py` | `knob_guard` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service. The record is `data/nhs_rtt/rtt_national_monthly.csv`; nothing here
touches the network.

This pack imports the model document (Chapter 20), the runtime (Chapter 22), the critic
(Chapter 28), the sensitivity tools (Chapter 29), the policy comparison (Chapter 30), and the
calibration pack (Chapter 35).

Example:

```python
from chapters.chapter_36_elective_backlog.code.calibrate import fit, report
```
