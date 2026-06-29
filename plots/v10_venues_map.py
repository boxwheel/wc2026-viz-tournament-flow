"""Viz 10: WC-2026 venues — a map (lat/lon scatter) sized by capacity, colored by goals.

The host trio (USA/Mexico/Canada) on a simple lat/lon plane (no basemap) with
each venue as a circle: size = stadium capacity, color = goals scored at that
venue. State outline approximated by the convex hull of host cities.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import pandas as pd

from _common import out_paths
from data.load import tournament_frame, venues
from style.house import (apply_style, credit, title_block,
                          INK, INK_SOFT, RULE, GOLD, SEQ_CMAP)


NAME = "v10_venues_map"


def render():
    apply_style()
    tf = tournament_frame()
    v = venues()
    # Goals per venue (group stage only — knockouts mostly unplayed)
    g = tf[tf.completed].copy()
    g["goals"] = g.home_score + g.away_score
    by_venue = g.groupby("venue_id").agg(
        goals=("goals", "sum"),
        matches=("match_id", "count"),
    ).reset_index()
    v = v.merge(by_venue, on="venue_id", how="left").fillna({"goals": 0, "matches": 0})

    fig, ax = plt.subplots(figsize=(15, 11))

    # Country tint backgrounds
    ax.set_xlim(-130, -65)
    ax.set_ylim(15, 55)

    # Soft country bands (just colored rectangles for the three host nations)
    # USA box ~ 25..50 lat, -125..-65 lon
    ax.add_patch(plt.Rectangle((-125, 25), 60, 25, facecolor="#EAE3D6",
                                edgecolor="none", alpha=0.55, zorder=0))
    # Mexico ~ 14..32 lat, -118..-86 lon
    ax.add_patch(plt.Rectangle((-118, 14), 32, 18, facecolor="#E0D7C5",
                                edgecolor="none", alpha=0.55, zorder=0))
    # Canada ~ 42..70 lat, -140..-50 lon (shown only above 49)
    ax.add_patch(plt.Rectangle((-140, 49), 90, 21, facecolor="#D9D2C5",
                                edgecolor="none", alpha=0.55, zorder=0))

    # Plot venues
    norm = mcolors.Normalize(vmin=0, vmax=v.goals.max())
    cmap = plt.get_cmap(SEQ_CMAP)

    for _, r in v.iterrows():
        size = 60 + (r.capacity / 70000) * 800
        ax.scatter(r.longitude, r.latitude, s=size,
                    color=cmap(norm(r.goals)),
                    edgecolor="white", linewidth=1.5, zorder=4)

    # Label venues
    for _, r in v.iterrows():
        ax.annotate(f"{r.city}\n{int(r.capacity/1000)}k · {int(r.goals)}g",
                    (r.longitude, r.latitude),
                    xytext=(8, 8), textcoords="offset points",
                    fontsize=8.5, color=INK,
                    bbox=dict(boxstyle="round,pad=0.25",
                              facecolor="white", edgecolor=RULE, alpha=0.9))

    # Country labels
    ax.text(-100, 50, "CANADA", color=INK_SOFT, fontsize=18,
            fontweight="bold", alpha=0.4, ha="center")
    ax.text(-98, 39, "USA", color=INK_SOFT, fontsize=22,
            fontweight="bold", alpha=0.4, ha="center")
    ax.text(-102, 23, "MEXICO", color=INK_SOFT, fontsize=18,
            fontweight="bold", alpha=0.4, ha="center")

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.grid(True, alpha=0.18, zorder=1)

    # Colorbar
    sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cax = fig.add_axes([0.18, 0.08, 0.25, 0.012])
    cb = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cb.outline.set_visible(False)
    cb.ax.tick_params(labelsize=8, color=INK_SOFT)
    cax.set_title("Goals scored at venue (group + R32)",
                  fontsize=9, color=INK_SOFT, pad=6)

    # Size legend
    sl_ax = fig.add_axes([0.55, 0.07, 0.15, 0.04])
    sl_ax.set_xticks([]); sl_ax.set_yticks([])
    for sp in sl_ax.spines.values():
        sp.set_visible(False)
    cap_examples = [30000, 50000, 80000]
    for i, c in enumerate(cap_examples):
        size = 60 + (c / 70000) * 800
        sl_ax.scatter(i + 0.5, 0.5, s=size, color="white",
                       edgecolor=INK_SOFT, linewidth=1)
        sl_ax.text(i + 0.5, -0.1, f"{c//1000}k",
                    ha="center", va="top", color=INK_SOFT, fontsize=9)
    sl_ax.set_xlim(0, len(cap_examples))
    sl_ax.set_ylim(-0.8, 1.2)
    sl_ax.text(len(cap_examples) / 2, 1.4, "Stadium capacity",
                ha="center", va="bottom", color=INK_SOFT, fontsize=9)

    n_v = len(v)
    title_block(
        fig,
        "WC-2026 venues — capacity, location, and goals scored.",
        f"All {n_v} host venues across USA / Mexico / Canada. "
        "Dot size = stadium capacity; fill color = goals scored there so far.",
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
