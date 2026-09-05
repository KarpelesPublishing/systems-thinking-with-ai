"""Chapter 39: BTS Reporting Carrier On-Time Performance, aggregated to airport-months.

Downloads the monthly prezip files for the fit year (2023) and the holdout year (2024) from
transtats.bts.gov and streams each CSV row by row out of its zip, never holding a whole file.
Pass one counts departures per origin to pick the thirty busiest airports of the fit year. Pass
two keeps one cell per airport, date, and clock hour for those airports, and three derived files
are written from the cells: airport-months, airport-year load bins, and airport-year clock hours.

    uv run python scripts/fetch_data.py bts-ontime

Standard library only. A month that fails to download is retried once and then skipped; the
manifest records which months were used, and the README's Known breaks section lists any gap.
"""
import csv
import datetime as dt
import io
import statistics
import sys
import time
import urllib.error
import zipfile
from pathlib import Path

from scripts.fetch.common import download

CASE = "bts_ontime"
FIT_YEAR = 2023
HOLDOUT_YEAR = 2024
YEARS = (FIT_YEAR, HOLDOUT_YEAR)
TOP_N = 30
BASE = "https://transtats.bts.gov/PREZIP/"
PATTERN = "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_{year}_{month}.zip"
SOURCE_URL = "https://www.transtats.bts.gov/Tables.asp?QO_VQ=EFD"
LICENCE = "United States federal work, public domain (17 U.S.C. 105)"
COLUMNS = ["airport", "period", "scheduled_departures", "peak_hour_departures",
           "mean_dep_delay_minutes", "cancellation_share", "mean_taxi_out",
           "departures_above_p90", "departures_above_p95", "p90_hourly_departures",
           "p95_hourly_departures", "load"]


def month_url(year: int, month: int) -> str:
    return BASE + PATTERN.format(year=year, month=month)


def _valid_zip(path: Path) -> bool:
    try:
        with zipfile.ZipFile(path) as z:
            return z.testzip() is None and any(n.endswith(".csv") for n in z.namelist())
    except (zipfile.BadZipFile, OSError):
        return False


def download_month(raw_dir: Path, year: int, month: int, timeout: int = 1800) -> Path | None:
    """One monthly zip, kept if already present and valid, retried once on failure."""
    dest = raw_dir / PATTERN.format(year=year, month=month)
    if dest.exists() and _valid_zip(dest):
        print(f"have {dest.name} ({dest.stat().st_size:,} bytes)", flush=True)
        return dest
    for attempt in (1, 2):
        started = time.time()
        try:
            print(f"downloading {dest.name} (attempt {attempt})", flush=True)
            download(month_url(year, month), dest, timeout=timeout)
            if _valid_zip(dest):
                print(f"got {dest.name} ({dest.stat().st_size:,} bytes, "
                      f"{time.time() - started:.0f}s)", flush=True)
                return dest
            print(f"bad zip {dest.name}", flush=True)
        except (urllib.error.URLError, OSError, TimeoutError) as exc:
            print(f"failed {dest.name}: {exc}", flush=True)
        dest.unlink(missing_ok=True)
    return None


# ---------------------------------------------------------------- streaming aggregation

BIN_WIDTH = 0.1
MONTH_COLUMNS = COLUMNS
HOUR_LOAD_COLUMNS = ["airport", "year", "load_bin_low", "flights", "mean_taxi_out",
                     "mean_dep_delay_minutes", "cancellation_share"]
CLOCK_HOUR_COLUMNS = ["airport", "year", "hour", "flights", "mean_dep_delay_minutes",
                      "mean_taxi_out"]


def stream_rows(path: Path):
    """Yield dict rows from the one CSV inside a monthly zip, never loading it whole."""
    with zipfile.ZipFile(path) as z:
        name = next(n for n in z.namelist() if n.endswith(".csv"))
        with z.open(name) as handle:
            text = io.TextIOWrapper(handle, encoding="utf-8", newline="")
            yield from csv.DictReader(text)


def count_origins(path: Path, counts: dict[str, int]) -> int:
    """Pass one: scheduled departures per origin airport, to pick the busiest."""
    rows = 0
    for row in stream_rows(path):
        rows += 1
        counts[row["Origin"]] = counts.get(row["Origin"], 0) + 1
    return rows


