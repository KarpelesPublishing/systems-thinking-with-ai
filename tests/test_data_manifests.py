"""The committed records match their manifests, offline, every run."""
import csv
import hashlib
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CASES = sorted(p.parent for p in DATA.glob("*/MANIFEST.json"))
SECTIONS = ["Source", "Licence", "Retrieval", "Derivation", "Column dictionary", "Checksum",
            "Known breaks"]


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_every_committed_data_file_matches_its_manifest_checksum(case):
    manifest = json.loads((case / "MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["files"], case
    for entry in manifest["files"]:
        path = case / entry["path"]
        assert path.exists(), path
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], path
        assert path.stat().st_size < 400_000, f"{path} is too large to commit"
    for key in ("case", "source_url", "licence", "retrieved", "vintage", "fetch_command"):
        assert manifest.get(key), f"{case.name}: manifest lacks {key}"


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_every_data_readme_has_the_required_sections(case):
    text = (case / "README.md").read_text(encoding="utf-8")
    for section in SECTIONS:
        assert re.search(rf"^## {section}\b", text, re.M), f"{case.name}: missing {section}"
    assert "—" not in text and "--" not in text.replace("---", "")


@pytest.mark.parametrize("case", CASES, ids=lambda p: p.name)
def test_column_dictionary_covers_every_committed_column(case):
    text = (case / "README.md").read_text(encoding="utf-8")
    for path in case.glob("*.csv"):
        with path.open(encoding="utf-8", newline="") as handle:
            header = next(csv.reader(handle))
        for column in header:
            assert f"`{column}`" in text, f"{case.name}: {path.name} column {column} undocumented"


def test_no_default_test_imports_the_network():
    for path in (ROOT / "tests").rglob("test_*.py"):
        text = path.read_text(encoding="utf-8")
        if "urllib.request" in text:
            assert "pytest.mark.network" in text, path
