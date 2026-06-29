"""Viz 2: Group → Knockout Sankey.

Two columns of nodes: left = the 12 groups (A–L), right = (Winner | Runner-up
| Best 3rd | Eliminated). Ribbons go from each group to whichever bin each of
its four teams ended up in. The ribbon thickness is uniform (one team per
ribbon) but ribbons curl in proportion to how many teams from the group
landed in each bin.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MplPath

from _common import out_paths
from data.load import group_standings, tournament_frame
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, GOLD, OUTCOME_COLORS, CONF_COLORS)


NAME = "v02_group_to_knockout_sankey"

BIN_ORDER = ["Group winner", "Runner-up", "Best 3rd", "Eliminated"]
BIN_COLORS = {
    "Group winner": "#0F8A5F",
    "Runner-up": "#5C8DAF",
    "Best 3rd": GOLD,
    "Eliminated": "#B8312D",
}


def _classify():
    tf = tournament_frame()
    gs = group_standings()
    r32 = tf[tf.stage_name == "Round of 32"]
    adv_ids = set(r32.home_team_id) | set(r32.away_team_id)
    rows = []
    for _, r in gs.iterrows():
        if r.rank_in_group == 1:
            b = "Group winner"
        elif r.rank_in_group == 2:
            b = "Runner-up"
        elif r.team_id in adv_ids:
            b = "Best 3rd"
        else:
            b = "Eliminated"
        rows.append((r.group, r.team_name, r.conf, r.rank_in_group,
                     r.pts, r.gd, b))
    import pandas as pd
    return pd.DataFrame(rows, columns=["group", "team", "conf", "rank",
                                        "pts", "gd", "bin"])


def render():
    apply_style()
    df = _classify()
    groups = sorted(df.group.unique())

    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    # Layout
    LX, RX = 0.13, 0.78          # bin columns
    NODE_W = 0.045
    TOP, BOT = 0.92, 0.10
    GROUP_GAP = 0.012
    BIN_GAP = 0.025

    # Y bands for groups (left column): 12 groups stacked
    n_groups = len(groups)
    total_h = TOP - BOT
    group_h = (total_h - GROUP_GAP * (n_groups - 1)) / n_groups
    group_y = {}
    for i, g in enumerate(groups):
        y_top = TOP - i * (group_h + GROUP_GAP)
        group_y[g] = (y_top - group_h, y_top)

    # Y bands for bins (right column): proportional to count
    bin_counts = df["bin"].value_counts().reindex(BIN_ORDER).fillna(0)
    n_total = bin_counts.sum()
    total_bin_h = TOP - BOT - BIN_GAP * (len(BIN_ORDER) - 1)
    bin_y = {}
    cursor = TOP
    for b in BIN_ORDER:
        h = total_bin_h * bin_counts[b] / n_total
        bin_y[b] = (cursor - h, cursor)
        cursor -= h + BIN_GAP

    # Sub-slots inside each group node (4 teams) and each bin (its count).
    # Each team is one unit ribbon. Compute its left source y and right tgt y.
    # Order groups by rank in group; order within bins by group letter so it's
    # legible.
    df_sorted = df.sort_values(["group", "rank"]).reset_index(drop=True)
    # Source y per (group, rank)
    src_y = {}
    for g in groups:
        y0, y1 = group_y[g]
        slot = (y1 - y0) / 4
        for k in range(4):
            src_y[(g, k + 1)] = y1 - (k + 0.5) * slot
    # Target y per (bin, team) — sort by group letter
    bin_assignments = {b: [] for b in BIN_ORDER}
    for _, r in df_sorted.iterrows():
        bin_assignments[r["bin"]].append((r.group, r["rank"], r.team))
    tgt_y = {}
    for b, items in bin_assignments.items():
        items.sort(key=lambda x: (x[0], x[1]))
        y0, y1 = bin_y[b]
        slot = (y1 - y0) / max(len(items), 1)
        for i, (g, k, team) in enumerate(items):
            tgt_y[(g, k, b)] = y1 - (i + 0.5) * slot

    # Draw group nodes (left) — wider node holds team names inside
    NAME_X0 = LX - 0.10  # left edge of name area
    NAME_W = 0.10        # width of name strip
    for g in groups:
        y0, y1 = group_y[g]
        # Name strip (light background to keep ribbon area clean)
        ax.add_patch(plt.Rectangle((NAME_X0, y0), NAME_W, y1 - y0,
                                    facecolor="#F1ECE2", edgecolor="none"))
        # Group block (dark)
        ax.add_patch(plt.Rectangle((LX, y0), NODE_W, y1 - y0,
                                    facecolor=INK, edgecolor="none", alpha=0.92))
        ax.text(LX + NODE_W / 2, (y0 + y1) / 2, g,
                ha="center", va="center", color="white",
                fontsize=11, fontweight="bold")
        # Per-team labels in the name strip
        sub = df_sorted[df_sorted.group == g]
        slot = (y1 - y0) / 4
        for k, (_, r) in enumerate(sub.iterrows()):
            cy = y1 - (k + 0.5) * slot
            ax.text(NAME_X0 + NAME_W - 0.006, cy, r.team,
                    ha="right", va="center", color=INK, fontsize=8)

    # Draw bin nodes (right)
    for b in BIN_ORDER:
        y0, y1 = bin_y[b]
        ax.add_patch(plt.Rectangle((RX, y0), NODE_W, y1 - y0,
                                    facecolor=BIN_COLORS[b],
                                    edgecolor="none", alpha=0.95))
        ax.text(RX + NODE_W + 0.012, (y0 + y1) / 2,
                f"{b}\n{int(bin_counts[b])} teams",
                ha="left", va="center", color=INK,
                fontsize=12, fontweight="bold")

    # Draw ribbons
    for _, r in df_sorted.iterrows():
        sy = src_y[(r.group, r["rank"])]
        ty = tgt_y[(r.group, r["rank"], r["bin"])]
        x0 = LX + NODE_W
        x1 = RX
        # Cubic bezier with horizontal control
        verts = [
            (x0, sy + 0.006),
            (x0 + (x1 - x0) * 0.45, sy + 0.006),
            (x1 - (x1 - x0) * 0.45, ty + 0.006),
            (x1, ty + 0.006),
            (x1, ty - 0.006),
            (x1 - (x1 - x0) * 0.45, ty - 0.006),
            (x0 + (x1 - x0) * 0.45, sy - 0.006),
            (x0, sy - 0.006),
            (x0, sy + 0.006),
        ]
        codes = [MplPath.MOVETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
                 MplPath.LINETO, MplPath.CURVE4, MplPath.CURVE4, MplPath.CURVE4,
                 MplPath.CLOSEPOLY]
        path = MplPath(verts, codes)
        color = BIN_COLORS[r["bin"]]
        ax.add_patch(PathPatch(path, facecolor=color, edgecolor="none",
                                alpha=0.55))

    title_block(
        fig,
        "From 12 groups to 32 — how the WC-2026 field made the knockouts.",
        "Each thin ribbon is one of 48 teams flowing from its group (left) to its "
        "knockout fate (right). Eight 3rd-placed sides survived; four did not.",
        y=0.97, x=0.05,
    )

    # Caption strip on what 3rd-place rule produced
    third_in = df[df["bin"] == "Best 3rd"]["team"].tolist()
    third_out = df[(df["bin"] == "Eliminated") & (df["rank"] == 3)]["team"].tolist()
    ax.text(0.05, 0.05,
            "Saved 3rd-placed: " + ", ".join(third_in) + ".\n"
            "Cut at the line: " + ", ".join(third_out) + ".",
            ha="left", va="top", color=INK_SOFT, fontsize=9.5,
            transform=fig.transFigure)

    credit(fig)

    p, sp = out_paths(NAME)
    fig.savefig(p)
    fig.savefig(sp)
    plt.close(fig)
    return p, sp


if __name__ == "__main__":
    p, sp = render()
    print("wrote", p, sp)