def _hour_of(crs: str) -> int | None:
    if len(crs) < 3 or not crs.isdigit():
        return None
    return min(int(crs[:-2]), 23)


def accumulate(path: Path, airports: set[str], cells: dict) -> int:
    """Pass two: per (airport, date, clock hour) sums for the chosen airports.

    Each cell holds [scheduled, delay_sum, delay_n, taxi_sum, taxi_n, cancelled]. Delay and
    taxi-out are summed over flights that operated; cancelled flights count in scheduled and
    cancelled only.
    """
    rows = 0
    for row in stream_rows(path):
        rows += 1
        airport = row["Origin"]
        if airport not in airports:
            continue
        hour = _hour_of(row["CRSDepTime"])
        if hour is None:
            continue
        cell = cells.get((airport, row["FlightDate"], hour))
        if cell is None:
            cell = cells[(airport, row["FlightDate"], hour)] = [0, 0.0, 0, 0.0, 0, 0]
        cell[0] += 1
        if row["Cancelled"] not in ("0.00", "0", "0.0", ""):
            cell[5] += 1
            continue
        if row["DepDelayMinutes"]:
            cell[1] += float(row["DepDelayMinutes"])
            cell[2] += 1
        if row["TaxiOut"]:
            cell[3] += float(row["TaxiOut"])
            cell[4] += 1
    return rows


