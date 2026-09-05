#!/usr/bin/env python3
"""Chapter 40, "The repository": the model document, runtime, scenario log, and who may touch each.

The chapter lays out the service-operation repository, in which every directory corresponds to
a chapter, and then states the authority boundary: agents call tools, not code, and the tool
layer refuses approve_patch and execute_pilot instead of relying on instruction. The roles that
run against it are the five from Part V (interviewer, compiler, critic, experiment designer,
policy searcher), each with a human gate. This figure draws the model document, the evidence
folder, the runtime, and the scenario log, and the stage of access each role has to each, taken
from the chapter's tool table: read, simulate, propose, and the two human-only stages.

    uv run --group figures python build/figures/fig_repository_structure.py

No numeric data. Placement is a layout choice; the artifacts, roles, and stages are the
chapter's. Where the chapter's tool table does not name a role, the cell is left blank.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from figstyle import figure, save  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from sdvocab import boundary, stock  # noqa: E402

ARTIFACTS = [
    ("model document", "model/"),
    ("evidence, ledger", "evidence/"),
    ("runtime", "run_scenario"),
    ("scenario log", "scenarios/"),
]
# The permissions drawn here are the pack's, not a drawing decision.
from chapters.chapter_31_repository.code.permissions import GRANTS  # noqa: E402

ROLES = ["interviewer", "compiler", "critic", "experiment\ndesigner", "policy\nsearcher",
         "human\nreviewer"]
# stage per (role, artifact): r read, s simulate, p propose, A approve, X execute
CELLS = {
    ("interviewer", "evidence, ledger"): "read",
    ("compiler", "model document"): "propose",
    ("compiler", "evidence, ledger"): "read",
    ("critic", "model document"): "read",
    ("critic", "runtime"): "simulate",
    ("critic", "scenario log"): "read",
    ("experiment\ndesigner", "evidence, ledger"): "read",
    ("experiment\ndesigner", "runtime"): "simulate",
    ("experiment\ndesigner", "scenario log"): "propose",
    ("policy\nsearcher", "model document"): "read",
    ("policy\nsearcher", "runtime"): "simulate",
    ("policy\nsearcher", "scenario log"): "read",
    ("human\nreviewer", "model document"): "approve",
    ("human\nreviewer", "scenario log"): "execute\npilot",
}


def main():
    for (role, artifact), stage in CELLS.items():
        key = role.replace("\n", "_")
        if key == "human_reviewer":
            continue
        assert stage in GRANTS[key], (role, artifact, stage, GRANTS[key])

    fig, ax = figure(height_in=3.1)
    ax.set_xlim(-0.1, 9.9)
    ax.set_ylim(-0.75, 5.1)
    ax.set_aspect("equal")
    ax.axis("off")

    x0, cw, y0, rh = 2.6, 1.8, 3.6, 0.62
    for j, (name, sub) in enumerate(ARTIFACTS):
        cx = x0 + j * cw + cw / 2
        stock(ax, cx, 4.5, name, w=cw - 0.15, h=0.8, sublabel=sub, fontsize=6.4)
    for i, role in enumerate(ROLES):
        cy = y0 - i * rh - rh / 2
        ax.text(x0 - 0.15, cy, role, ha="right", va="center", fontsize=6.6)
        for j, (name, _) in enumerate(ARTIFACTS):
            cx = x0 + j * cw + cw / 2
            ax.add_patch(Rectangle((x0 + j * cw, cy - rh / 2), cw, rh, facecolor="white",
                                   edgecolor="black", linewidth=0.4, zorder=1))
            stage = CELLS.get((role, name))
            if stage:
                bold = stage in ("approve", "execute\npilot")
                ax.text(cx, cy, stage, ha="center", va="center", fontsize=6.4,
                        weight="bold" if bold else "normal", zorder=4)
    boundary(ax, x0 - 1.55, y0 - 6 * rh - 0.06, x0 + 4 * cw + 0.06, y0 - 5 * rh + 0.02, "")
    ax.text(x0 - 0.15, y0 + 0.12, "role", ha="right", va="bottom", fontsize=6.6, style="italic")
    ax.text(x0 + 2 * cw, y0 - 6 * rh - 0.22,
            "read, simulate, propose are agent stages; approve and execute are human gates,\n"
            "and the tool layer refuses them to agents instead of instructing",
            ha="center", va="top", fontsize=6.2, style="italic")

    fig.tight_layout()
    save(fig, "repository-structure")


if __name__ == "__main__":
    main()
