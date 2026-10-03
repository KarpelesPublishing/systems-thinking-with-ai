---
name: st-35-calibration
description: "Design and audit a small calibration with provenance, predeclared fit targets, defensible knobs, separate holdout scores, zero-safe error selection, and identifiability limits using Chapter 35. Runs the chapter's model on the user's own inputs with notebooks/35-calibration.ipynb."
---

# Chapter 35: Fitting Is Not Confirming

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/35-calibration.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/35-calibration/reader.html.

## Method

### Inputs and decision

Obtain the source series and checksum, time and quantity units, model and solver settings, quantities already measurable, candidate parameter ranges, decision-relevant error tolerances, and fit and holdout windows.

### Work the question

1. Freeze the record with provenance and checksum. Check matching time units and sampling dates. The chapter code samples by a rounded time-step index, so use aligned observation dates or document the approximation.
2. Separate measured quantities from hidden candidate knobs. Defend each bound independently of the fit and reserve a holdout before searching. The teaching chapter limits case fits to three knobs; the one-knob-per-three-observations guard is only a size guard.
3. Choose MAE for error in units, RMSE when larger misses deserve weight, or MAPE only after examining zeros and small denominators. This helper drops zero observations and refuses an all-zero record; omitted zeros receive no score.
4. Use shape correlation only when level and scale are judged separately. The helper returns one for a constant path. For cycles, period and amplitude can address phase-insensitive questions, but dated decisions also need phase or prediction error.
5. Run the defended grid and preserve its evaluations, residuals, range and method. Report boundary solutions and profiles; passing a tolerance or the size guard does not identify a parameter.
6. Apply fitted values as inferred with record, method, residual and checksum. Report holdout separately and run relevant criticism on the fitted document. Name at least one rival or omitted mechanism that could also fit.

### Limits to preserve

A holdout pass supports transfer to that window, not causal confirmation. A fitted value is conditional on structure and the search range. Synthetic tank source notes are teaching labels, and their example checksum is not the checksum of an empirical ledger.

### Connected chapters

Use Chapter 11 for evidence labels, Chapter 19 for solver refinement, Chapter 28 for fitted-model criticism, Chapter 29 for screening, and Chapters 36 to 39 for case-specific targets and failure modes.

## Apply it to the user's inputs

1. Open `notebooks/35-calibration.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `class Series`: One observed sequence, with where it came from.
- `class Target`: One model output the fit must reproduce, and how close is close enough.
- `class Knob`: One parameter the fit is allowed to move, and the range somebody will defend.
- `class Fit`: Everything needed to audit a calibration.
- `checksum_of(path: str | Path)`
- `read_series(path: str | Path, time_column: str, value_column: str, *, name: str, unit: str, source: str, time_origin: str | None=None)`: Read one column of a CSV as a Series.
- `months_between(origin: str, when: str)`
- `mape(model: list[float], observed: list[float])`
- `rmse(model: list[float], observed: list[float])`
- `mae(model: list[float], observed: list[float])`
- `shape(model: list[float], observed: list[float])`: One minus the correlation of the two paths. Zero is the same shape at any scale.
- `with_values(document: ModelDocument, values: dict[str, float])`: A copy of the document with the named parameter values replaced. Nothing else moves.
- `sampled(document: ModelDocument, variables: list[str], times: tuple[float, ...], settings: RunSettings | None=None)`: Run the document and read each variable at the requested times.
- `error_of(document: ModelDocument, targets: list[Target], settings: RunSettings | None=None)`: Weighted total error, error per target, and residuals per target, for one document.
- `grid_fit(document: ModelDocument, knobs: list[Knob], targets: list[Target], settings: RunSettings | None=None, refinements: int=2)`: Coarse grid over every knob, then re-grid around the winner.
- `with_fitted(document: ModelDocument, fit: Fit, targets: list[Target])`: The document with fitted values in place, each marked inferred with its provenance.
- `holdout(document: ModelDocument, fit: Fit, targets: list[Target], settings: RunSettings | None=None)`: Error of the fitted document on targets the fit never saw. Record it in the Fit.
- `fit_report(fit: Fit, targets: list[Target])`: A table a chapter can print: parameter, fitted value, range searched, then each target.

Demonstrations in the notebook, with the chapter's settings:

1. Scoring a cycle by point-by-point distance: `cycle_score(shift=0.5, error='rmse')`. Settings offered: `shift` in [0.0, 0.125, 0.25, 0.5]; `error` in ['rmse', 'shape'].
2. How many knobs the record allows, and what they cost: `knob_budget(knobs=2, points=5)`. Settings offered: `knobs` in [1, 2, 3]; `points` in [5, 9].
3. The tank, fitted by a grid: `tank_fit(steps=9, refinements=2)`. Settings offered: `steps` in [3, 5, 9]; `refinements` in [0, 2].
4. The wrong knob passes the window and fails the holdout: `wrong_knob(knob='arrivals', refinements=2)`. Settings offered: `knob` in ['rate', 'arrivals']; `refinements` in [0, 2].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Phase shift (cycles) 0.500; Error function rmse; Shifted model 14.14; Flat line at the mean 7.07
- Demonstration 2: Knobs 2; Observations 5; Points required 6; Outcome refused; Runs at 9 steps and 3 passes 243; Time at one second a run (minutes) 4.05
- Demonstration 3: Steps per pass 9; Refinement passes 2; Model runs 27; Fitted rate 0.069375; Fit-window error (mape) 0.0050; Holdout error (mape) 0.0085; Within the 1 percent tolerance yes
- Demonstration 4: Knob moved arrivals; Fitted arrivals 7.5781; Fit-window error (mape) 0.0089; Holdout error (mape) 0.0291; Passes the fit tolerance (0.01) yes; Passes the holdout tolerance (0.02) no

Copyright Jason Karpeles. All rights reserved.
