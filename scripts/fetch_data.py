#!/usr/bin/env python3
"""Fetch and derive the four case records, or verify the committed ones.

    uv run python scripts/fetch_data.py <case>    nhs-rtt, bls-jolts, fred-capacity, or bts-ontime
    uv run python scripts/fetch_data.py --verify  recompute every MANIFEST.json checksum, offline

Standard library only. Each case module under scripts/fetch exposes fetch(dest_root) -> dict
(the manifest it wrote) and derives its committed CSV from the raw download.
"""
import argparse
import hashlib
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CASES = {"nhs-rtt": "nhs_rtt", "bls-jolts": "bls_jolts", "fred-capacity": "fred_capacity",
         "bts-ontime": "bts_ontime"}
USER_AGENT = "systems-thinking-with-ai (https://github.com/KarpelesPublishing)"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_manifest(case_dir: Path, manifest: dict) -> Path:
    files = []
    for name in manifest["files"]:
        path = case_dir / name
        files.append({"path": name, "sha256": sha256(path), "bytes": path.stat().st_size,
                      "rows": sum(1 for _ in path.open(encoding="utf-8")) - 1})
    manifest = {**manifest, "files": files}
    out = case_dir / "MANIFEST.json"
    out.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return out


def verify() -> int:
    bad = 0
    for manifest_path in sorted(DATA.glob("*/MANIFEST.json")):
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for entry in manifest["files"]:
            path = manifest_path.parent / entry["path"]
            ok = path.exists() and sha256(path) == entry["sha256"]
            print(f"{'ok  ' if ok else 'BAD '} {path.relative_to(ROOT)}")
            bad += not ok
    return 1 if bad else 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("case", nargs="?", choices=sorted(CASES))
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if not a.case:
        ap.error("name a case or pass --verify")
    module = importlib.import_module(f"scripts.fetch.{CASES[a.case]}")
    manifest = module.fetch(DATA)
    print(json.dumps(manifest, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
