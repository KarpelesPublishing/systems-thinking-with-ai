#!/usr/bin/env python3
"""Run every figure generator in a subprocess and record the font that was resolved.

    uv run --group figures python build/figures/regenerate.py

Writes build/out/logs/figure-fonts.txt so a visual QA pass can say which font it was valid for.
"""
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main() -> int:
    from matplotlib import font_manager
    try:
        font = font_manager.findfont("Times New Roman", fallback_to_default=False)
    except Exception:
        font = font_manager.findfont("DejaVu Serif")
    log = ROOT / "build/out/logs"
    log.mkdir(parents=True, exist_ok=True)
    (log / "figure-fonts.txt").write_text(f"serif resolved to: {font}\n")
    print(f"font: {font}")
    failures = 0
    for script in sorted(HERE.glob("fig_*.py")):
        t0 = time.time()
        r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        status = "ok" if r.returncode == 0 else "FAIL"
        failures += r.returncode != 0
        print(f"{status:4} {script.name:44} {time.time() - t0:5.1f}s")
        if r.returncode:
            print(r.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
