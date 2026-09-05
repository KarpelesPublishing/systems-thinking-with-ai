"""Chapter 38: manufacturing utilization, production and prices; total industrial capacity.

Four monthly series retrieved through FRED (Federal Reserve Bank of St. Louis), each a plain CSV
with no API key:

    MCUMFN       manufacturing capacity utilization, percent of capacity (Federal Reserve G.17)
    CAPB50001S   total industrial capacity index, 2017 = 100 (Federal Reserve G.17)
    IPMAN        manufacturing industrial production index, 2017 = 100 (Federal Reserve G.17)
    PCUOMFGOMFG  producer price index, total manufacturing industries, Dec 1984 = 100 (BLS PPI)

The producing agencies are the Federal Reserve Board (G.17 release) and the Bureau of Labor
Statistics (PPI program). FRED is the retrieval route only. All four are United States federal
works in the public domain.

The capacity index includes mining and utilities, unlike the manufacturing-only utilization
and production series. Their ratio must not be used to reconstruct manufacturing utilization.

Derivation: the four raw files are joined on month. The committed record starts at the first month
every G.17 series reports (1972-01) and ends at the last month all three G.17 series report. The
PPI column is blank before 1984-12 and wherever BLS reports no value. Values are copied as
published, with no rounding and no seasonal or price adjustment beyond what the agencies apply.
"""
import csv
import datetime as dt
from pathlib import Path

from scripts.fetch.common import download

CASE = "fred_capacity"
BASE = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
SERIES = {
    "utilization": "MCUMFN",
    "capacity_index": "CAPB50001S",
    "production_index": "IPMAN",
    "ppi": "PCUOMFGOMFG",
}
G17 = ("utilization", "capacity_index", "production_index")
COLUMNS = ("period", "utilization", "capacity_index", "production_index", "ppi")


def read_fred(path: Path) -> dict[str, str]:
    """Month (YYYY-MM-01) to the published value as text; missing values are dropped."""
    out: dict[str, str] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        if len(header) != 2 or header[0] != "observation_date":
            raise ValueError(f"{path.name}: unexpected header {header}")
        for date, value in reader:
            if value.strip() and value.strip() != ".":
                out[date] = value.strip()
    return out


def derive(raw: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    """Join the four series on month across the G.17 common window."""
    start = max(min(raw[name]) for name in G17)
    end = min(max(raw[name]) for name in G17)
    rows = []
    for month in sorted(raw["utilization"]):
        if not start <= month <= end:
            continue
        row = {"period": month}
        for name in SERIES:
            row[name] = raw[name].get(month, "")
        if any(not row[name] for name in G17):
            raise ValueError(f"{month}: a G.17 series is missing inside the common window")
        rows.append(row)
    return rows


def fetch(dest_root: Path) -> dict:
    """Download the four series, derive the joined monthly record, write the manifest."""
    from scripts.fetch_data import write_manifest

    raw_dir = dest_root / "raw" / CASE
    case_dir = dest_root / CASE
    case_dir.mkdir(parents=True, exist_ok=True)
    raw: dict[str, dict[str, str]] = {}
    for name, series_id in SERIES.items():
        path = download(BASE + series_id, raw_dir / f"{series_id}.csv")
        raw[name] = read_fred(path)
    rows = derive(raw)
    out = case_dir / "capacity_monthly.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(COLUMNS), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    today = dt.date.today().isoformat()
    manifest = {
        "case": CASE,
        "source_url": [BASE + series_id for series_id in SERIES.values()],
        "producers": "Federal Reserve Board, G.17 Industrial Production and Capacity Utilization "
                     "(MCUMFN, CAPB50001S, IPMAN); Bureau of Labor Statistics, Producer Price "
                     "Index (PCUOMFGOMFG). Retrieved through FRED, Federal Reserve Bank of "
                     "St. Louis.",
        "licence": "United States federal works, public domain",
        "retrieved": today,
        "vintage": f"FRED download of {today}; record {rows[0]['period'][:7]} to "
                   f"{rows[-1]['period'][:7]}",
        "fetch_command": "uv run python scripts/fetch_data.py fred-capacity",
        "files": ["capacity_monthly.csv"],
    }
    write_manifest(case_dir, manifest)
    return manifest
