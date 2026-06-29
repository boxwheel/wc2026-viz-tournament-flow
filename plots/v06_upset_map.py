"""Viz 6: Upset map — Elo gap vs goal difference for every group match.

A scatter of 72 group-stage matches:
- X = pre-tournament Elo difference (home minus away)
- Y = actual goal difference (home minus away)

Quadrants make the meaning intuitive. The few outright upsets (where the
underdog won) get team labels; draws and chalk wins are dimmer.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import tournament_frame
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, GOLD, OUTCOME_COLORS)


NAME = "v06_upset_map"


def render():
    apply_style()
    tf = tournament_frame()
    g = tf[(tf.stage_name == "Group Stage") & tf.completed].copy()
    g["elo_diff"] = g["home_elo_rating"] - g["away_elo_rating"]
    g["gd"] = g["home_score"] - g["away_score"]
    # Outright upset: signs opposite, Elo gap meaningful, gd nonzero
    g["upset"] = ((np.sign(g["elo_diff"]) != np.sign(g["gd"])) &
                  (g["gd"] != 0) & (np.abs(g["elo_diff"]) > 50))
    g["draw"] = g["gd"] == 0

    fig, ax = plt.subplots(figsize=(15, 11))

    xlim = (max(abs(g["elo_diff"].min()), abs(g["elo_diff"].max())) + 30)
    ylim = max(abs(g["gd"].min()), abs(g["gd"].max())) + 1
    xlim = round(xlim / 50) * 50 + 50

    # Quadrant shading
    ax.axvspan(-xlim, 0, ymin=0.5, ymax=1.0, facecolor=GOLD, alpha=0.07,
                zorder=0)
    ax.axvspan(0, xlim, ymin=0, ymax=0.5, facecolor=GOLD, alpha=0.07,
                zorder=0)
    ax.axhline(0, color=INK, linewidth=0.7, alpha=0.5)
    ax.axvline(0, color=INK, linewidth=0.7, alpha=0.5)

    # Soft expectation diagonal
    xs = np.linspace(-xlim, xlim, 100)
    ax.plot(xs, xs / 80, color=INK_SOFT, linestyle=":", linewidth=1,
            label="rough expectation: 80 Elo ≈ 1 goal")

    # Dim chalk + draws
    chalk = g[~g.upset & ~g.draw]
    draws = g[g.draw]
    upsets = g[g.upset]

    ax.scatter(chalk.elo_diff, chalk.gd, s=110, color=OUTCOME_COLORS["win"],
                alpha=0.30, edgecolor="white", linewidth=0.8,
                label=f"Chalk result ({len(chalk)})")
    ax.scatter(draws.elo_diff, draws.gd, s=110, color=OUTCOME_COLORS["draw"],
                alpha=0.55, edgecolor="white", linewidth=0.8,
                label=f"Draw ({len(draws)})")
    ax.scatter(upsets.elo_diff, upsets.gd, s=220,
                color=GOLD, alpha=0.95, edgecolor="white", linewidth=1.5,
                label=f"Outright upset ({len(upsets)})", zorder=5)

    # Label upsets
    used_labels = []
    upsets_sorted = upsets.assign(absx=np.abs(upsets.elo_diff)).sort_values("absx", ascending=False)
    for _, r in upsets_sorted.iterrows():
        winner = r.home_team_name if r.gd > 0 else r.away_team_name
        loser = r.away_team_name if r.gd > 0 else r.home_team_name
        score = (f"{int(r.home_score)}–{int(r.away_score)}"
                 if r.gd > 0 else f"{int(r.away_score)}–{int(r.home_score)}")
        label = f"{winner} {score} {loser}"
        # Place label outside dot
        side = "left" if r.elo_diff < 0 else "right"
        dx = 40 if side == "left" else -40
        dy = 0.6 if r.gd > 0 else -0.6
        # avoid overlapping by stacking vertically if needed
        for prev in used_labels:
            if abs(prev[0] - (r.elo_diff + dx)) < 200 and abs(prev[1] - (r.gd + dy)) < 0.5:
                dy += 0.6 if dy > 0 else -0.6
        used_labels.append((r.elo_diff + dx, r.gd + dy))
        ax.annotate(label, (r.elo_diff, r.gd),
                    xytext=(r.elo_diff + dx, r.gd + dy),
                    fontsize=10, ha=side, va="center", color=INK,
                    fontweight="bold",
                    arrowprops=dict(arrowstyle="-", color=INK, linewidth=0.7))

    ax.set_xlim(-xlim, xlim)
    ax.set_ylim(-ylim, ylim)
    ax.set_xlabel("Pre-tournament Elo difference  (home minus away)")
    ax.set_ylabel("Actual goal difference  (home minus away)")
    ax.grid(True, alpha=0.18)

    # Corner mood labels
    ax.text(-xlim + 30, ylim - 0.4, "↖  Underdog (home) WON  —  UPSET",
            ha="left", va="top", color=GOLD, fontsize=11, fontweight="bold")
    ax.text(xlim - 30, -ylim + 0.4, "↘  Underdog (away) WON  —  UPSET",
            ha="right", va="bottom", color=GOLD, fontsize=11, fontweight="bold")
    ax.text(xlim - 30, ylim - 0.4, "↗  Favorite (home) won  —  chalk",
            ha="right", va="top", color=INK_SOFT, fontsize=10, style="italic")
    ax.text(-xlim + 30, -ylim + 0.4, "↙  Favorite (away) won  —  chalk",
            ha="left", va="bottom", color=INK_SOFT, fontsize=10, style="italic")

    ax.legend(loc="lower right", fontsize=10, framealpha=0.9)

    n_draws = int(g["draw"].sum())
    title_block(
        fig,
        "WC-2026 group stage — the upset map.",
        f"Of {len(g)} completed group matches, only {len(upsets)} produced outright upsets "
        f"(underdog won with a meaningful Elo gap); {n_draws} ended drawn.",
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
