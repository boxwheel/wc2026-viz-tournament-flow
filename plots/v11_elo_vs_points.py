"""Viz 11: Pre-tournament Elo vs group-stage points.

Each of 48 teams plotted as a dot: x = Elo, y = group-stage points.
Diagonal regression line traces the expectation; teams far above or below
their line get labeled (over- and under-performers).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import group_standings, teams
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, GOLD, CONF_COLORS)


NAME = "v11_elo_vs_points"


def render():
    apply_style()
    gs = group_standings()
    t = teams()[["team_id", "elo_rating", "fifa_ranking_pre_tournament",
                 "confederation"]]
    df = gs.merge(t, on="team_id")

    # Linear fit (least squares) -> residuals
    A = np.vstack([df.elo_rating, np.ones(len(df))]).T
    slope, intercept = np.linalg.lstsq(A, df.pts, rcond=None)[0]
    df["expected_pts"] = slope * df.elo_rating + intercept
    df["resid"] = df.pts - df.expected_pts

    fig, ax = plt.subplots(figsize=(14.5, 10.5))

    xs = np.linspace(df.elo_rating.min() - 30, df.elo_rating.max() + 30, 100)
    ax.plot(xs, slope * xs + intercept, color=INK, linewidth=1,
            linestyle="--", alpha=0.6,
            label=f"Linear fit: pts ≈ {slope:.4f}·Elo + {intercept:.1f}")

    # Per-confederation dots
    for conf in df.confederation.unique():
        sub = df[df.confederation == conf]
        ax.scatter(sub.elo_rating, sub.pts, s=130,
                    color=CONF_COLORS.get(conf, "#888"),
                    alpha=0.78, edgecolor="white", linewidth=1.2,
                    label=conf)

    # Label top over- and under-performers
    overs = df.nlargest(6, "resid")
    unders = df.nsmallest(6, "resid")
    for _, r in pd.concat([overs, unders]).iterrows():
        sign = "+" if r.resid > 0 else ""
        ax.annotate(f"{r.team_name} ({sign}{r.resid:.1f})",
                    (r.elo_rating, r.pts),
                    xytext=(8, 6 if r.resid > 0 else -10),
                    textcoords="offset points",
                    fontsize=9, color=INK,
                    bbox=dict(boxstyle="round,pad=0.2",
                              facecolor="white",
                              edgecolor=GOLD if r.resid > 0 else "#C8102E",
                              alpha=0.95))

    ax.set_xlabel("Pre-tournament Elo rating")
    ax.set_ylabel("Group-stage points (out of 9)")
    ax.set_yticks(range(0, 10))
    ax.grid(True, alpha=0.20)
    ax.legend(loc="lower right", fontsize=9, framealpha=0.85, ncol=2)

    title_block(
        fig,
        "Did the WC-2026 group stage agree with Elo?",
        f"Each dot is a team's pre-tournament Elo vs the group-stage points it "
        f"actually scored. Dashed line = least-squares fit (slope {slope:.4f} "
        "pts per Elo point). Labels are the six biggest over- and underperformers.",
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
