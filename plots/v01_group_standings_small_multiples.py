"""Viz 1: Group standings small-multiples — 12 panels, one per group.

Each panel devotes the left third to rank+team name, the middle to a goals
scored (green, right of spine) vs goals conceded (red, left of spine) bar,
and the right third to the points + goal difference.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import out_paths
from data.load import group_standings
from style.house import (apply_style, credit, title_block, team_color,
                          INK, INK_SOFT, OUTCOME_COLORS, RULE, GOLD)


NAME = "v01_group_standings_small_multiples"


def render():
    apply_style()
    s = group_standings()
    groups = sorted(s["group"].unique())

    fig, axes = plt.subplots(3, 4, figsize=(18, 12),
                              gridspec_kw=dict(hspace=0.55, wspace=0.20))
    axes = axes.flatten()

    max_g = max(s.gf.max(), s.ga.max())

    # Each panel uses x in [0, 1] with these regions:
    NAME_X0 = 0.02   # left edge of name area
    BAR_X0 = 0.36    # left edge of bar area (corresponds to -max_g)
    BAR_MID = 0.62   # zero spine
    BAR_X1 = 0.88    # right edge of bar area (corresponds to +max_g)
    POINTS_X = 0.93  # right side text

    def x_for_goals(v):
        # map v in [-max_g, max_g] to [BAR_X0, BAR_X1]
        return BAR_MID + (v / max_g) * (BAR_X1 - BAR_MID)

    for ax, g in zip(axes, groups):
        sub = s[s.group == g].copy().reset_index(drop=True)
        y = np.arange(len(sub))[::-1]

        ax.set_xlim(0, 1)
        ax.set_ylim(-0.6, len(sub) - 0.2)
        ax.set_xticks([]); ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_visible(False)

        # Spine
        ax.plot([BAR_MID, BAR_MID], [-0.5, len(sub) - 0.4],
                color=INK, linewidth=0.9, alpha=0.6)

        for i, r in sub.iterrows():
            row_y = y[i]
            # rank dot
            dot_color = GOLD if r.rank_in_group <= 2 else INK_SOFT
            ax.scatter(NAME_X0 + 0.015, row_y, s=180, color=dot_color, zorder=4)
            ax.text(NAME_X0 + 0.015, row_y, f"{int(r.rank_in_group)}",
                    ha="center", va="center_baseline",
                    color="white", fontsize=8.5, fontweight="bold", zorder=5)
            # team name
            ax.text(NAME_X0 + 0.04, row_y, r.team_name, ha="left",
                    va="center_baseline", color=INK,
                    fontsize=10, fontweight="bold")
            # Green (gf) bar — right of spine
            gf_right = x_for_goals(r.gf)
            ax.add_patch(plt.Rectangle((BAR_MID, row_y - 0.25),
                                        gf_right - BAR_MID, 0.5,
                                        facecolor=OUTCOME_COLORS["win"],
                                        edgecolor="none", alpha=0.9))
            # Red (ga) bar — left of spine
            ga_left = x_for_goals(-r.ga)
            ax.add_patch(plt.Rectangle((ga_left, row_y - 0.25),
                                        BAR_MID - ga_left, 0.5,
                                        facecolor=OUTCOME_COLORS["loss"],
                                        edgecolor="none", alpha=0.9))
            # Tiny numeric labels on bars (only if bar is non-trivial)
            if r.gf > 0:
                ax.text(gf_right + 0.005, row_y, f"{int(r.gf)}",
                        ha="left", va="center_baseline",
                        color=OUTCOME_COLORS["win"], fontsize=8)
            if r.ga > 0:
                ax.text(ga_left - 0.005, row_y, f"{int(r.ga)}",
                        ha="right", va="center_baseline",
                        color=OUTCOME_COLORS["loss"], fontsize=8)
            # Points pill on right
            color = team_color(r.team_name, default="#444")
            ax.text(POINTS_X + 0.015, row_y, f"{int(r.pts)}",
                    ha="right", va="center_baseline",
                    color=color, fontsize=12, fontweight="bold")
            ax.text(POINTS_X + 0.02, row_y, "pts", ha="left",
                    va="center_baseline", color=INK_SOFT, fontsize=8)

        # Tick marks at -max_g, 0, +max_g
        for v in (-max_g, max_g):
            ax.plot([x_for_goals(v)]*2, [-0.55, -0.45],
                    color=INK_SOFT, linewidth=0.6)
        ax.text(x_for_goals(-max_g), -0.62, f"{int(max_g)} GA",
                ha="center", va="top", color=INK_SOFT, fontsize=7.5)
        ax.text(x_for_goals(max_g), -0.62, f"{int(max_g)} GF",
                ha="center", va="top", color=INK_SOFT, fontsize=7.5)

        # Mini-title
        ax.text(0, len(sub) - 0.1, f"Group {g}",
                ha="left", va="bottom", fontsize=13, fontweight="bold",
                color=INK)
        # Group separator rule
        ax.plot([0, 1], [len(sub) - 0.4, len(sub) - 0.4],
                color=RULE, linewidth=0.5)

    title_block(
        fig,
        "WC-2026 group stage — the four-team verdicts, at a glance.",
        "Green bars: goals scored about the spine. Red bars: goals conceded. "
        "Gold dots: the top two finishers from each group who advance.",
        y=0.97,
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
