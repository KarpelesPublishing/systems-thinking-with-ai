# NHS England RTT waiting times, national monthly series, 2007 to 2026

The record behind Chapter 36, "Elective Backlogs as a Stock". One row per month from August 2007
to the newest published month, on the commissioner basis, for consultant-led Referral to
Treatment (RTT) pathways in England.

## Source

NHS England, Consultant-led Referral to Treatment Waiting Times. Landing page:
`https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/`. The file read
is the "RTT Overview Timeseries Including Estimates for Missing Trusts" workbook published on the
page for the current financial year (`rtt-data-YYYY-YY`); the exact URL of the release used is
the `source_url` key in `MANIFEST.json`. The workbook has one sheet, "Full Time Series", with the
monthly national position since April 2007.

An RTT pathway is an administrative object: a clock that starts at referral and stops at the
start of treatment or at a decision that treatment is not needed. Incomplete pathways are the
clocks still running at the end of the month. One patient can hold more than one pathway; the
workbook's own estimate of unique patients runs at roughly five sixths of the pathway count.

## Licence

Open Government Licence v3.0. Attribution statement, verbatim from the licence:

"Contains public sector information licensed under the Open Government Licence v3.0."

## Retrieval

`uv run python scripts/fetch_data.py nhs-rtt` runs `scripts/fetch/nhs_rtt.py`, which reads the
landing page, finds the newest `rtt-data-YYYY-YY` page, finds the newest "RTT Overview Timeseries"
workbook link on it, downloads the workbook to `data/raw/` (ignored by git) with the repository's
descriptive User-Agent, and derives the CSV. The retrieval date is the `retrieved` key in
`MANIFEST.json`; the workbook's own SHA-256 is `raw_sha256` there.

## Derivation

The workbook is read with the standard library only (`zipfile` plus `xml.etree`). The script
locates the second header row by its "No. within 18 weeks" label, checks that every column it
maps carries the expected label, and then takes one row per month. The month cell is an Excel
serial date on every row but one: the February 2024 row carries the text `* Feb-24` because the
workbook footnotes a definitional change there (see Known breaks); the script reads that label
as a month and keeps the row. Rows whose total incomplete count is blank (months not yet
published, and the placeholder rows for future months) are dropped. A `-` in the workbook becomes
an empty cell. Counts are written as integers; the median wait is rounded to two decimals.
Nothing is rebased, smoothed, or interpolated.

Rows: 227, August 2007 to June 2026.

## Column dictionary

| Column | Unit | Type | Evidence level |
| --- | --- | --- | --- |
| `period` | calendar month, `YYYY-MM`, the month whose end the position describes | text | observed |
| `total_incomplete` | incomplete RTT pathways at month end | integer | observed (administrative count, with NHS England estimates for missing trusts) |
| `within_18_weeks` | incomplete pathways waiting 18 weeks or less | integer | observed |
| `over_18_weeks` | incomplete pathways waiting more than 18 weeks | integer | observed |
| `over_52_weeks` | incomplete pathways waiting more than 52 weeks | integer | observed |
| `over_65_weeks` | incomplete pathways waiting more than 65 weeks; empty before the band existed | integer | observed |
| `over_78_weeks` | incomplete pathways waiting more than 78 weeks; empty before the band existed | integer | observed |
| `over_104_weeks` | incomplete pathways waiting more than 104 weeks; April 2021 onward | integer | observed |
| `median_wait_weeks` | median wait of incomplete pathways, weeks, estimated from banded counts | decimal | observed (an estimate from aggregate bands, per the workbook's note 1) |
| `new_periods` | RTT clock starts during the month; collected since October 2015 | integer | observed |
| `completed_pathways` | pathways completed during the month, admitted plus non-admitted | integer | observed |
| `unreported_removals` | pathways that left the list without a completed pathway being reported; derived by NHS England as a residual | integer | observed (a published residual, not a count of validation events) |
| `total_removals` | completed pathways plus unreported removals | integer | observed (derived by NHS England) |

## Checksum

`MANIFEST.json` carries the SHA-256 of `rtt_national_monthly.csv`:
`bed7bf200c555c53828c7ef73223d804c3ba9ddffa3fb29ff99ca22d2d6020d0`.
`scripts/fetch_data.py`, run with its verify flag, recomputes it offline. The checksum fixes the
vintage: NHS England revises earlier months when trusts resubmit, and a later workbook will
differ in some cells. The chapter's numbers describe the vintage the checksum names.

## Known breaks

- From April 2013 the series excludes consultant-led sexual health pathways (workbook note 9);
  those were mostly under a week and non-admitted.
- Until September 2015, admitted pathways were adjusted for clock pauses; unadjusted figures are
  used throughout this CSV (note 5).
- `new_periods` begins in October 2015 (note 8). Earlier months are empty.
- The waiting-time bands above 52 weeks were added to the return for April 2021 data onward
  (note 10); `over_104_weeks` is empty before then, and `over_65_weeks` and `over_78_weeks` are
  empty before the months they were first published.
- From February 2024 data onward, community service pathways are no longer reported in RTT
  datasets (note 11). The February 2024 row is the flagged row.
- March 2020 to mid 2021: the monthly return continued through the pandemic, but activity and
  referrals both fell sharply and some trusts did not submit; the workbook includes estimates for
  missing trusts in the totals. Demand that was never referred in 2020 does not appear anywhere in
  this record.
- `unreported_removals` is a residual: new periods minus completed pathways minus the change in
  the list. It bundles validation, patients who declined or died, duplicate records removed, and
  reporting error. It cannot be separated into those parts from this file.
