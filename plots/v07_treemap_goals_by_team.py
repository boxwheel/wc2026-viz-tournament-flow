"""Viz 7: Treemap of group-stage goals by confederation → team.

Two-level treemap: outer = confederation (color), inner = team (text + count).
Sized by goals scored. Anchors the macro story: who scored the goals.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import squarify

from _common import out_paths
from data.load import group_standings, teams
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, CONF_COLORS)


NAME = "v07_treemap_goals_by_team"


def render():
    apply_style()
    s = group_standings()
    t = teams()[["team_id", "confederation"]]
    df = s.merge(t, on="team_id", how="left").rename(columns={"conf": "conf_drop"})
    df = df[df.gf > 0].copy()
    df = df.sort_values(["confederation", "gf"], ascending=[True, False])

    fig, ax = plt.subplots(figsize=(16, 11))

    norm = plt.Normalize(0, 1)
    # Treemap on a 100x60 canvas
    canvas_w, canvas_h = 100, 62
    # First: partition canvas across confederations (sized by total goals per conf)
    conf_totals = df.groupby("confederation").gf.sum().sort_values(ascending=False)
    conf_rects = squarify.squarify(
        squarify.normalize_sizes(conf_totals.values, canvas_w, canvas_h),
        0, 0, canvas_w, canvas_h)

    # Then inside each conf, place teams
    for (conf, total), r in zip(conf_totals.items(), conf_rects):
        sub = df[df.confederation == conf].sort_values("gf", ascending=False)
        team_rects = squarify.squarify(
            squarify.normalize_sizes(sub.gf.values, r["dx"], r["dy"]),
            r["x"], r["y"], r["dx"], r["dy"])

        # Conf outer color
        c_outer = CONF_COLORS.get(conf, "#999")

        for trec, (_, row) in zip(team_rects, sub.iterrows()):
            x, y, dx, dy = trec["x"], trec["y"], trec["dx"], trec["dy"]
            # Slight inset for clean edges
            inset = 0.25
            ax.add_patch(plt.Rectangle((x + inset, y + inset),
                                        max(0, dx - 2 * inset),
                                        max(0, dy - 2 * inset),
                                        facecolor=c_outer,
                                        alpha=0.20 + 0.75 * (row.gf / df.gf.max()),
                                        edgecolor="white",
                                        linewidth=1.0))
            # Team label if there's room
            if dx > 5 and dy > 3:
                label = row.team_name
                if dx < 9:
                    label = label.split()[0][:9]
                fs = max(6, min(15, int(dy * 0.9)))
                ax.text(x + dx / 2, y + dy / 2 + 0.5, label,
                        ha="center", va="center", color="white",
                        fontsize=min(fs, 14), fontweight="bold")
                ax.text(x + dx / 2, y + dy / 2 - max(1.5, dy*0.18), f"{int(row.gf)}",
                        ha="center", va="center", color="white",
                        fontsize=min(fs - 2, 11))

        # Conf banner: label on top edge of conf block
        ax.text(r["x"] + 0.5, r["y"] + r["dy"] - 0.5,
                f"{conf}  ·  {int(total)} goals",
                ha="left", va="top", color=c_outer,
                fontsize=11, fontweight="bold",
                path_effects=None,
                bbox=dict(boxstyle="round,pad=0.3",
                          facecolor="white", edgecolor="none", alpha=0.85))

    ax.set_xlim(0, canvas_w)
    ax.set_ylim(0, canvas_h)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.invert_yaxis()  # so larger tiles read top-down

    # Footer stat
    n_scoring = (s.gf > 0).sum()
    n_total = len(s)
    n_silent = n_total - n_scoring
    silent_teams = ", ".join(s[s.gf == 0].team_name.tolist())
    ax.text(0.005, -0.03,
            f"{n_total} teams in the group stage  •  {n_silent} scored zero  "
            f"({silent_teams or 'none'})",
            transform=ax.transAxes, ha="left", va="top",
            color=INK_SOFT, fontsize=9.5)

    title_block(
        fig,
        "Who scored the WC-2026 group-stage goals? A confederation treemap.",
        "Tile area = goals scored in the group stage. Outer color = confederation. "
        "Read it left-to-right by confederation power and top-to-bottom by team.",
        x=0.05, y=0.97,
    )
    credit(fig)

    p, sp = out_paths(NAME)
    fig.savefig(p)
    fig.savefig(sp)
    plt.close(fig)
    return p, sp


if __name__ == "__main__":
    p, sp = render()
    print("wrote", p, sp)
