"""Viz 9: All 48 teams' form strips — three group matches in chronological order.

For each team in a 12×4 grid, plot a three-cell strip of W/D/L outcomes,
labeled with the opponent and scoreline. Provides a parallel view of every
team's group-stage journey, sortable by group.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import tournament_frame, group_standings
from style.house import (apply_style, credit, title_block, team_color,
                          INK, INK_SOFT, RULE, OUTCOME_COLORS, GOLD)


NAME = "v09_team_form_strips"


def _build_long():
    tf = tournament_frame()
    g = tf[(tf.stage_name == "Group Stage") & tf.completed].copy()
    rows = []
    for _, r in g.iterrows():
        for side in ("home", "away"):
            tid = r[f"{side}_team_id"]
            tname = r[f"{side}_team_name"]
            grp = r[f"{side}_group_letter"]
            opp_name = r[f"{'away' if side == 'home' else 'home'}_team_name"]
            gf = r[f"{side}_score"]
            ga = r[f"{'away' if side == 'home' else 'home'}_score"]
            outcome = "win" if gf > ga else "loss" if gf < ga else "draw"
            rows.append(dict(team_id=tid, team=tname, group=grp,
                             opp=opp_name, gf=int(gf), ga=int(ga),
                             outcome=outcome, date=r.date))
    df = pd.DataFrame(rows).sort_values(["team_id", "date"])
    df["matchday"] = df.groupby("team_id").cumcount() + 1
    return df


def render():
    apply_style()
    df = _build_long()
    gs = group_standings()[["team_id", "team_name", "group", "rank_in_group",
                              "pts", "gd"]]

    groups = sorted(df.group.unique())

    # 4 rows (teams within group) x 12 cols (groups A-L)
    fig, axes = plt.subplots(4, 12, figsize=(22, 11),
                              gridspec_kw=dict(hspace=0.65, wspace=0.30,
                                                top=0.87, bottom=0.05,
                                                left=0.03, right=0.98))

    for col, group in enumerate(groups):
        teams_in_g = gs[gs.group == group].sort_values("rank_in_group")
        for row, (_, tinfo) in enumerate(teams_in_g.iterrows()):
            ax = axes[row, col]
            sub = df[df.team_id == tinfo.team_id].sort_values("matchday")
            # Strip
            for i, (_, m) in enumerate(sub.iterrows()):
                color = OUTCOME_COLORS[m.outcome]
                ax.add_patch(plt.Rectangle((i, 0), 0.92, 1,
                                            facecolor=color, edgecolor="white",
                                            alpha=0.92))
                letter = m.outcome[0].upper()
                ax.text(i + 0.46, 0.62, letter, ha="center", va="center",
                        color="white", fontsize=14, fontweight="bold")
                ax.text(i + 0.46, 0.30,
                        f"{m.gf}–{m.ga}", ha="center", va="center",
                        color="white", fontsize=8)
                ax.text(i + 0.46, 0.10,
                        f"v {m.opp[:9]}", ha="center", va="center",
                        color="white", fontsize=6.5)

            ax.set_xlim(-0.15, 3.1)
            ax.set_ylim(-0.15, 1.55)
            ax.set_xticks([]); ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_visible(False)

            # Team name + group + pts above
            qualified = tinfo.rank_in_group <= 2 or (
                tinfo.rank_in_group == 3 and tinfo.pts >= 4
            )  # rough — 3rd-placed advance if pts>=4 (approx; use actual logic if needed)
            # use rank from group_standings, and check membership in advancers via 3rd-place logic
            dot_color = GOLD if tinfo.rank_in_group <= 2 else INK_SOFT
            ax.scatter(-0.08, 1.25, s=110, color=dot_color, zorder=3)
            ax.text(-0.08, 1.25, f"{int(tinfo.rank_in_group)}",
                    ha="center", va="center_baseline", color="white",
                    fontsize=8, fontweight="bold", zorder=4)
            ax.text(0.06, 1.25, tinfo.team_name,
                    ha="left", va="center_baseline", color=INK,
                    fontsize=10, fontweight="bold")
            ax.text(3.05, 1.25, f"{int(tinfo.pts)} pts",
                    ha="right", va="center_baseline", color=INK_SOFT,
                    fontsize=9)

            # Group label at top of column
            if row == 0:
                ax.text(1.5, 1.78, f"Group {group}",
                        ha="center", va="bottom", color=INK,
                        fontsize=14, fontweight="bold")

    title_block(
        fig,
        "WC-2026 group stage — every team's three-match arc.",
        "48 form strips, one per team. Each cell is a matchday (Win/Draw/Loss) "
        "with score and opponent. Gold dot = top-2 finisher; columns are groups A–L.",
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
