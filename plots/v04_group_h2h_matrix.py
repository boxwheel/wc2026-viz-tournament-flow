"""Viz 4: Group head-to-head matrices — 12 mini-grids of every group match.

For each of the 12 groups, a 4x4 matrix: rows = home team, cols = away team,
each cell shows the score of the match between them, colored by the home
team's goal difference (diverging vlag). Diagonal blanked.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import tournament_frame, group_standings
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, DIV_CMAP, GOLD)


NAME = "v04_group_h2h_matrix"


def render():
    apply_style()
    tf = tournament_frame()
    gs = group_standings()
    groups = sorted(tf.home_group_letter.dropna().unique())

    fig, axes = plt.subplots(3, 4, figsize=(18, 17),
                              gridspec_kw=dict(hspace=0.85, wspace=0.45,
                                                top=0.86, bottom=0.07,
                                                left=0.05, right=0.96))
    axes = axes.flatten()

    # Shared color scale anchored at 0
    vmax = 5
    norm = mcolors.TwoSlopeNorm(vmin=-vmax, vcenter=0, vmax=vmax)
    cmap = plt.get_cmap(DIV_CMAP)

    for ax, g in zip(axes, groups):
        teams_in_g = gs[gs.group == g].sort_values("rank_in_group")
        team_order = teams_in_g.team_name.tolist()
        ids_in_g = dict(zip(teams_in_g.team_name, teams_in_g.team_id))
        n = len(team_order)
        ax.set_xlim(-0.5, n - 0.5)
        ax.set_ylim(n - 0.5, -0.5)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

        # Draw cells
        sub = tf[(tf.home_group_letter == g) & (tf.stage_name == "Group Stage")]
        score_lookup = {}
        for _, r in sub.iterrows():
            score_lookup[(r.home_team_name, r.away_team_name)] = (
                int(r.home_score), int(r.away_score))

        for i, home in enumerate(team_order):
            for j, away in enumerate(team_order):
                if i == j:
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                                facecolor="#EEE7D8",
                                                edgecolor=RULE, linewidth=0.6))
                    continue
                if (home, away) in score_lookup:
                    hs, as_ = score_lookup[(home, away)]
                    gd = hs - as_
                    color = cmap(norm(gd))
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                                facecolor=color,
                                                edgecolor="white", linewidth=1.5))
                    txt_color = "white" if abs(gd) >= 3 else INK
                    ax.text(j, i, f"{hs}–{as_}", ha="center",
                            va="center", color=txt_color, fontsize=11,
                            fontweight="bold")
                else:
                    ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1,
                                                facecolor="#F8F4EC",
                                                edgecolor=RULE, linewidth=0.6))

        # Row labels (left) + column labels (top), abbreviated
        for idx, t in enumerate(team_order):
            short = (t[:9] + "…") if len(t) > 10 else t
            ax.text(-0.65, idx, short, ha="right", va="center",
                    fontsize=8.5, color=INK)
            ax.text(idx, -0.65, short, ha="center", va="bottom",
                    fontsize=8.5, color=INK, rotation=30)

        # Rank pin: small gold dot for top-2
        for idx, (_, r) in enumerate(teams_in_g.iterrows()):
            color = GOLD if r.rank_in_group <= 2 else INK_SOFT
            ax.scatter(-1.25, idx, s=70, color=color, zorder=3)
            ax.text(-1.25, idx, f"{int(r.rank_in_group)}",
                    ha="center", va="center_baseline",
                    color="white", fontsize=7, fontweight="bold", zorder=4)

        ax.text(-1.7, -2.0, f"Group {g}", ha="left", va="bottom",
                fontsize=13, fontweight="bold", color=INK)

    # Colorbar manual
    cax = fig.add_axes([0.36, 0.05, 0.3, 0.012])
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, color=INK_SOFT)
    cb.set_ticks([-vmax, -2, 0, 2, vmax])
    cb.set_ticklabels([f"−{vmax}", "−2", "0", "+2", f"+{vmax}"])
    cax.set_title("Goal difference: row team home minus away",
                  fontsize=9, color=INK_SOFT, pad=8)

    title_block(
        fig,
        "Every group, every game — a 4×4 head-to-head heatmap per group.",
        "Each cell holds the actual scoreline. Color is the home team's goal "
        "difference (blue = won big; red = lost big). Diagonals are blanks.",
        y=0.985,
    )
    credit(fig, y=0.005)

    p, sp = out_paths(NAME)
    fig.savefig(p)
    fig.savefig(sp)
    plt.close(fig)
    return p, sp


if __name__ == "__main__":
    p, sp = render()
    print("wrote", p, sp)
