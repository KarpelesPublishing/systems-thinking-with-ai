---
name: st-39-congestion-curve
description: "Audit the Chapter 39 airport congestion lookup and schedule-cap comparison, separating taxi-out from schedule lateness, preserving load domain, pooled weighting, explicit departure units, and twenty-one failed no-cap draws. Runs the chapter's model on the user's own inputs with notebooks/39-congestion-curve.ipynb."
---

# Chapter 39: Delay Is a Curve, Not a Line

From *Systems Thinking with AI* by Jason Karpeles. The chapter notebook is `notebooks/39-congestion-curve.ipynb` in this repository: it defines the chapter's model code in full and reruns every demonstration. The interactive version is at https://karpeles.com/companions/systems-thinking-with-ai/39-congestion-curve/reader.html.

## Method

### Inputs and decision

Identify resource and time cell, physical queue-time measure versus target lateness, scheduled and reported-flight denominators, capacity proxy, bin counts, curve domain, holdout year, and cancellation and movement bounds.

### Work the question

1. Keep taxi-out and schedule departure delay distinct; they measure different process stages. A slope mismatch does not identify schedule padding, and a pooled airport relationship is not one airport's causal response.
2. Build or inspect hourly cells and bins with their counts. The chapter code pools row means by scheduled-departure counts although each row mean excludes cancellations and missing measurements. Do not call the result an exact operated-flight mean.
3. Fit the convex curve on 2023 bins and assess 2024 separately. Report MAE about 0.54 and 0.64 minutes, the knee at the lower grid boundary, and the easing in thin top bins the convex form cannot reproduce.
4. Carry the fourteen points as an inferred lookup on load 0.05 to 1.35. Preserve refusal outside the domain. The lowest-load baseline is inferred at 0.05, not observed zero-queue taxi-out.
5. Audit units: delay and padding are minute/departure, padding changes minute/departure/day, the aggregate queue is minutes and its flows minute/day. Cancellation slope is departure/minute. State the assumed representative peak-hour exposure used per model day.
6. Compare caps on identical draws with both cancellation and movement bounds. No cap violates cancellation in twenty-one of forty draws; preserve IDs even when displayed numbers round alike. Report movement losses and the omitted rescheduling path beside delay benefits.

### Limits to preserve

The curve is a conditional cross-sectional relationship across thirty airports. Confounding does not establish the direction of bias. Policy-table `worst` comes from the generic minimum helper; for lower-is-better delay the adverse end is its maximum, labeled `best` internally, so report direction explicitly. No cap comparison authorizes a real schedule change.

### Connected chapters

Use Chapter 10 for population and weighting boundaries, Chapter 15 for lookup refusal, Chapter 18 for queues, Chapter 30 for all-bound shared draws, and Chapter 35 for fit versus holdout.

## Apply it to the user's inputs

1. Open `notebooks/39-congestion-curve.ipynb` and run all cells. Every later cell depends on the model cells near the top.
2. Restate the user's numbers in the chapter's units and time base before calling anything. Ask for any missing initial value, rate or horizon rather than substituting the chapter's defaults.
3. Call the chapter's functions below with the user's values in a new cell at the end of the notebook, or call a demonstration function with a different setting and compare it with the chapter's case.
4. Report the inputs used, the numbers the cell printed, the check that confirms them, and the assumptions from the Method section that the conclusion depends on.

Chapter functions defined in the notebook:

