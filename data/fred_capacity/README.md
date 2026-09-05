# FRED capacity: manufacturing utilization, production and prices; total industrial capacity

Monthly record for Chapter 38, "Capacity Arrives When the Price Has Gone".

## Source

Three series are produced by the Federal Reserve Board in its G.17 release, Industrial Production
and Capacity Utilization: manufacturing capacity utilization (FRED id `MCUMFN`, percent of
capacity), the total industrial capacity index (`CAPB50001S`, 2017 = 100), and the manufacturing
industrial production index (`IPMAN`, 2017 = 100). The fourth is produced by the Bureau of Labor
Statistics in its Producer Price Index program: total manufacturing industries (`PCUOMFGOMFG`,
December 1984 = 100). All four were retrieved through FRED, the data service of the Federal
Reserve Bank of St. Louis, which is the retrieval route and not the producer.

CAPB50001S includes mining and utilities as well as manufacturing. It is broader than IPMAN
and MCUMFN, so production_index / capacity_index does not reconstruct the manufacturing
utilization series. The chapter fits utilization only; the other columns provide context.

## Licence

United States federal works, public domain. FRED redistributes them without restriction.

## Retrieval

```
uv run python scripts/fetch_data.py fred-capacity
```

The script downloads `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>` for each of the
four ids (no key needed) into `data/raw/fred_capacity/`, which git ignores, and derives the
committed file. Retrieved 2026-09-03; the manifest records the date and the checksum.

## Derivation

The four raw files are joined on month. The record starts at the first month every G.17 series
reports (1972-01) and ends at the last month all three report (2026-07 in this vintage). Values are
copied as published: no rounding, no smoothing, no adjustment beyond the seasonal adjustment the
agencies apply. Where BLS publishes no PPI value for a month, the `ppi` cell is empty; the PPI
begins in 1984-12, so every earlier `ppi` cell is empty.

## Column dictionary

| Column | Unit | Type | Evidence level |
| --- | --- | --- | --- |
| `period` | month, as `YYYY-MM-01` | text | observed |
| `utilization` | percent of capacity, seasonally adjusted | float | observed (Federal Reserve estimate) |
| `capacity_index` | total industrial capacity index, 2017 = 100, seasonally adjusted | float | observed (Federal Reserve estimate) |
| `production_index` | index, 2017 = 100, seasonally adjusted | float | observed (Federal Reserve estimate) |
| `ppi` | index, December 1984 = 100, not seasonally adjusted | float or empty | observed (BLS) |

Capacity and utilization are themselves estimates the Federal Reserve builds from surveys and
production data, not counts. The evidence level "observed" here means published by the producing
agency; the chapter treats them as the record and says so.

## Checksum

`MANIFEST.json` carries the SHA-256 of `capacity_monthly.csv`. The verify option of
`scripts/fetch_data.py` recomputes it offline. A later FRED download will differ, because
the Federal Reserve revises earlier years of the G.17 in its annual revision; the chapter's numbers
describe the vintage the checksum names.

## Known breaks

- The Federal Reserve revises capacity and utilization for earlier years at each annual
  revision, so a re-fetch changes earlier values as well as recent ones.
- `ppi` is empty before 1984-12 and in any month BLS did not publish.
- The record includes the recessions of 1973 to 1975, 1980, 1981 to 1982, 1990 to 1991, 2001, 2007
  to 2009, and 2020, none of which the chapter's model contains.
- 2020-03 to 2020-06 carries the pandemic shutdown; the chapter's fit window ends 2019-12.
