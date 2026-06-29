"""Viz 3: Knockout bracket tree — the 32 teams that survived groups.

Renders the R32 matchups as a left-aligned bracket of 16 horizontal pairs.
Where matches have been played, the score is shown; where scheduled, the date
is shown. Color codes the team's confederation. Future rounds are drawn as
empty slots so the tree is whole.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np

from _common import out_paths
from data.load import tournament_frame, teams
from style.house import (apply_style, credit, title_block, team_color,
                          INK, INK_SOFT, RULE, CONF_COLORS, PAGE_BG, GOLD)


NAME = "v03_bracket_r32"


def render():
    apply_style()
    tf = tournament_frame()
    r32 = tf[tf.stage_name == "Round of 32"].sort_values("date").reset_index(drop=True)
    n = len(r32)
    assert n == 16

    fig, ax = plt.subplots(figsize=(15, 13))
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)

    # Layout: 4 columns (R32, R16, QF, SF), plus Final in center column
    COL_X = [0.05, 0.30, 0.55, 0.78]  # left-edge x of each column box
    COL_W = [0.20, 0.20, 0.18, 0.16]

    # 16 R32 brackets stacked
    TOP, BOT = 0.92, 0.06
    row_h = (TOP - BOT) / 16
    pair_h = row_h * 0.78
    gap = row_h * 0.22

    def draw_team_row(x, y, w, h, name, score, conf, won=None):
        # Color band (confederation strip)
        cstrip_w = 0.012
        ax.add_patch(plt.Rectangle((x, y), cstrip_w, h,
                                    facecolor=CONF_COLORS.get(conf, "#999"),
                                    edgecolor="none"))
        bg = "#F1ECE2" if won is None else ("#E3F3E9" if won else "#F8E6E4")
        ax.add_patch(plt.Rectangle((x + cstrip_w, y), w - cstrip_w, h,
                                    facecolor=bg, edgecolor=RULE,
                                    linewidth=0.6))
        # Name
        ax.text(x + cstrip_w + 0.005, y + h / 2, str(name) if pd_notnull(name) else "—",
                ha="left", va="center", color=INK,
                fontsize=9.5, fontweight="bold" if won else "regular")
        # Score (right-aligned)
        score_text = f"{int(score)}" if pd_notnull(score) else ""
        ax.text(x + w - 0.005, y + h / 2, score_text,
                ha="right", va="center", color=INK,
                fontsize=11, fontweight="bold")

    import pandas as pd  # noqa: E402
    def pd_notnull(v):
        try:
            return pd.notnull(v)
        except Exception:
            return v is not None

    # R32 matches
    for i, r in r32.iterrows():
        y_base = TOP - (i + 1) * row_h
        h = pair_h / 2 - 0.001
        home_won = (pd.notnull(r.home_score) and r.home_score > r.away_score) if r.completed else None
        away_won = (pd.notnull(r.away_score) and r.away_score > r.home_score) if r.completed else None
        # home row (top), away row (bottom)
        draw_team_row(COL_X[0], y_base + pair_h / 2 + 0.001, COL_W[0], h,
                       r.home_team_name, r.home_score, r.home_confederation,
                       won=home_won)
        draw_team_row(COL_X[0], y_base, COL_W[0], h,
                       r.away_team_name, r.away_score, r.away_confederation,
                       won=away_won)
        # Match metadata above
        date_str = pd.to_datetime(r.date).strftime("%b %d")
        ax.text(COL_X[0] + COL_W[0] / 2, y_base + pair_h + 0.002, date_str,
                ha="center", va="bottom", color=INK_SOFT, fontsize=8)
        if not r.completed:
            ax.text(COL_X[0] + COL_W[0] + 0.005, y_base + pair_h / 2, "•",
                    ha="left", va="center", color=INK_SOFT, fontsize=10)

    # Empty slots for R16 (8), QF (4), SF (2) + Final
    def draw_slots(col, n_slots, parent_pair_count):
        x = COL_X[col]
        w = COL_W[col]
        h_slot = pair_h / 2 - 0.001
        for i in range(n_slots):
            # Center each slot pair between two parent slots
            # parents are at row indices 2*i and 2*i+1 of the previous column
            prev_pair_per_slot = parent_pair_count // n_slots
            top_y = TOP - (2 * i * (row_h * prev_pair_per_slot / 2) + row_h * prev_pair_per_slot / 2)
            # Simpler: compute mid-y of the two parent matches
            # For col=1 (R16), parent matches at col=0 indices 2*i and 2*i+1
            # mid-y of match i = TOP - (i + 0.5) * row_h
            # mid-y of pair = avg of mids = TOP - ((2i + 0.5 + 2i + 1.5) / 2) * row_h
            # = TOP - (2i + 1) * row_h
            mid_y = TOP - (2 * i + 1) * row_h * (parent_pair_count // n_slots // 2) if False else TOP - (2 * i + 1) * row_h
            # Above is for col=1 only. For col=2 (QF), parents at col=1
            # We'll compute generically:
            pass
        # Generic implementation:
        # For col c, each slot pair groups 2 parent pairs from col c-1.
        # The y-center of a slot pair at index i is the avg of pair-i-of-col-c
        # parent positions.

    # Compute pair midpoints per column
    midpoints = []
    # col0 (R32) midpoints
    col0_mid = [TOP - (i + 0.5) * row_h for i in range(16)]
    midpoints.append(col0_mid)
    # col1 (R16): each slot pairs two col0 pairs => avg of two col0 mids
    col1_mid = [(col0_mid[2 * i] + col0_mid[2 * i + 1]) / 2 for i in range(8)]
    midpoints.append(col1_mid)
    col2_mid = [(col1_mid[2 * i] + col1_mid[2 * i + 1]) / 2 for i in range(4)]
    midpoints.append(col2_mid)
    col3_mid = [(col2_mid[2 * i] + col2_mid[2 * i + 1]) / 2 for i in range(2)]
    midpoints.append(col3_mid)
    final_mid = (col3_mid[0] + col3_mid[1]) / 2

    # Draw connectors col0->col1, col1->col2, col2->col3, col3->Final
    def connector(x0, y0, x1, y1):
        midx = x0 + (x1 - x0) * 0.55
        ax.plot([x0, midx, midx, x1], [y0, y0, y1, y1],
                color=RULE, linewidth=0.9, solid_capstyle="round")

    for c in range(3):
        src = midpoints[c]
        tgt = midpoints[c + 1]
        n_tgt = len(tgt)
        x_src_right = COL_X[c] + COL_W[c]
        x_tgt_left = COL_X[c + 1]
        for i in range(n_tgt):
            connector(x_src_right, src[2 * i], x_tgt_left, tgt[i])
            connector(x_src_right, src[2 * i + 1], x_tgt_left, tgt[i])

    # Draw empty slot boxes for R16, QF, SF
    pair_h_for_empty = pair_h
    for c, mids in enumerate(midpoints[1:], start=1):
        x = COL_X[c]
        w = COL_W[c]
        for my in mids:
            h_each = pair_h_for_empty / 2 - 0.001
            for k in (0, 1):
                yy = my - pair_h_for_empty / 2 + k * (pair_h_for_empty / 2 + 0.001)
                ax.add_patch(plt.Rectangle((x, yy), w, h_each,
                                            facecolor="#FFFFFF",
                                            edgecolor=RULE, linewidth=0.5))
            ax.plot([x, x + w], [my, my], color=RULE, linewidth=0.4)

    # Final box (single match) at far right
    final_x = 0.93
    final_w = 0.06
    fh = pair_h
    final_left = final_x - final_w
    ax.add_patch(plt.Rectangle((final_left, final_mid - fh / 2),
                                final_w, fh, facecolor="#FFFFFF",
                                edgecolor=GOLD, linewidth=1.5))
    ax.text(final_left + final_w / 2, final_mid, "Final",
            ha="center", va="center", color=GOLD, fontweight="bold",
            fontsize=11)
    # connectors col3 -> Final
    for s in midpoints[3]:
        connector(COL_X[3] + COL_W[3], s, final_left, final_mid)

    # Column headers
    headers = ["Round of 32 (1/16 played)", "Round of 16", "Quarter-finals",
               "Semi-finals"]
    for c, h in enumerate(headers):
        ax.text(COL_X[c] + COL_W[c] / 2, TOP + 0.03, h,
                ha="center", va="bottom", color=INK,
                fontsize=11, fontweight="bold")

    # Confederation legend
    legend_y = 0.04
    legend_x = 0.05
    spacing = 0.13
    for i, (conf, color) in enumerate(CONF_COLORS.items()):
        x = legend_x + i * spacing
        ax.add_patch(plt.Rectangle((x, legend_y), 0.01, 0.012,
                                    facecolor=color, edgecolor="none"))
        ax.text(x + 0.014, legend_y + 0.006, conf,
                ha="left", va="center", color=INK_SOFT, fontsize=9)

    title_block(
        fig,
        "WC-2026 knockouts — the bracket of 32, drawn whole.",
        "16 R32 matchups are set; only 1 has been played (South Africa 0–1 — top row). "
        "Slots ahead are empty until matches are played.",
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