- `build_document(lookup_points: tuple[tuple[float, float], ...], scheduled_load: float, departures_per_day: float, cancel_at_record: float, cancel_per_minute: float, record_queue_delay: float, representative_peak_departures: float, baseline_taxi_out: float, lookup_note: str='', queue_clear_time: float=2.0, padding_adjustment_time: float=90.0, load_cap: float=10.0, movements_retained: float=1.0)`: The airport model with the fitted curve in place and every value labeled.
- `free_knobs()`: The parameters nobody measured. Three, by design.
- `read_months(path: Path=MONTHS)`: Every airport-month row as floats, with the year split out.
- `read_hour_bins(path: Path=HOURS)`: Every airport-year load bin as floats.
- `read_clock_hours(path: Path=CLOCK)`: Every airport-year clock hour as floats.
- `rows_for_year(rows: list[dict], year: int)`
- `pooled_bins(rows: list[dict], value: str='mean_taxi_out', min_flights: int=MIN_BIN_FLIGHTS)`: (bin center, flight-weighted mean of `value`, flights) per load bin across airports.
- `bins_as_series(bins: list[tuple[float, float, int]], path: Path=HOURS)`: The bins as Chapter 35's Series: load as time, taxi-out as value, with checksum.
- `curve(load: float, base: float, knee: float, curvature: float)`
- `fit_curve(bins: list[tuple[float, float, int]], knobs: tuple[Knob, ...]=KNOBS, refinements: int=2)`: Grid search over the three knobs, re-gridded around the winner, scored by bin MAE.
- `fitted_congestion_lookup(hour_rows: list[dict] | None=None)`: The exported artifact: the fitted curve sampled on the fit-year bin centers.
- `lookup_note(fit: dict, bins: list[tuple[float, float, int]], path: Path=HOURS)`
- `holdout_error(points: tuple[tuple[float, float], ...], holdout_rows: list[dict])`: The fitted lookup against the other year's bins. Loads outside the domain are refused.
- `convex_above_knee(points: tuple[tuple[float, float], ...], knee: float)`: Non-decreasing everywhere, and second differences non-negative from the knee upward.
- `cancellation_fit(month_rows: list[dict])`: Departure-weighted least squares of cancellation share on mean delay: (base, slope).
- `observed_summary(month_rows: list[dict])`: Departure-weighted facts from the airport-month file the model is anchored to.
- `month_load_correlation(month_rows: list[dict])`: Correlation of monthly mean departure delay with monthly load, across airport-months.
- `clock_profile(clock_rows: list[dict], min_flights: int=MIN_BIN_FLIGHTS)`: (hour, mean departure delay, mean taxi-out, flights) pooled across airports.
- `fitted_document(month_rows: list[dict] | None=None, hour_rows: list[dict] | None=None, **overrides)`: The airport document with the fitted lookup, cancellation slope, and observed anchors.
- `policies(facts: dict)`
- `uncertainties(facts: dict, points: tuple[tuple[float, float], ...])`: Ranges somebody will defend, kept inside the lookup's domain so every draw can run.
- `bounds(facts: dict)`
- `policy_table(document: ModelDocument, facts: dict, points: tuple[tuple[float, float], ...], draws: int=40, seed: int=7)`: Every policy on delay, cancellations, and movements, with the bounds that can veto.
- `critic_report(document: ModelDocument)`
- `padding_run(document: ModelDocument, days: int=365)`: One year at the document's own load: how much of the realized delay padding hides.
- `run_case(month_rows: list[dict] | None=None, hour_rows: list[dict] | None=None, clock_rows: list[dict] | None=None)`: Everything the chapter prints, in one dict, from the committed record.
- `as_variable(points: tuple[tuple[float, float], ...], note: str)`: The lookup as a document variable, so a reader can see how it is carried.

Demonstrations in the notebook, with the chapter's settings:

1. Two measures, two slopes: `two_measures(measure='taxi', year=2023, min_flights=20000)`. Settings offered: `measure` in ['taxi', 'delay']; `year` in [2023, 2024]; `min_flights` in [20000, 100000].
2. A convex curve fitted to one year: `curve_against_bins(curvature=3.09, year=2023)`. Settings offered: `curvature` in [2.0, 3.09, 4.0]; `year` in [2023, 2024].
3. Pricing a cap needs two points on the curve: `cap_price(cap='cap_at_p95', load=1.0944)`. Settings offered: `cap` in ['cap_at_p95', 'cap_at_p90']; `load` in [0.9958, 1.0944, 1.2218].
4. Padding hides the delay it responds to: `padding_loop(time=90.0, load=1.0944)`. Settings offered: `time` in [30.0, 90.0, 180.0]; `load` in [1.0944, 1.2218].

## Reference numbers

The chapter's settings give these values in the notebook. Reproduce one before trusting a new run.

- Demonstration 1: Measure Taxi-out; Year 2023; Smallest bin kept load 0.05, 22,576 departures; Mean at load 0.05 (minutes) 15.91; Mean at load 1.15 (minutes) 20.87; Change (minutes) 4.96; Bins kept 14
- Demonstration 2: Curvature (minutes per unit of squared load) 3.09; Year scored 2023; Bins scored 14; Mean absolute error (minutes) 0.54; Curve at load 1.35 (minutes) 22.42; Bin mean at load 1.35 (minutes) 19.37
- Demonstration 3: Cap p95; Load as filed 1.094; Load after the cap 1.000; Delay above baseline, as filed (minutes) 4.59; Delay above baseline, capped (minutes) 3.97; Benefit per peak departure (minutes) 0.61; Departures kept by the cap (percent) 98.95; Movements lost, model (percent) 2.26
- Demonstration 4: Padding adjustment time (days) 90; Load 1.094; Realized delay, day 365 (minutes) 4.59; Padding, day 90 (minutes) 2.87; Padding, day 365 (minutes) 4.51; Reported delay, day 365 (minutes) 0.08

Copyright Jason Karpeles. All rights reserved.
