#!/usr/bin/env python3
"""Stock-and-flow and causal-loop vocabulary for structure diagrams, in black ink.

Every function draws onto a matplotlib Axes in axis units and returns what it drew. Callers set
`ax.set_aspect("equal")` and `ax.axis("off")`, and place nodes by hand; the vocabulary here only
keeps the glyphs consistent across the book: a stock is a rectangle, a flow is a thick arrow with
a valve, a source or sink is a cloud, an auxiliary is a circle, a causal link is a thin curved
arrow with a polarity at its head, a delay is a double bar across an arrow, and a loop identifier
is a small ring with R or B in it.
"""
import math

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

NODE_W, NODE_H = 1.5, 0.7
R_AUX = 0.30


def stock(ax, x, y, label, w=NODE_W, h=NODE_H, sublabel=None, fontsize=7.0):
    """Rectangle centred at (x, y) with the stock name inside."""
    ax.add_patch(Rectangle((x - w / 2, y - h / 2), w, h, facecolor="white", edgecolor="black",
                           linewidth=1.0, zorder=3))
    if sublabel:
        ax.text(x, y + 0.11, label, ha="center", va="center", fontsize=fontsize, zorder=4)
        ax.text(x, y - 0.14, sublabel, ha="center", va="center", fontsize=fontsize - 1.2,
                style="italic", zorder=4)
    else:
        ax.text(x, y, label, ha="center", va="center", fontsize=fontsize, zorder=4)
    return (x, y, w, h)


def cloud(ax, x, y, r=0.26):
    """Source or sink: three overlapping circles, white fill, black edge."""
    for dx, dy, rr in ((-0.55 * r, -0.15 * r, 0.75 * r), (0.55 * r, -0.15 * r, 0.75 * r),
                       (0.0, 0.3 * r, 0.85 * r)):
        ax.add_patch(Circle((x + dx, y + dy), rr, facecolor="white", edgecolor="black",
                            linewidth=0.8, zorder=3))
    # white core to hide the interior arcs
    for dx, dy, rr in ((-0.55 * r, -0.15 * r, 0.75 * r), (0.55 * r, -0.15 * r, 0.75 * r),
                       (0.0, 0.3 * r, 0.85 * r)):
        ax.add_patch(Circle((x + dx, y + dy), rr - 0.045, facecolor="white", edgecolor="white",
                            linewidth=0, zorder=3.1))
    return (x, y)


def _valve(ax, x, y, angle_deg, size=0.16):
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    s = size
    tri1 = [(x, y), (x - s * ux + s * 0.75 * px, y - s * uy + s * 0.75 * py),
            (x - s * ux - s * 0.75 * px, y - s * uy - s * 0.75 * py)]
    tri2 = [(x, y), (x + s * ux + s * 0.75 * px, y + s * uy + s * 0.75 * py),
            (x + s * ux - s * 0.75 * px, y + s * uy - s * 0.75 * py)]
    for tri in (tri1, tri2):
        ax.add_patch(plt.Polygon(tri, closed=True, facecolor="white", edgecolor="black",
                                 linewidth=0.8, zorder=5))


def flow(ax, start, end, label=None, valve=True, label_side="above", fontsize=6.8,
         shrinkA=0.0, shrinkB=0.0, double=False):
    """Thick material-flow arrow start to end with a bowtie valve at its midpoint."""
    (x1, y1), (x2, y2) = start, end
    ax.annotate("", xy=end, xytext=start,
                arrowprops=dict(arrowstyle="-|>", linewidth=1.6, color="black",
                                shrinkA=shrinkA, shrinkB=shrinkB, mutation_scale=11),
                zorder=2)
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    ang = math.degrees(math.atan2(y2 - y1, x2 - x1))
    if valve:
        _valve(ax, mx, my, ang)
    if double:
        delay_mark(ax, (mx, my), ang)
    if label:
        a = math.radians(ang)
        px, py = -math.sin(a), math.cos(a)
        off = 0.30 if label_side == "above" else -0.30
        ax.text(mx + px * off, my + py * off, label, ha="center", va="center",
                fontsize=fontsize, zorder=6)
    return (mx, my)


def auxiliary(ax, x, y, label, r=R_AUX, fontsize=6.8, dashed=False):
    """Circle node for an auxiliary or parameter."""
    ax.add_patch(Circle((x, y), r, facecolor="white", edgecolor="black", linewidth=0.9,
                        linestyle=(0, (2.5, 1.5)) if dashed else "solid", zorder=3))
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize, zorder=4)
    return (x, y)


def text_node(ax, x, y, label, fontsize=7.0, style=None):
    """A bare variable name, the causal-loop-diagram convention."""
    ax.text(x, y, label, ha="center", va="center", fontsize=fontsize, style=style, zorder=4)
    return (x, y)


