"""NHS England consultant-led Referral to Treatment (RTT) waiting times, national monthly series.

Source landing page:
    https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/

NHS England publishes one "RTT Overview Timeseries" workbook each month, on the page for the
current financial year, covering every month since April 2007 on the commissioner basis. This
module finds the newest such workbook by reading the landing page and then the newest
`rtt-data-YYYY-YY` page, downloads it to `data/raw/`, reads the single worksheet with the
standard library (zipfile plus xml.etree, no openpyxl), and writes the derived CSV that the
Chapter 36 pack reads. The raw workbook is not committed; the CSV and its checksum are.

Licence: Open Government Licence v3.0. Attribution statement, verbatim from the licence:
"Contains public sector information licensed under the Open Government Licence v3.0."
"""

import csv
import datetime
import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

from scripts.fetch.common import download, fetch_text
from scripts.fetch_data import sha256, write_manifest

LANDING = "https://www.england.nhs.uk/statistics/statistical-work-areas/rtt-waiting-times/"
LICENCE = "Open Government Licence v3.0"
NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}

# Worksheet column letter -> CSV column. The letters are the layout of the "Full Time Series"
# sheet as published in the June 2026 release; `_header_check` refuses a workbook whose
# second header row does not carry the expected label at each letter.
COLUMNS = (
    ("V", "total_incomplete", "Total waiting (mil)"),
    ("F", "within_18_weeks", "No. within 18 weeks"),
    ("J", "over_18_weeks", "No. > 18 weeks"),
    ("L", "over_52_weeks", "No. > 52 weeks"),
    ("P", "over_65_weeks", "No. > 65 weeks"),
    ("R", "over_78_weeks", "No. > 78 weeks"),
    ("T", "over_104_weeks", "No. > 104 weeks"),
    ("D", "median_wait_weeks", "Median wait (weeks)"),
    ("AL", "new_periods", "No. of new RTT periods"),
    ("AO", "completed_pathways", "Total completed pathways"),
    ("AQ", "unreported_removals", "Total unreported removals"),
    ("AS", "total_removals", "Total removals"),
)
INTEGER_COLUMNS = {name for _, name, _ in COLUMNS} - {"median_wait_weeks"}


def newest_timeseries_url() -> str:
    """The URL of the newest RTT Overview Timeseries workbook, found from the landing page."""
    landing = fetch_text(LANDING)
    pages = re.findall(r'href="(https://www\.england\.nhs\.uk/statistics/statistical-work-areas/'
                       r'rtt-waiting-times/rtt-data-(\d{4})-\d{2}/?)"', landing)
    if not pages:
        raise RuntimeError("no rtt-data-YYYY-YY pages found on the landing page")
    for url, _ in sorted(set(pages), key=lambda p: p[1], reverse=True):
        page = fetch_text(url.rstrip("/") + "/")
        files = re.findall(r'href="([^"]*RTT-Overview-Timeseries[^"]*\.xlsx)"', page)
        if files:
            return files[-1]
    raise RuntimeError("no RTT Overview Timeseries workbook found on any yearly page")


def _shared_strings(book: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in book.namelist():
        return []
    root = ET.fromstring(book.read("xl/sharedStrings.xml"))
    return ["".join(t.text or "" for t in si.iter(f"{{{NS['m']}}}t"))
            for si in root.findall("m:si", NS)]


def read_sheet(path: Path) -> dict[int, dict[str, str]]:
    """Every row of the first worksheet as {row number: {column letter: cell text}}."""
    with zipfile.ZipFile(path) as book:
        strings = _shared_strings(book)
        root = ET.fromstring(book.read("xl/worksheets/sheet1.xml"))
    rows: dict[int, dict[str, str]] = {}
    for row in root.iter(f"{{{NS['m']}}}row"):
        cells: dict[str, str] = {}
        for cell in row.findall("m:c", NS):
            value = cell.find("m:v", NS)
            if value is None or value.text is None:
                continue
            letter = re.match(r"[A-Z]+", cell.attrib["r"]).group()
            text = strings[int(value.text)] if cell.attrib.get("t") == "s" else value.text
            cells[letter] = text
        rows[int(row.attrib["r"])] = cells
    return rows


def _header_check(rows: dict[int, dict[str, str]]) -> int:
    """Find the second header row and confirm every mapped column carries its label."""
    for number, cells in rows.items():
        if cells.get("F", "").startswith("No. within 18 weeks"):
            for letter, _, label in COLUMNS:
                found = cells.get(letter, "").strip()
                if not found.startswith(label):
                    raise RuntimeError(f"column {letter}: expected '{label}', found '{found}'")
            return number
    raise RuntimeError("header row not found: the workbook layout has changed")


MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


def _period(text: str) -> str | None:
    """`YYYY-MM` from an Excel serial date, or from a text month such as `* Feb-24`.

    The February 2024 row carries a text label with an asterisk instead of a date, because
    the workbook footnotes a definitional change there. It is a real month and is kept.
    """
    if re.fullmatch(r"\d+(\.0+)?", text):
        day = datetime.date(1899, 12, 30) + datetime.timedelta(days=int(float(text)))
        return f"{day.year:04d}-{day.month:02d}"
    match = re.search(r"([A-Z][a-z]{2})-(\d{2})\b", text)
    if match and match.group(1) in MONTHS:
        return f"20{match.group(2)}-{MONTHS.index(match.group(1)) + 1:02d}"
    return None


def _number(text: str | None, integer: bool) -> str:
    if text is None or text.strip() in ("", "-"):
        return ""
    value = float(text)
    return str(int(round(value))) if integer else f"{value:.2f}"


def derive(raw: Path, out: Path) -> list[dict[str, str]]:
    """Write the national monthly CSV from the workbook and return its rows."""
    rows = read_sheet(raw)
    header = _header_check(rows)
    records = []
    for number in sorted(rows):
        if number <= header:
            continue
        cells = rows[number]
        period = _period(cells.get("C", ""))
        if period is None:
            continue
        record = {"period": period}
        for letter, name, _ in COLUMNS:
            record[name] = _number(cells.get(letter), name in INTEGER_COLUMNS)
        if record["total_incomplete"]:
            records.append(record)
    if len(records) < 200:
        raise RuntimeError(f"only {len(records)} monthly rows found; expected the full series")
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["period"] + [n for _, n, _ in COLUMNS])
        writer.writeheader()
        writer.writerows(records)
    return records


def fetch(dest_root: Path) -> dict:
    """Download the newest workbook, derive the CSV, write MANIFEST.json, return the manifest."""
    url = newest_timeseries_url()
    raw = download(url, dest_root / "raw" / url.rsplit("/", 1)[-1])
    case_dir = dest_root / "nhs_rtt"
    records = derive(raw, case_dir / "rtt_national_monthly.csv")
    manifest = {
        "case": "nhs_rtt",
        "source_url": url,
        "landing_page": LANDING,
        "licence": LICENCE,
        "attribution": "Contains public sector information licensed under the "
                       "Open Government Licence v3.0.",
        "retrieved": datetime.date.today().isoformat(),
        "vintage": f"{records[0]['period']} to {records[-1]['period']}, "
                   f"commissioner basis, release named in source_url",
        "fetch_command": "uv run python scripts/fetch_data.py nhs-rtt",
        "raw_file": raw.name,
        "raw_sha256": sha256(raw),
        "files": ["rtt_national_monthly.csv"],
    }
    write_manifest(case_dir, manifest)
    return manifest
