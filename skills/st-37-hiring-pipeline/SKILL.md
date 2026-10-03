---
name: st-37-hiring-pipeline
description: "Analyze the Chapter 37 hiring pipeline with vacancies, headcount and capability coflow; interpret learning time constants, weak ramp identification, tenure-rate denominators, and constrained hiring policies. Runs the chapter's model on the user's own inputs with notebooks/37-hiring-pipeline.ipynb."
---

# Chapter 37: Hiring Is a Pipeline, Not a Number

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/37-hiring-pipeline.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/37-hiring-pipeline/reader.html.

## Method

### Inputs and decision

Collect vacancy, hire, quit, separation and employment records with consistent intervals; distinguish headcount from capability; obtain initial contribution, learning-curve assumptions, target step, fit windows, and payroll and capability bounds.

### Work the question

1. Reconcile hires minus separations with employment change over matching intervals. JOLTS and CES are different surveys; preserve the observed identity gap instead of forcing their counts to agree.
2. Trace vacancies through the fill delay into headcount, then experience and departures through the coflow. New hires enter at an assumed 0.4 of seasoned contribution; effective capability has no directly observed national counterpart.
3. Treat `ramp_time` as an exponential learning time constant. Specify an operational threshold separately and distinguish the continuous curve from the monthly Euler recurrence.
4. Read the fit and holdout errors alongside the ramp profile. The fit accepts widely different ramps after other parameters refit; a twelve-month winner does not establish a twelve-month workforce fact.
5. Separate the twenty-four-month headline from the twenty-month comparison. In the latter, check payroll ceiling and capability floor on every shared draw from the same run. A policy fixing the ramp overrides the sampled ramp, so retain sampled and effective values.
6. Propose a role-specific cohort measurement of output relative to comparable seasoned workers. For tenure quit rates divide quits by group population or person-time exposed, and test whether leavers carry average capability.

### Limits to preserve

National aggregate fit parameters do not identify a particular employer or role. Faster recruiting is not instantaneous productive capacity. Senior mentoring drag, recruiting limits and labor-market effects are omitted, and the bounds are assumed decision rules rather than empirical permissions.

### Connected chapters

Use Chapter 16 for first-order delays, Chapter 17 for coflows, Chapter 29 for informative cohort studies, Chapter 30 for policy overrides and bounds, and Chapter 35 for parameter profiles.

## Apply it to the user's inputs

1. Open `notebooks/37-hiring-pipeline.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `document(target_step: float=0.0)`: The hiring pipeline with unfitted parameters. `target_step` raises the target at month 0.
- `effective_capability(result)`: The exported artifact: the capability path of a run, in thousand effective persons.
- `capability_share(result)`: Effective capability over headcount, the number no payroll report carries.
- `record()`: Every column of the committed CSV as a Series, time in months since January 2015.
- `record_rows()`
- `identity_gap(start: str='2015-01', end: str='2019-12')`: Cumulative flows after the opening stock against the CES employment change.
- `document(target_step: float=0.0)`
- `knobs()`
- `targets(window: tuple[float, float]=FIT_WINDOW)`
- `holdout_targets()`
- `fit()`: Grid fit on the fit window, then the holdout error recorded in the same Fit.
- `fitted_document(target_step: float=0.0)`: The document with fitted values in place, each marked inferred.
- `fitted_path()`: The fitted document run from January 2015 through December 2024, no scenario.
- `against_record(variable: str, months: tuple[int, ...])`: Model against record for one variable at named months since January 2015.
- `report()`
- `ramp_profile(values: tuple[float, ...]=(2.0, 6.0, 12.0, 18.0))`: Best fit-window error at each ramp value, refitting the other two knobs each time.
- `findings()`
- `defects()`
- `model_identity_residual(months: int=60)`: Headcount change minus cumulative hires less quits and layoffs. Zero by construction.
- `run(target_step: float=TARGET_STEP, months: int=HEADLINE_MONTH, overrides: dict[str, float] | None=None)`
- `policies()`
- `uncertainties()`
- `bounds()`
- `headline()`: Headcount and effective capability at month 24 under each rule, and the record's row.
- `overshoot(gap_closing_time: float=1.0)`: The hire-harder rule pushed to a one-month gap-closing time: boom, freeze, and overshoot.
- `comparison(draws: int=COMPARE_DRAWS, seed: int=SEED)`: Compare capability and enforce the payroll ceiling on the same twenty-month runs.
- `ranking()`: Which uncertainty moves month 24 capability the most, one at a time.
- `envelope(draws: int=DRAWS, seed: int=SEED)`: Month 20 capability under the baseline rule across every uncertainty at once.
- `month20(policy: str)`: Deterministic month 20 capability under one rule at the fitted values.

Demonstrations in the notebook, with the chapter's settings:

1. Heads rise and capability does not: `heads_vs_capability(rule='baseline', step=0.1)`. Settings offered: `rule` in ['baseline', 'hire_harder', 'retain', 'shorten_ramp']; `step` in [0.05, 0.1].
2. Two surveys, one identity: `identity(end='2019-12')`. Settings offered: `end` in ['2016-12', '2017-12', '2018-12', '2019-12'].
3. A fit within tolerance, a holdout outside it: `holdout_miss(series='quits', month=84)`. Settings offered: `series` in ['hires', 'quits']; `month` in [0, 59, 84, 119].
4. Which parameter decides capability: `capability_swing(parameter='ramp_time', hold='midpoint')`. Settings offered: `parameter` in ['ramp_time', 'initial_capability', 'gap_closing_time', 'quit_sensitivity']; `hold` in ['midpoint', 'fitted'].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Rule Baseline; Target step 10 percent; Headcount, month 24 (thousand) 159,721; Effective capability, month 24 (thousand) 129,864; Capability per head 0.813; Hires over 24 months (thousand) 154,441; Capability above baseline (thousand) 0; Record, no push: employment, January 2017 (thousand) 145,628
- Demonstration 2: Window January 2015 to December 2019; Hires less separations (thousand) 11,253; Employment change (thousand) 11,226; Gap (thousand) 27; Gap share of the change (percent) 0.24; Model identity residual (thousand persons) 0.000
- Demonstration 3: Series quits; Month January 2022; Model (thousand) 3,507; Record (thousand) 4,413; Model against record (percent) (-20.5); Fit window error (percent) 3.15; Holdout error (percent) 10.72
- Demonstration 4: Parameter swung ramp_time; Range swung 2.00 to 12.00; Others held at midpoints of their ranges; Capability at month 24, low end (thousand) 153,668; Capability at month 24, high end (thousand) 131,257; Swing (thousand) 22,410

Copyright Jason Karpeles. All rights reserved.