def percentile(values: list, q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def _add(total: list, cell: list) -> None:
    for i in range(6):
        total[i] += cell[i]


def capacity_proxies(cells: dict, airports: list[str]) -> tuple[dict, dict]:
    """Fit-year p90 and p95 of scheduled departures per clock hour, zero hours included."""
    counts: dict[str, list[int]] = {a: [] for a in airports}
    days: dict[str, set[str]] = {a: set() for a in airports}
    for (airport, date, _hour), cell in cells.items():
        if int(date[:4]) == FIT_YEAR:
            counts[airport].append(cell[0])
            days[airport].add(date)
    for airport in airports:
        counts[airport].extend([0] * (24 * len(days[airport]) - len(counts[airport])))
    return ({a: percentile(counts[a], 0.90) for a in airports},
            {a: percentile(counts[a], 0.95) for a in airports})


def derive(cells: dict, airports: list[str], months_used: dict[int, list[int]]
           ) -> tuple[list[dict], list[dict], list[dict]]:
    """Airport-month rows, airport-year load-bin rows, and airport-year clock-hour rows."""
    p90, p95 = capacity_proxies(cells, airports)
    months: dict[tuple[str, str], list] = {}
    peaks: dict[tuple[str, str], dict[str, int]] = {}
    above: dict[tuple[str, str], list[float]] = {}
    load_bins: dict[tuple[str, int, int], list] = {}
    clock: dict[tuple[str, int, int], list] = {}
    for (airport, date, hour), cell in cells.items():
        year, period = int(date[:4]), date[:7]
        if year not in months_used or int(date[5:7]) not in months_used[year]:
            continue
        key = (airport, period)
        _add(months.setdefault(key, [0, 0.0, 0, 0.0, 0, 0]), cell)
        day_peaks = peaks.setdefault(key, {})
        day_peaks[date] = max(day_peaks.get(date, 0), cell[0])
        spill = above.setdefault(key, [0.0, 0.0])
        spill[0] += max(0.0, cell[0] - p90[airport])
        spill[1] += max(0.0, cell[0] - p95[airport])
        load = cell[0] / p95[airport] if p95[airport] else 0.0
        _add(load_bins.setdefault((airport, year, int(load // BIN_WIDTH)),
                                  [0, 0.0, 0, 0.0, 0, 0]), cell)
        _add(clock.setdefault((airport, year, hour), [0, 0.0, 0, 0.0, 0, 0]), cell)

    month_rows = []
    for (airport, period), m in sorted(months.items()):
        peak = statistics.fmean(peaks[(airport, period)].values())
        month_rows.append({
            "airport": airport,
            "period": f"{period}-01",
            "scheduled_departures": m[0],
            "peak_hour_departures": round(peak, 3),
            "mean_dep_delay_minutes": round(m[1] / m[2], 3) if m[2] else "",
            "cancellation_share": round(m[5] / m[0], 5),
            "mean_taxi_out": round(m[3] / m[4], 3) if m[4] else "",
            "departures_above_p90": round(above[(airport, period)][0], 1),
            "departures_above_p95": round(above[(airport, period)][1], 1),
            "p90_hourly_departures": round(p90[airport], 2),
            "p95_hourly_departures": round(p95[airport], 2),
            "load": round(peak / p95[airport], 4) if p95[airport] else "",
        })
    bin_rows = []
    for (airport, year, index), b in sorted(load_bins.items()):
        bin_rows.append({
            "airport": airport, "year": year, "load_bin_low": round(index * BIN_WIDTH, 1),
            "flights": b[0],
            "mean_taxi_out": round(b[3] / b[4], 3) if b[4] else "",
            "mean_dep_delay_minutes": round(b[1] / b[2], 3) if b[2] else "",
            "cancellation_share": round(b[5] / b[0], 5),
        })
    clock_rows = []
    for (airport, year, hour), h in sorted(clock.items()):
        clock_rows.append({
            "airport": airport, "year": year, "hour": hour, "flights": h[0],
            "mean_dep_delay_minutes": round(h[1] / h[2], 3) if h[2] else "",
            "mean_taxi_out": round(h[3] / h[4], 3) if h[4] else "",
        })
    return month_rows, bin_rows, clock_rows


def write_csv(rows: list[dict], path: Path, columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def fetch(dest_root: Path) -> dict:
    """Download, aggregate in two streaming passes, write the CSVs and MANIFEST.json."""
    from scripts.fetch_data import write_manifest

    raw_dir = dest_root / "raw" / CASE
    case_dir = dest_root / CASE
    raw_dir.mkdir(parents=True, exist_ok=True)
    paths: dict[tuple[int, int], Path] = {}
    missing: list[str] = []
    for year in YEARS:
        for month in range(1, 13):
            path = download_month(raw_dir, year, month)
            if path is None:
                missing.append(f"{year}-{month:02d}")
            else:
                paths[(year, month)] = path
    origin_counts: dict[str, int] = {}
    for (year, month), path in paths.items():
        if year == FIT_YEAR:
            count_origins(path, origin_counts)
    airports = sorted(origin_counts, key=lambda a: (-origin_counts[a], a))[:TOP_N]
    print(f"busiest {TOP_N} origins of {FIT_YEAR}: {' '.join(airports)}", flush=True)
    cells: dict = {}
    months_used: dict[int, list[int]] = {y: [] for y in YEARS}
    total_rows = 0
    for (year, month), path in paths.items():
        started = time.time()
        n = accumulate(path, set(airports), cells)
        total_rows += n
        months_used[year].append(month)
        print(f"aggregated {path.name}: {n:,} rows in {time.time() - started:.0f}s", flush=True)
    month_rows, bin_rows, clock_rows = derive(cells, airports, months_used)
    write_csv(month_rows, case_dir / "airport_month_delay.csv", MONTH_COLUMNS)
    write_csv(bin_rows, case_dir / "airport_hour_load.csv", HOUR_LOAD_COLUMNS)
    write_csv(clock_rows, case_dir / "airport_clock_hour.csv", CLOCK_HOUR_COLUMNS)
    manifest = {
        "case": CASE,
        "source_url": SOURCE_URL,
        "licence": LICENCE,
        "retrieved": dt.date.today().isoformat(),
        "vintage": f"monthly prezip files for {FIT_YEAR} and {HOLDOUT_YEAR}, "
                   f"{total_rows:,} flight rows aggregated",
        "fetch_command": "uv run python scripts/fetch_data.py bts-ontime",
        "months_missing": missing,
        "airports": airports,
        "files": ["airport_month_delay.csv", "airport_hour_load.csv", "airport_clock_hour.csv"],
    }
    write_manifest(case_dir, manifest)
    return manifest


if __name__ == "__main__":
    fetch(Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data"))
