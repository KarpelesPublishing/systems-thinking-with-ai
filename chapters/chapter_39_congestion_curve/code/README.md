# Chapter 39 pack: congestion_curve

Main entry points in this pack, and the idea each one carries.

| Model idea | Python file | Primary function |
| --- | --- | --- |
| The airport as a document: a queue that is a level, a fitted delay curve, and padding | `model.py` | `build_document` |
| The parameters nobody measured. Three, by design | `model.py` | `free_knobs` |
| Every airport-month row of the committed record, as floats | `calibrate.py` | `read_months` |
| Airport-year load bins | `calibrate.py` | `read_hour_bins` |
| Airport-year clock hours | `calibrate.py` | `read_clock_hours` |
| Pool existing load bins across airports using scheduled-departure weights | `calibrate.py` | `pooled_bins` |
| The bins as Chapter 35's Series, with source and checksum | `calibrate.py` | `bins_as_series` |
| A three-knob convex curve fitted to the bins by grid search, scored by MAE | `calibrate.py` | `fit_curve` |
| The exported artifact: the fitted curve on the bin centers, evidence inferred | `calibrate.py` | `fitted_congestion_lookup` |
| The fitted lookup against the other year's bins, refusing loads outside its domain | `calibrate.py` | `holdout_error` |
| Non-decreasing everywhere and convex from the knee upward | `calibrate.py` | `convex_above_knee` |
| Cancellation share against delay across airport-months, least squares | `calibrate.py` | `cancellation_fit` |
| Departure-weighted fit-year facts the model is anchored to | `calibrate.py` | `observed_summary` |
| The document with the fitted curve and observed anchors in place | `calibrate.py` | `fitted_document` |
| no_cap, cap_at_p95, cap_at_p90 as Chapter 30 policies | `calibrate.py` | `policies` |
| Ranges somebody will defend, kept inside the lookup's domain | `calibrate.py` | `uncertainties` |
| Every policy on delay, cancellations, and movements, with bounds that can veto | `calibrate.py` | `policy_table` |
| Chapter 28's four checks on the fitted document, as a defect report | `calibrate.py` | `critic_report` |
| One year at the record's load: how much realized delay padding hides | `calibrate.py` | `padding_run` |
| Everything the chapter prints, in one dict | `calibrate.py` | `run_case` |

Each function is importable on its own. Nothing here requires YAML, a CLI, an LLM,
or an external service. It reads `airport_month_delay.csv`, `airport_hour_load.csv`, and
`airport_clock_hour.csv` under `data/bts_ontime/`, each committed with its checksum.

This pack imports the lookup from Chapter 15, the document from Chapter 20, the runtime from
Chapter 22, the critic from Chapter 28, the uncertainty from Chapter 29, the policies from
Chapter 30, and the Series, Knob, and error functions from Chapter 35.

Example:

```python
from chapters.chapter_39_congestion_curve.code.calibrate import fitted_congestion_lookup
```