def link(ax, a, b, polarity="+", curve=0.25, delay=False, label=None, shrinkA=13.5,
         shrinkB=13.5, fontsize=6.6, linestyle="solid", lw=0.85, sign_pos=0.42,
         sign_side=None):
    """Thin causal arrow a to b, arc, with a '+' or '-' set beside the arrow head.

    sign_pos moves the polarity sign back along the arrow, away from the head, and
    sign_side moves it further out from the arc. Both exist for the crowded diagrams
    where the default lands the sign on a neighbouring label.
    """
    ax.annotate("", xy=b, xytext=a,
                arrowprops=dict(arrowstyle="-|>", linewidth=lw, color="black",
                                connectionstyle=f"arc3,rad={curve}", shrinkA=shrinkA,
                                shrinkB=shrinkB, mutation_scale=8, linestyle=linestyle),
                zorder=2)
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    n = math.hypot(dx, dy) or 1.0
    # arc3 puts its control point at midpoint + rad * (dy, -dx); the drawn arc passes about
    # halfway to it, so the outside of the bend is this perpendicular.
    px, py = dy / n, -dx / n
    mx, my = (x1 + x2) / 2 + px * curve * n / 2, (y1 + y2) / 2 + py * curve * n / 2
    if polarity:
        # near the head, offset to the outside of the arc
        side = 0.2 + curve * 0.5 if sign_side is None else sign_side
        hx = x2 - dx / n * sign_pos + px * side
        hy = y2 - dy / n * sign_pos + py * side
        ax.text(hx, hy, polarity, ha="center", va="center", fontsize=fontsize + 1.2, zorder=6)
    if delay:
        ang = math.degrees(math.atan2(dy, dx))
        delay_mark(ax, (mx, my), ang)
    if label:
        ax.text(mx + px * 0.25, my + py * 0.25, label, ha="center", va="center",
                fontsize=fontsize, style="italic", zorder=6)
    return (mx, my)


def delay_mark(ax, p, angle_deg, size=0.14, gap=0.07):
    """Two short parallel bars crossing an arrow at point p."""
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    px, py = -uy, ux
    x, y = p
    for s in (-gap / 2, gap / 2):
        cx, cy = x + ux * s, y + uy * s
        ax.plot([cx - px * size, cx + px * size], [cy - py * size, cy + py * size],
                color="black", linewidth=0.9, zorder=6, solid_capstyle="butt")


def loop_id(ax, x, y, name, direction="cw", r=0.30, fontsize=7.0):
    """Loop identifier: a partial ring with an arrow head and R or B at its centre."""
    from matplotlib.patches import Arc
    t1, t2 = (200, 520) if direction == "cw" else (20, 340)
    ax.add_patch(Arc((x, y), 2 * r, 2 * r, theta1=t1 % 360, theta2=t2 % 360, color="black",
                     linewidth=0.7, zorder=3))
    # arrow head at the end of the arc
    end = math.radians(t2 if direction == "cw" else t2)
    ex, ey = x + r * math.cos(end), y + r * math.sin(end)
    sgn = -1 if direction == "cw" else 1
    tx, ty = -math.sin(end) * sgn, math.cos(end) * sgn
    ax.annotate("", xy=(ex + tx * 0.02, ey + ty * 0.02), xytext=(ex - tx * 0.10, ey - ty * 0.10),
                arrowprops=dict(arrowstyle="-|>", linewidth=0.7, color="black", mutation_scale=6),
                zorder=3)
    ax.text(x, y, name, ha="center", va="center", fontsize=fontsize, zorder=4)
    return (x, y)


def boundary(ax, x0, y0, x1, y1, label, fontsize=6.6):
    """Dashed rectangle marking a model boundary, with an italic corner label."""
    ax.add_patch(FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0.02",
                                facecolor="none", edgecolor="black", linewidth=0.7,
                                linestyle=(0, (3.0, 2.0)), zorder=1))
    ax.text(x0 + 0.08, y1 - 0.10, label, ha="left", va="top", fontsize=fontsize, style="italic",
            zorder=4)


def offset_points(a, b, delta):
    """Shift segment a to b perpendicular by delta (axis units)."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    n = (dx ** 2 + dy ** 2) ** 0.5
    px, py = -dy / n * delta, dx / n * delta
    return (x1 + px, y1 + py), (x2 + px, y2 + py)


def legend_rows(ax, rows, x, y, dy=0.30, fontsize=6.6, sample=0.55):
    """Manually drawn legend. rows is a list of (linestyle, text)."""
    for i, (ls, text) in enumerate(rows):
        yy = y - i * dy
        ax.plot([x, x + sample], [yy, yy], color="black", linewidth=1.0, linestyle=ls)
        ax.text(x + sample + 0.15, yy, text, ha="left", va="center", fontsize=fontsize)
