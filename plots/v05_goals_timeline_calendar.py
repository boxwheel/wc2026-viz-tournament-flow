"""Viz 5: Tournament goals calendar — every goal placed by match minute and day.

For each goal in `match_events.csv`, plot a dot at (date, minute), with color
by team confederation. The y-axis shows match minute (0–90+); the x-axis is
calendar day. Lines mark normal-time halves (45, 90). A density ribbon on the
right shows when goals tend to happen.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import events, tournament_frame, teams
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, CONF_COLORS, GOLD, PAGE_BG)


NAME = "v05_goals_timeline_calendar"


def render():
    apply_style()
    ev = events()
    tf = tournament_frame()
    t = teams()[["team_id", "confederation"]]

    # Goal events only
    goals = ev[ev.event_type.str.contains("Goal", case=False, na=False)].copy()
    goals = goals.merge(tf[["match_id", "date", "stage_name"]], on="match_id",
                        how="left")
    goals = goals.merge(t, on="team_id", how="left")
    goals["date"] = pd.to_datetime(goals["date"]).dt.date
    goals = goals[goals.minute.notna()].copy()
    goals["minute"] = goals["minute"].clip(0, 120)

    # Group goals only (R32 has 1)
    g_goals = goals[goals.stage_name == "Group Stage"].copy()

    dates = sorted(g_goals["date"].unique())
    date_to_x = {d: i for i, d in enumerate(dates)}
    g_goals["x"] = g_goals["date"].map(date_to_x) + np.random.RandomState(7).uniform(-0.3, 0.3, len(g_goals))

    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(1, 2, width_ratios=[5, 1], wspace=0.05)
    ax = fig.add_subplot(gs[0])
    ax_d = fig.add_subplot(gs[1], sharey=ax)

    # Half-time / full-time markers
    for m in (45, 90):
        ax.axhline(m, color=RULE, linewidth=0.8, linestyle="-", zorder=1)
        ax.text(-0.5, m + 0.5, f"min {m}", color=INK_SOFT, fontsize=8,
                ha="left", va="bottom")

    # Highlight 75-90 band (late goals)
    ax.axhspan(75, 95, color=GOLD, alpha=0.05, zorder=0)

    # Plot goals
    for conf, group in g_goals.groupby("confederation"):
        color = CONF_COLORS.get(conf, "#888")
        ax.scatter(group.x, group.minute, color=color, s=30, alpha=0.85,
                   edgecolors="white", linewidths=0.5, label=conf)

    ax.set_xlim(-0.6, len(dates) - 0.4)
    ax.set_ylim(96, -2)
    ax.set_xticks(range(len(dates)))
    ax.set_xticklabels([d.strftime("%b %d") for d in dates],
                       rotation=30, ha="right", fontsize=9)
    ax.set_ylabel("Match minute")
    ax.set_yticks([0, 15, 30, 45, 60, 75, 90])
    ax.grid(False)
    ax.spines["right"].set_visible(False)

    # Density panel on right
    ax_d.hist(g_goals.minute, bins=np.arange(0, 100, 5),
              orientation="horizontal", color=INK, alpha=0.7,
              edgecolor="white", linewidth=0.5)
    ax_d.set_xlabel("Goals (5-min bins)")
    ax_d.spines["left"].set_visible(False)
    ax_d.tick_params(left=False, labelleft=False)
    ax_d.invert_yaxis()

    # Highlight stats
    n = len(g_goals)
    late = (g_goals.minute >= 75).sum()
    second_half = (g_goals.minute >= 45).sum()
    first_15 = (g_goals.minute < 15).sum()
    ax.text(0.02, 0.97,
            f"{n} goals across 72 group matches  •  "
            f"{late} ({late*100//n}%) in min 75+  •  "
            f"{second_half} ({second_half*100//n}%) after half-time  •  "
            f"{first_15} ({first_15*100//n}%) in the first 15",
            transform=ax.transAxes, ha="left", va="top",
            color=INK_SOFT, fontsize=9.5,
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#F1ECE2",
                      edgecolor=RULE))

    # Confederation legend horizontal at bottom
    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(handles, labels, loc="lower right",
                    ncol=6, fontsize=9, frameon=False)

    title_block(
        fig,
        "WC-2026 group stage in minutes — every goal, every day.",
        "Each dot is one of 215 group-stage goals, placed by date (x) and match "
        "minute (y); color = scoring team's confederation. Gold band = late "
        "goals (min 75+).",
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
