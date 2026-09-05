# BLS JOLTS national totals, 2015 to 2024

The record behind Chapter 37, "Hiring Is a Pipeline, Not a Number". Six monthly series from the
US Bureau of Labor Statistics, total nonfarm, seasonally adjusted, levels in thousands.

## Source

Bureau of Labor Statistics public API v2, `https://api.bls.gov/publicAPI/v2/timeseries/data/`,
unregistered access (no key). Series:

| BLS series id | Column | Survey |
| --- | --- | --- |
| `JTS000000000000000JOL` | `openings` | JOLTS, job openings level |
| `JTS000000000000000HIL` | `hires` | JOLTS, hires level |
| `JTS000000000000000QUL` | `quits` | JOLTS, quits level |
| `JTS000000000000000LDL` | `layoffs` | JOLTS, layoffs and discharges level |
| `JTS000000000000000TSL` | `separations` | JOLTS, total separations level |
| `CES0000000001` | `employment` | CES, total nonfarm employment |

JOLTS is a sample survey of establishments and is revised; CES is a separate establishment survey
with its own revisions and an annual benchmark. The two do not share a sample.

## Licence

Public domain as a work of the United States federal government. The Bureau of Labor Statistics
asks that it be cited as the source. Suggested citation: "U.S. Bureau of Labor Statistics, Job
Openings and Labor Turnover Survey and Current Employment Statistics, retrieved through the BLS
public API on the date in MANIFEST.json."

## Retrieval

`uv run python scripts/fetch_data.py bls-jolts` runs `scripts/fetch/bls_jolts.py`, which posts two
JSON requests (2015 to 2019 and 2020 to 2024, the ten-year and twenty-five-series limits for
unregistered use) with the repository's descriptive User-Agent, writes the raw responses to
`data/raw/bls_jolts/` (ignored by git), and derives the CSV. The retrieval date is the `retrieved`
key in `MANIFEST.json`.

## Derivation

Each response is a list of series, each with monthly points keyed by year and period `M01` to
`M12`. The script keeps monthly points only, writes `period` as `YYYY-MM-01`, joins the six
series on the month, keeps months where all six are present, and sorts ascending. Values are
copied as the API returns them; nothing is rounded, rebased, or interpolated.

## Column dictionary

| Column | Unit | Type | Evidence level |
| --- | --- | --- | --- |
| `period` | first day of the month, ISO date | text | observed |
| `openings` | thousands of job openings, last business day of the month, SA | integer | observed (survey estimate) |
| `hires` | thousands of hires during the month, SA | integer | observed (survey estimate) |
| `quits` | thousands of quits during the month, SA | integer | observed (survey estimate) |
| `layoffs` | thousands of layoffs and discharges during the month, SA | integer | observed (survey estimate) |
| `separations` | thousands of total separations during the month, SA | integer | observed (survey estimate) |
| `employment` | thousands of jobs on nonfarm payrolls, SA | integer | observed (survey estimate) |

## Checksum

`MANIFEST.json` carries the SHA-256 of `jolts_monthly.csv`. The verify option of
`scripts/fetch_data.py` (see `data/README.md`) recomputes it offline. The checksum fixes the vintage: a later release with revised
months will not match, and the chapter's numbers describe this file.

## Known breaks

- April 2020: employment falls from 150,895 thousand in March to 130,426 thousand, and hires
  fall to 4,029 thousand then rise to 8,133 thousand in May. The pandemic months are in the file
  and are outside both the fit window (2015 to 2019) and the holdout window (2022 to 2024).
- `separations` exceeds `quits` plus `layoffs` by "other separations" (retirements, deaths,
  transfers, disability), which the file does not carry as its own column.
- JOLTS levels and CES employment come from different samples, so hires minus separations does
  not equal the change in employment month by month. Over 2015 to 2019 the cumulative net differs
  from the employment change by about two percent.
- BLS revises the most recent months and re-benchmarks annually. A refetch changes recent values.
