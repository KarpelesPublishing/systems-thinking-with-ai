---
name: st-36-elective-backlog
description: "Interpret or adapt the Chapter 36 elective-backlog case: pathway stock balances, long-waiter aging, residual removals, conditional recovery dates, and a fit that fails its later holdout. Runs the chapter's model on the user's own inputs with notebooks/36-elective-backlog.ipynb."
---

# Chapter 36: Elective Backlogs as a Stock

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/36-elective-backlog.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/36-elective-backlog/reader.html.

## Method

### Inputs and decision

Obtain monthly incomplete pathways, the aged band, referrals, completions and other departures, definitions and checksum, the fit and holdout windows, and the decision about total list versus long waits.

### Work the question

1. Reconcile stock change with all flows over matching intervals. Count administrative pathways rather than silently substituting unique patients. Split completions from residual removals before attributing validation effects.
2. Preserve waiting list and long-waiter stocks separately. An internal aging transfer cancels in the total but changes who waits; capacity assigned to new referrals is different from FIFO treatment of oldest cases.
3. Keep the committed fit window April 2016 to December 2019 and holdout April 2021 to June 2026 explicit. Report total MAPE 3.63 percent versus 35.57 percent beside the targets and tolerances. Tail steepness at 4.5 is a boundary solution.
4. Dispose of the critic's capacity-without-outflow finding as the retained structural limitation it is, and identify reporting outputs separately. The fitted capacity can only grow, which does not describe the activity collapse.
5. Compare policies with all three declared bounds and shared draws on the same twenty-month runs. Distinguish those from headline month-24 and month-48 projections and from the 200-draw envelope. Keep sampled ranges distinct from confidence intervals.
6. Return the balance diagnosis, tail-allocation question, failed holdout, conditional policy table, and prioritized measurements of treatment order and removal composition. A recovery date is a property of the run; `None` means no crossing within its horizon. The helper converts the crossing time to a month with Python `round`, which rounds halves to even, so a date can land one month before the list is actually under the threshold (for example `longest_first` at 6,000,000 reports 2023-02 while month 8 is still above it); confirm any date against the monthly path.

### Limits to preserve

The model counts pathways, not clinical benefit, and administrative removals may include people lost to care. Its narrow parameter envelope excludes structural error exposed by the holdout. The comparison is teaching output, not advice about prioritizing named patients.

### Connected chapters

Use Chapters 4 and 12 for balances, Chapter 17 for aging, Chapter 30 for all-metric bounds, Chapter 35 for fit and holdout, and Chapter 34 for subgroup consequences.

## Apply it to the user's inputs

