---
name: st-38-capacity-cycle
description: "Interpret or reproduce the Chapter 38 capacity-cycle fit, RK4 period-and-amplitude refinement, construction and perception delays, phase limits, and the comparison with no admissible policy. Runs the chapter's model on the user's own inputs with notebooks/38-capacity-cycle.ipynb."
---

# Chapter 38: Capacity Arrives When the Price Has Gone

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/38-capacity-cycle.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/38-capacity-cycle/reader.html.

## Method

### Inputs and decision

Obtain the frozen utilization record and units, declared fit and holdout windows, detrending and period rule, solver and sample interval, lookup shape, construction delay, and unchanged mean-utilization and amplitude bounds.

### Work the question

1. Trace capacity through completions and retirement, with perception and construction as different delays. A zero new-investment command does not empty construction already in progress; contraction begins only when completions fall below retirements.
2. Check sector and quantity coverage before constructing utilization. The committed capacity index covers total industry while fitted utilization and production are manufacturing; dividing mismatched series cannot reconstruct the target.
3. Establish numerical adequacy for both period and amplitude. Use the half-month RK4 calculation and monthly samples; successive half, quarter and eighth-month checks must satisfy one sampled month and one percent amplitude thresholds.
4. Keep the fit at gain 0.25, sensitivity 2.0 and construction delay eighteen months. Report the grid boundary, 128 evaluated candidates, phase-insensitive targets and separate holdout. Fit scoring uses 360 observations; the displayed path includes the month-360 endpoint.
5. Compare all four rules across the same twelve numbered draws with every bound read from the same run. All rules fail at least one unchanged bound; the utilization trigger fails amplitude at zero-based draw ID 9, the tenth draw. Retain no admissible recommendation.
6. Distinguish internal sufficiency from historical cause, and phase uncertainty from period fit. Name the missing pipeline, perceived-margin, retirement and demand observations needed to test the mechanism.

### Limits to preserve

The period fits ninety months, while the earlier holdout period error is 32.8 percent and fails. Point-estimate damping does not establish robust policy admissibility. A weak autocorrelation return, range-based amplitude and fitted aggregate delay do not identify plant timing or the next trough date.

### Connected chapters

Use Chapter 2 for rival explanations, Chapter 15 for lookup shape, Chapter 16 for delays, Chapter 19 for numerical refinement, Chapter 30 for exclusions, and Chapter 35 for calibration scope.

## Apply it to the user's inputs

1. Open `notebooks/38-capacity-cycle.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `document(construction_delay: float=DEFAULT_CONSTRUCTION_DELAY, perception_delay: float=DEFAULT_PERCEPTION_DELAY, investment_gain: float=DEFAULT_INVESTMENT_GAIN, margin_sensitivity: float=DEFAULT_MARGIN_SENSITIVITY, capital_lifetime: float=DEFAULT_CAPITAL_LIFETIME, demand: float=80.0, horizon: int=360)`: The capacity-cycle document. Delay times are fixed per document; parameters can be fitted.
- `utilization_path(doc: ModelDocument, months: int | None=None, dt: float=1.0, solver: str='euler')`: Utilization sampled once a month from a run of the document.
- `autocorrelation(values: list[float])`: Autocorrelation of the detrended series at lags 0 to half the length.
- `cycle_period(values: list[float])`: Dominant period in months: the first local maximum of the autocorrelation after it first crosses zero. None when the series never returns to positive correlation inside half its length, which is what a flat or a one-way series produces.
- `amplitude(values: list[float])`: Peak-to-trough range of the detrended series, in the series' own unit.
- `period_error(model: list[float], observed: list[float])`: Relative error of the dominant period. A model with no cycle scores the whole record.
- `amplitude_error(model: list[float], observed: list[float])`: Relative error of the peak-to-trough amplitude.
- `record()`
- `holdout_record()`
- `document(construction_delay: float=capacity.DEFAULT_CONSTRUCTION_DELAY)`
- `knobs()`
- `targets()`
- `holdout_targets()`
- `fit()`: Grid over the two parameter knobs inside a loop over the construction delay. Slow.
- `pinned_fit()`: A Fit object at the pinned values, scored on the fit window, without searching.
- `fitted_construction_delay()`
- `fitted_document()`: The document at the pinned fitted values, every fitted quantity marked inferred.
- `holdout_errors()`: The fitted document against 1972 to 1989, which the fit never saw.
- `report()`
- `model_path(doc: ModelDocument | None=None, dt: float=0.5, solver: str='rk4')`: Monthly utilization from the fitted document, or from the one given.
- `critic_report()`
- `endogenous_check()`: Demand is constant already; this states it and reads the swing off the run.
- `step_refinement(tolerance_months: float=1.0, amplitude_relative_tolerance: float=0.01)`: Check period and amplitude at half, quarter and eighth-month RK4 steps.
- `construction_delay_sweep(delays: tuple[float, ...]=(12.0, 18.0, 24.0, 30.0, 36.0, 48.0))`: Period and amplitude as the construction delay moves, other fitted values held.
- `phase_envelope(starts: tuple[float, ...]=(70.0, 74.0, 78.0, 82.0, 86.0), months: int=240)`: Run the fitted document from several starting utilizations and read the spread.
- `first_trough(path: list[float], window: int=12)`: Month of the first point lower than every point within `window` months either side.
- `policies()`: The rule in the record, and three rules somebody might swap it for.
- `uncertainties()`
- `bounds()`
- `policy_statistics()`: Each policy at the fitted values with no draws: period, amplitude, mean utilization.
- `compare_policies(draws: int=12, seed: int=7)`: Chapter 30's comparison, run here so the horizon and the bounds can be stated.
- `recommendation(draws: int=12, seed: int=7)`
- `sensitivity_ranking()`: Chapter 29: which uncertainty moves steadiness most, one at a time, over thirty years.
- `summary()`: Every number the chapter prints, in one place.

Demonstrations in the notebook, with the chapter's settings:

1. Period and amplitude, not the path: `score_statistics(window='fit', series='record')`. Settings offered: `window` in ['fit', 'holdout']; `series` in ['record', 'model'].
2. Sensible at every step, and still a cycle: `rule_cycle(rule='build_when_margins_good', demand=80.0)`. Settings offered: `rule` in ['build_when_margins_good', 'utilisation_trigger', 'smoothed_margin_trigger', 'fixed_replacement']; `demand` in [80.0, 84.0].
3. The construction delay carries the period: `delay_sets_period(delay=18.0, gain=0.25)`. Settings offered: `delay` in [12.0, 18.0, 30.0, 48.0]; `gain` in [0.15, 0.25].
4. A period is not a date: `phase_start(start=78.0, view='alone')`. Settings offered: `start` in [70.0, 78.0, 86.0]; `view` in ['alone', 'all five'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Window 1990 to 2019; Series record; Dominant period 90 months; Amplitude (points) 17.96; Mean utilization (points) 77.5
- Demonstration 2: Rule Build when margins are good (fitted); Demand (held constant) 80; Period 90 months; Amplitude (points) 17.5; Mean utilization 71.8; Highest and lowest 81.1 and 64.2; Mean bound (at least 74) breaks; Amplitude bound (at most 17.96) meets
- Demonstration 3: Construction delay 18 months; Investment gain 0.25; Model period 90 months; Model amplitude (points) 17.5; Record period 90 months
- Demonstration 4: Start utilization 78; Starting capacity (index) 102.6; First trough (month) 20

Copyright Jason Karpeles. All rights reserved.
