"""Viz 8: Possession × xG per team-match — does the ball win matches?

Scatter of every team-performance in the group stage:
  X = possession %
  Y = xG generated
  color = match outcome (W/D/L) for that team
  size = goals actually scored

The point: high-possession teams don't always win, and chalk wins don't always
look like dominance on xG.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import tournament_frame, team_stats, teams
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, OUTCOME_COLORS, GOLD)


NAME = "v08_possession_vs_xg"


def render():
    apply_style()
    tf = tournament_frame()
    ts = team_stats()
    tlk = teams()[["team_id", "team_name"]]

    g = tf[(tf.stage_name == "Group Stage") & tf.completed].copy()

    # Build long form: one row per (match, team) with xg, possession, goals, outcome
    rows = []
    for _, r in g.iterrows():
        for side in ("home", "away"):
            tid = r[f"{side}_team_id"]
            tname = r[f"{side}_team_name"]
            xg = r[f"{side}_xg"]
            gf = r[f"{side}_score"]
            ga = r[f"{'away' if side=='home' else 'home'}_score"]
            outcome = "win" if gf > ga else "loss" if gf < ga else "draw"
            rows.append(dict(match_id=r.match_id, team_id=tid,
                             team_name=tname, xg=xg, gf=gf, ga=ga,
                             outcome=outcome))
    long = pd.DataFrame(rows)
    long = long.merge(ts[["match_id", "team_id", "possession_pct"]],
                      on=["match_id", "team_id"], how="left")
    long = long.dropna(subset=["possession_pct", "xg"])

    fig, ax = plt.subplots(figsize=(14.5, 10.5))

    # Reference lines
    ax.axvline(50, color=INK, linewidth=0.6, alpha=0.4, linestyle="--")
    ax.axhline(long.xg.median(), color=INK, linewidth=0.6, alpha=0.4,
                linestyle="--")
    ax.text(50.5, long.xg.max() + 0.2, "even possession",
            color=INK_SOFT, fontsize=9, va="top")
    ax.text(long.possession_pct.max() + 0.5, long.xg.median(),
            f"median xG ({long.xg.median():.2f})",
            color=INK_SOFT, fontsize=9, va="center")

    for outcome, color in OUTCOME_COLORS.items():
        sub = long[long.outcome == outcome]
        sizes = 80 + 80 * sub.gf
        ax.scatter(sub.possession_pct, sub.xg,
                   color=color, s=sizes, alpha=0.55,
                   edgecolor="white", linewidth=0.9,
                   label=f"{outcome.capitalize()} ({len(sub)})")

    # Highlight: high-poss but lost; high xg but lost; low-poss but won
    high_poss_lost = long[(long.possession_pct > 60) & (long.outcome == "loss")]
    low_poss_won = long[(long.possession_pct < 40) & (long.outcome == "win")]
    high_xg_lost = long[(long.xg > long.xg.quantile(0.85)) & (long.outcome == "loss")]

    interesting = pd.concat([high_poss_lost, low_poss_won, high_xg_lost]).drop_duplicates()
    for _, r in interesting.iterrows():
        ax.annotate(r.team_name, (r.possession_pct, r.xg),
                    xytext=(6, 6), textcoords="offset points",
                    fontsize=8.5, color=INK,
                    bbox=dict(boxstyle="round,pad=0.2",
                              facecolor="white", edgecolor=RULE, alpha=0.85))

    # Anti-diagonal "trend" smoothing visualization: linear fit on means per 5% bins
    bins = np.arange(20, 86, 5)
    avg = long.groupby(pd.cut(long.possession_pct, bins=bins))["xg"].mean()
    centers = (bins[:-1] + bins[1:]) / 2
    valid = avg.dropna()
    if len(valid) > 1:
        ax.plot(centers[:len(valid)], valid.values, color=GOLD,
                linewidth=2, alpha=0.7, label="binned mean xG (5% poss bins)")

    ax.set_xlabel("Ball possession (%)")
    ax.set_ylabel("Expected goals (xG)")
    ax.set_xlim(15, 85)
    ax.grid(True, alpha=0.18)
    ax.legend(loc="upper left", fontsize=10, frameon=True, framealpha=0.85)

    title_block(
        fig,
        "Possession isn't a verdict — WC-2026 group-stage xG vs ball-share.",
        "Each dot = one team's performance in one match (144 team-matches). "
        "Dot size = actual goals. Labels = the side that had >60% possession "
        "and lost, or <40% and won.",
        x=0.06, y=0.97,
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
