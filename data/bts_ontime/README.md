# BTS Reporting Carrier On-Time Performance, aggregated for Chapter 39

Three derived files for the thirty busiest origin airports of 2023, built from the monthly
flight-level files the Bureau of Transportation Statistics publishes. Nothing here is a flight;
every row is a sum or a mean over thousands of them.

## Source

Bureau of Transportation Statistics, Reporting Carrier On-Time Performance (1987 to present),
table listing at https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFD. The files read are the
monthly prezip archives at
`https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_YYYY_M.zip`
for 2023 (months 1 to 12, the fit year) and 2024 (months 1 to 12, the holdout year). Each archive
holds one CSV of every scheduled domestic flight by a reporting carrier, 110 columns, roughly
520,000 to 635,000 rows a month. The columns used are `Origin`, `FlightDate`, `CRSDepTime`,
`DepDelayMinutes`, `Cancelled`, and `TaxiOut`.

## Licence

United States federal government work, in the public domain under 17 U.S.C. 105. The derived
files may be redistributed. The raw archives are not committed; they are 25 to 35 MB each and
live under `data/raw/bts_ontime/`, which git ignores.

## Retrieval

Retrieved 2026-09-03 by `uv run python scripts/fetch_data.py bts-ontime`, which downloads any
archive not already present and valid, retries a failed month once, and streams each CSV out of
its zip a row at a time. All twenty-four months were retrieved; one (2024-11) needed the retry.
Total raw download 673 MB. the verify mode of `scripts/fetch_data.py` recomputes the
checksums offline.

## Derivation

Pass one counts scheduled departures per origin in 2023 and keeps the thirty largest:
ATL DEN DFW ORD CLT LAX LAS PHX MCO SEA LGA BOS DCA EWR SFO JFK DTW MSP IAH SLC MIA BNA BWI AUS
SAN PHL FLL MDW TPA DAL. Pass two keeps one cell per airport, calendar date, and scheduled
departure clock hour (`CRSDepTime` truncated to the hour) for those airports, holding scheduled
departures, the sum and count of `DepDelayMinutes` and `TaxiOut` over flights that operated, and
cancellations. Cancelled flights count as scheduled and cancelled and contribute no delay or
taxi-out. Rows with a malformed `CRSDepTime` are dropped.

The capacity proxy is per airport: the 95th percentile of scheduled departures per clock hour
over every hour of every 2023 day on which the airport had a flight, empty hours included.
The 90th percentile is kept beside it. Both are fixed from 2023 and applied to 2024 as well, so
a 2024 hour can carry a load the 2023 record never reached.

`airport_month_delay.csv` has one row per airport-month. `peak_hour_departures` is the largest
hourly count on each day, averaged over the month's days. `load` is that average divided by the
airport's 2023 p95 hourly count. `departures_above_p90` and `departures_above_p95` sum, over
the month's hours, the departures in excess of the p90 or p95 count: the movements a cap at
that level would have to move or drop.

`airport_hour_load.csv` has one row per airport, year, and load bin. Each clock-hour cell's
load is its departures divided by the airport's p95; bins are 0.1 wide and labeled by their
lower edge. Means are flight-weighted over the cells in the bin.

`airport_clock_hour.csv` has one row per airport, year, and scheduled departure clock hour,
pooling every day of the year.

## Column dictionary

`airport_month_delay.csv`

| Column | Unit | Type | Evidence level |
|---|---|---|---|
| `airport` | IATA code | text | observed |
| `period` | first day of month, YYYY-MM-01 | date | observed |
| `scheduled_departures` | departures | integer | observed |
| `peak_hour_departures` | departures per hour, mean over days of the daily maximum | float | observed |
| `mean_dep_delay_minutes` | minutes per operated departure, against schedule | float | observed |
| `cancellation_share` | share of scheduled departures cancelled | float | observed |
| `mean_taxi_out` | minutes per operated departure, pushback to wheels up | float | observed |
| `departures_above_p90` | departures in hours above the p90 count | float | derived |
| `departures_above_p95` | departures in hours above the p95 count | float | derived |
| `p90_hourly_departures` | departures per hour, 2023 90th percentile | float | derived |
| `p95_hourly_departures` | departures per hour, 2023 95th percentile | float | derived |
| `load` | dimensionless, peak_hour_departures over p95_hourly_departures | float | derived |

`airport_hour_load.csv`

| Column | Unit | Type | Evidence level |
|---|---|---|---|
| `airport` | IATA code | text | observed |
| `year` | calendar year | integer | observed |
| `load_bin_low` | dimensionless, lower edge of a 0.1-wide load bin | float | derived |
| `flights` | scheduled departures in the bin | integer | observed |
| `mean_taxi_out` | minutes per operated departure | float | observed |
| `mean_dep_delay_minutes` | minutes per operated departure, against schedule | float | observed |
| `cancellation_share` | share of scheduled departures cancelled | float | observed |

`airport_clock_hour.csv`

| Column | Unit | Type | Evidence level |
|---|---|---|---|
| `airport` | IATA code | text | observed |
| `year` | calendar year | integer | observed |
| `hour` | scheduled departure clock hour, 0 to 23, local time | integer | observed |
| `flights` | scheduled departures in that hour over the year | integer | observed |
| `mean_dep_delay_minutes` | minutes per operated departure, against schedule | float | observed |
| `mean_taxi_out` | minutes per operated departure | float | observed |

Every value in the fitted curve the chapter builds from these files is evidence level
`inferred`, and none of it is stored here.

## Checksum

Recorded in `MANIFEST.json` and checked by `tests/test_data_manifests.py` offline.

| File | SHA-256 | Bytes | Rows |
|---|---|---|---|
| `airport_month_delay.csv` | `9ff2b6472b6ddcc3c978210e947035d0b68355e45c08260e674285d62cc651a3` | 55,788 | 720 |
| `airport_hour_load.csv` | `2147bc0fa6e7b820eb27df249d202c4858789e0818a358aae1b139f5fc0c9147` | 32,725 | 823 |
| `airport_clock_hour.csv` | `6b8fd8a3289954cc927218b97af5e25374e2f9b05dde830e309e19ffaa7bd9d7` | 35,785 | 1,176 |

## Known breaks

- No months are missing from either year.
- Only reporting carriers appear in the source (those above the BTS revenue threshold), so
  scheduled departures undercount total airport movements, and arrivals are absent altogether.
  Load is a proxy built from reported departures, not from runway movements.
- `DepDelayMinutes` is floored at zero by BTS, so early departures count as zero delay and the
  mean is a mean of non-negative values.
- Clock hour 24 does not occur in the source; a `CRSDepTime` of 2400 would truncate to hour 24
  and is clamped to 23. Hours 1 to 4 have too few flights for the pooled profile and the chapter
  drops any bin or hour under 20,000 flights.
- The p95 capacity proxy is fixed from 2023. A 2024 airport whose schedule grew carries loads
  above 1.35, which the fitted lookup refuses by design.
- BTS revises monthly files after first release. The checksums fix the vintage retrieved on
  2026-09-03; a later download may differ.