1. Open `notebooks/36-elective-backlog.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `read_record(path: Path=RECORD)`
- `month_index(rows: list[dict[str, str]], period: str)`
- `first_year_mean(rows: list[dict[str, str]], column: str, period: str, months: int=12)`: Mean of a column over the `months` rows starting at `period` inclusive.
- `window_mean(rows: list[dict[str, str]], column: str, start: str, end: str)`: Mean of a column over the rows from `start` to `end` inclusive. A record fact, not a fit.
- `window_ratio(rows: list[dict[str, str]], numerator: str, denominator: str, start: str, end: str)`: Mean of one column divided by the mean of another over the same months.
- `build(start: str='2016-04', *, horizon: int=45, rows: list[dict[str, str]] | None=None, validation_rate: float=0.06, system_growth: float=0.002, tail_steepness: float=1.75, long_share: float=0.05)`: The model with its stocks set from the record at `start`.
- `free_knob_count(document: ModelDocument)`: How many parameters carry no observed value and no assumed note: the knobs a fit may move.
- `record()`: The two series the fit and the holdout read, in months since April 2016.
- `last_period()`
- `document(start: str=FIT_START)`: The unfitted model, stocks set from the record at `start`, run to the end of the record.
- `knobs()`
- `targets()`
- `holdout_targets()`
- `settings(horizon: float)`
- `fit()`: Grid fit on 2016-04 to 2019-12, then the holdout from 2021-04, recorded in the Fit.
- `fitted_document(start: str=FIT_START)`: The model with fitted values in place, marked inferred, stocks from the record at start.
- `report()`
- `critic_report(doc: ModelDocument | None=None)`: What Chapter 28's critic says about the fitted document.
- `run(doc: ModelDocument, horizon: float)`
- `at_month(result: Result, name: str, month: float)`
- `record_at(period: str)`
- `period_after(start: str, months: int)`
- `recovery_date(result: Result, threshold: float, variable: str='total_incomplete', start: str=POLICY_START)`: The first month at which `variable` is at or below `threshold`, or None if never.
- `policy_document()`: The fitted structure with stocks and referrals reset to the record at POLICY_START.
- `baseline_policy()`
- `with_policy(doc: ModelDocument, policy: Policy)`
- `headline_table(months: tuple[int, ...]=(0, 24, 48))`: Record, fitted model, and each policy from POLICY_START at the named months.
- `long_waiter_table(months: tuple[int, ...]=(0, 24, 48))`: The same table for the over-52-week stock.
- `class PolicyComparison`: Chapter 30's evaluations on the objective, with every bound checked on its own metric.
- `compare_policies(draws: int=40, seed: int=7)`: Every policy against shared draws, with all bounds checked on each run.
- `sensitivity_ranking(metric: str='long_waiters')`: Which uncertainty moves the long-wait stock most at Chapter 30's horizon.
- `uncertainty_envelope(draws: int=200, seed: int=11, metric: str='total_incomplete')`: Two hundred draws across the five uncertainty ranges, as low, median, and high.
- `knob_guard(doc: ModelDocument | None=None)`: The number of free knobs in the document; the chapter's rule is at most three.
- `evidence_summary(doc: ModelDocument | None=None)`

Demonstrations in the notebook, with the chapter's settings:

1. A gap held open is the growth: `gap_times_months(months=44, gap_scale=1.0)`. Settings offered: `months` in [24, 44]; `gap_scale` in [0.5, 1.0, 2.0].
2. A fit that passes and a holdout that fails: `fit_and_holdout(validation_rate=0.06, system_growth=0.004)`. Settings offered: `validation_rate` in [0.04, 0.06, 0.08]; `system_growth` in [0.0, 0.004].
3. Which parameter decides the long-wait stock: `tail_swing(parameter='long_share', hold='midpoint')`. Settings offered: `parameter` in ['long_share', 'tail_steepness', 'complexity_penalty', 'suppression_strength']; `hold` in ['midpoint', 'fitted'].
4. A recovery date, or the honest None: `recovery(policy='baseline', threshold=6000000.0)`. Settings offered: `policy` in ['baseline', 'uniform_uplift', 'longest_first', 'validation_push']; `threshold` in [6000000.0, 4000000.0].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Gap per month in the record 18,439 pathways; Gap used in this state 18,439 pathways (x 1.0); Months the gap is held open 44; Change in the list 811,305; List after those months (constructed) 4,414,911; List in the record at that month 4,414,911; Constructed minus record 0; Referrals, first year to third (percent) 7.5; Completions, first year to third (percent) 5.6
- Demonstration 2: Validation rate (per month) 0.06; System growth (per month) 0.004; Fit window error (percent) 3.63; Against the 5 percent tolerance inside; Holdout error (percent) 35.57; Model, December 2019 4,206,670; Model, June 2026 4,676,007
- Demonstration 3: Parameter swung long_share; Range swung 0.020 to 0.150; Others held at midpoints of their ranges; Long waiters at month 20, low end 142,700; Long waiters at month 20, high end 16,339; Swing (pathways) 126,362
- Demonstration 4: Policy baseline; Threshold 6,000,000; First month at or under it 2023-04; List at month 0 6,760,060; Lowest list in 48 months 5,340,226

Copyright Jason Karpeles. All rights reserved.
