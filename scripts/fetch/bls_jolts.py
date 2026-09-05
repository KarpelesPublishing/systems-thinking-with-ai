"""BLS JOLTS national totals plus CES total nonfarm employment, 2015 to 2024, monthly.

Two POST requests to the BLS public API v2 without a key (unregistered requests allow ten years
and twenty-five series per call; this asks for six series over two five-year windows), the raw
JSON kept under data/raw/bls_jolts, and one derived CSV of levels in thousands, seasonally
adjusted, sorted ascending by month. Standard library only.

    uv run python scripts/fetch_data.py bls-jolts
"""
import csv
import datetime as dt
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.fetch.common import USER_AGENT  # noqa: E402
from scripts.fetch_data import write_manifest  # noqa: E402

API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
SERIES = {
    "JTS000000000000000JOL": "openings",
    "JTS000000000000000HIL": "hires",
    "JTS000000000000000QUL": "quits",
    "JTS000000000000000LDL": "layoffs",
    "JTS000000000000000TSL": "separations",
    "CES0000000001": "employment",
}
COLUMNS = ["period", "openings", "hires", "quits", "layoffs", "separations", "employment"]
WINDOWS = (("2015", "2019"), ("2020", "2024"))
LICENCE = ("Public domain (United States federal government work); the Bureau of Labor "
           "Statistics requests attribution")


def request(startyear: str, endyear: str, timeout: int = 120) -> dict:
    payload = json.dumps({"seriesid": sorted(SERIES), "startyear": startyear,
                          "endyear": endyear}).encode("utf-8")
    req = urllib.request.Request(API, data=payload, method="POST", headers={
        "User-Agent": USER_AGENT, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        body = json.loads(response.read().decode("utf-8"))
    if body.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS API: {body.get('status')}: {body.get('message')}")
    return body


def derive(responses: list[dict]) -> list[dict[str, str]]:
    """One row per month with every series present, from the raw API responses."""
    table: dict[str, dict[str, str]] = {}
    for body in responses:
        for series in body["Results"]["series"]:
            column = SERIES[series["seriesID"]]
            for point in series["data"]:
                if not point["period"].startswith("M") or point["period"] == "M13":
                    continue
                period = f"{point['year']}-{point['period'][1:]}-01"
                table.setdefault(period, {"period": period})[column] = point["value"]
    rows = [row for _, row in sorted(table.items())
            if all(column in row for column in COLUMNS[1:])]
    if not rows:
        raise RuntimeError("no complete monthly rows in the BLS responses")
    return rows


def fetch(dest_root: Path) -> dict:
    case_dir = dest_root / "bls_jolts"
    raw_dir = dest_root / "raw" / "bls_jolts"
    case_dir.mkdir(parents=True, exist_ok=True)
    raw_dir.mkdir(parents=True, exist_ok=True)
    retrieved = dt.date.today().isoformat()
    responses = []
    for start, end in WINDOWS:
        body = request(start, end)
        (raw_dir / f"jolts_{start}_{end}.json").write_text(
            json.dumps(body, indent=1) + "\n", encoding="utf-8")
        responses.append(body)
    rows = derive(responses)
    out = case_dir / "jolts_monthly.csv"
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "case": "bls_jolts",
        "source_url": API,
        "licence": LICENCE,
        "retrieved": retrieved,
        "vintage": f"BLS public API v2 data as published on {retrieved}, "
                   f"{rows[0]['period'][:7]} to {rows[-1]['period'][:7]}, seasonally adjusted",
        "fetch_command": "uv run python scripts/fetch_data.py bls-jolts",
        "files": [out.name],
    }
    write_manifest(case_dir, manifest)
    return json.loads((case_dir / "MANIFEST.json").read_text(encoding="utf-8"))
