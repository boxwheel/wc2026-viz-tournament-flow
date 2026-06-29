"""House style: a single shared aesthetic for the WC-2026 viz gallery.

Call ``apply_style()`` once at the top of every plot script. Exposes palettes
and a ``credit()`` helper for the consistent caption stamp.
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

PAGE_BG = "#FBF8F2"
INK = "#1A1A1A"
INK_SOFT = "#4A4A4A"
RULE = "#D9D2C5"
ACCENT = "#C8102E"
GOLD = "#C9A227"
PITCH_GREEN = "#1E5631"

CONF_COLORS = {
    "UEFA": "#1F4E79",
    "CONMEBOL": "#0F8A5F",
    "CONCACAF": "#C8102E",
    "AFC": "#E07B00",
    "CAF": "#7A4FB2",
    "OFC": "#2BB1C8",
}

OUTCOME_COLORS = {
    "win": "#0F8A5F",
    "draw": "#A0A0A0",
    "loss": "#C8102E",
}

SEQ_CMAP = "rocket_r"
DIV_CMAP = "vlag"

TEAM_COLORS = {
    "Argentina": "#75AADB",
    "Brazil": "#FFCB05",
    "France": "#0055A4",
    "England": "#CE1124",
    "Germany": "#000000",
    "Spain": "#C60B1E",
    "Portugal": "#006633",
    "Netherlands": "#FF6900",
    "Italy": "#1B3A82",
    "Belgium": "#E30613",
    "Croatia": "#171796",
    "USA": "#3C3B6E",
    "Mexico": "#006847",
    "Canada": "#D52B1E",
    "Japan": "#BC002D",
    "South Korea": "#003478",
    "Morocco": "#C1272D",
    "Senegal": "#00853F",
    "Australia": "#FFB81C",
    "Uruguay": "#5CBFEB",
    "Colombia": "#FCD116",
    "Switzerland": "#D52B1E",
    "Denmark": "#C8102E",
    "Saudi Arabia": "#006C35",
    "Iran": "#239F40",
    "Ecuador": "#FFD100",
    "Ghana": "#006B3F",
    "Côte d'Ivoire": "#F77F00",
    "Cameroon": "#007A3D",
    "Algeria": "#006233",
    "Egypt": "#D72121",
    "Nigeria": "#008753",
    "South Africa": "#007749",
    "Tunisia": "#E70013",
    "Poland": "#DC143C",
    "Serbia": "#C6363C",
    "Austria": "#ED2939",
    "Czech Republic": "#11457E",
    "Norway": "#BA0C2F",
    "Wales": "#D30731",
    "Scotland": "#0065BD",
    "Türkiye": "#E30A17",
    "Ukraine": "#FFD500",
    "Hungary": "#477050",
    "Sweden": "#FECC02",
    "Paraguay": "#DA121A",
    "Peru": "#D91023",
    "Chile": "#0039A6",
    "Venezuela": "#CF142B",
    "Costa Rica": "#002B7F",
    "Panama": "#005AA7",
    "Jamaica": "#009B3A",
    "Honduras": "#0073CF",
    "New Zealand": "#000000",
    "Qatar": "#8A1538",
    "United Arab Emirates": "#009639",
    "Iraq": "#CE1126",
    "Uzbekistan": "#1EB53A",
}


def apply_style():
    """Apply the house matplotlib + seaborn theme."""
    sns.set_theme(context="talk", style="white")
    mpl.rcParams.update({
        "figure.facecolor": PAGE_BG,
        "axes.facecolor": PAGE_BG,
        "savefig.facecolor": PAGE_BG,
        "savefig.edgecolor": PAGE_BG,
        "figure.dpi": 110,
        "savefig.dpi": 200,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.35,

        "font.family": ["DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 16,
        "axes.titleweight": "bold",
        "axes.titlepad": 12,
        "axes.labelsize": 11,
        "axes.labelcolor": INK_SOFT,
        "axes.labelweight": "regular",
        "axes.edgecolor": RULE,
        "axes.linewidth": 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": False,
        "grid.color": RULE,
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,

        "xtick.color": INK_SOFT,
        "ytick.color": INK_SOFT,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
        "xtick.major.size": 0,
        "ytick.major.size": 0,

        "legend.frameon": False,
        "legend.fontsize": 10,
        "text.color": INK,
    })


def credit(fig, source="Kaggle: mominullptr/fifa-world-cup-2026-dataset",
           viz="boxwheel/wc2026-viz-tournament-flow", y=0.02):
    """Stamp source + repo credit on a figure."""
    fig.text(0.5, y,
             f"Source: {source}  ·  {viz}",
             ha="center", va="bottom",
             fontsize=8, color=INK_SOFT, style="italic")


def title_block(fig, title, subtitle=None, x=0.06, y=0.965, subtitle_dy=0.03):
    """Left-aligned editorial title + subtitle block."""
    fig.text(x, y, title, ha="left", va="top",
             fontsize=20, fontweight="bold", color=INK)
    if subtitle:
        fig.text(x, y - subtitle_dy, subtitle, ha="left", va="top",
                 fontsize=12, color=INK_SOFT)


def team_color(name, default="#444444"):
    return TEAM_COLORS.get(name, default)
