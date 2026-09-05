#!/usr/bin/env python3
"""Shared style and output policy for the book's figures.

Rules, all forced by the book rather than by taste:

  Black ink only. The paperback prints black on white, so nothing may depend on hue. Curves are
  separated by dash pattern and by direct labels, never by colour.

  Small. Default width 4.4in on an 8.5 x 11 page, so a figure costs a third of a page.

  Serif, at the body's size. The interior sets 11pt serif; figure text is 7 to 8pt serif.

  Two files per figure. PNG at 300 dpi for the EPUB, PDF for print, same source script.

Nothing here invents data. Every figure either plots numbers a chapter pack produces, or draws a
structure the chapter describes in prose. The docstring of each figure script says which, and a
data figure asserts the numbers the chapter prints before it saves.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
PNG_DIR = ROOT / "build/figures/png"
PRINT_DIR = ROOT / "build/figures/print"
WIDTH_IN = 4.4

STYLE = {
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 8,
    "axes.labelsize": 8,
    "axes.titlesize": 8,
    "xtick.labelsize": 7,
    "ytick.labelsize": 7,
    "legend.fontsize": 7,
    "axes.linewidth": 0.6,
    "xtick.major.width": 0.6,
    "ytick.major.width": 0.6,
    "lines.linewidth": 1.1,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "savefig.pad_inches": 0.02,
    "text.color": "black",
    "axes.edgecolor": "black",
    "axes.labelcolor": "black",
    "xtick.color": "black",
    "ytick.color": "black",
    "mathtext.fontset": "custom",
    "mathtext.rm": "serif",
    "mathtext.it": "serif:italic",
    "mathtext.bf": "serif:bold",
}

# Dash patterns for up to four series on one axis, used in this order.
DASHES = ["solid", (0, (4.0, 1.8)), (0, (1.2, 1.4)), (0, (4.0, 1.5, 1.2, 1.5))]


def figure(height_in=2.6, width_in=WIDTH_IN):
    plt.rcParams.update(STYLE)
    return plt.subplots(figsize=(width_in, height_in))


def grid_figure(rows, cols, height_in, width_in=WIDTH_IN, sharex=False, sharey=False):
    """Small multiples: six reference modes, four archetypes, five bends."""
    plt.rcParams.update(STYLE)
    return plt.subplots(rows, cols, figsize=(width_in, height_in), sharex=sharex, sharey=sharey)


def label_line(ax, x, y, text, dx=0.0, dy=0.0, ha="left", va="center", fontsize=7):
    """Direct label at a point on a curve, replacing a colour legend."""
    return ax.text(x + dx, y + dy, text, ha=ha, va=va, fontsize=fontsize)


def save(fig, slug):
    """Write fig-<slug>.png (EPUB) and fig-<slug>.pdf (print), then close the figure."""
    if not slug.startswith("fig-"):
        slug = f"fig-{slug}"
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PRINT_DIR.mkdir(parents=True, exist_ok=True)
    written = [PNG_DIR / f"{slug}.png", PRINT_DIR / f"{slug}.pdf"]
    for path in written:
        fig.savefig(path)
    plt.close(fig)
    for path in written:
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
    return written
