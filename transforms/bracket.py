"""Bracket / sankey transforms: turn the WC-2026 fixture list into a flow graph."""
from __future__ import annotations

import pandas as pd

STAGE_ORDER = [
    "Group Stage",
    "Round of 32",
    "Round of 16",
    "Quarter-finals",
    "Semi-finals",
    "Third-place match",
    "Final",
]

STAGE_RANK = {s: i for i, s in enumerate(STAGE_ORDER)}


def confederation_to_stage_flow(tournament: pd.DataFrame) -> pd.DataFrame:
    """Edges: (confederation_at_groups) -> (advanced_to_stage).

    A team is mapped to the deepest stage they appear in (whether they played
    it yet or not — scheduled fixtures count as "advanced to that round").
    """
    long = []
    for _, r in tournament.iterrows():
        long.append((r.home_team_id, r.home_team_name, r.home_confederation,
                     r.home_group_letter, r.stage_name))
        long.append((r.away_team_id, r.away_team_name, r.away_confederation,
                     r.away_group_letter, r.stage_name))
    df = pd.DataFrame(long, columns=["team_id", "team_name", "conf",
                                      "group", "stage"])
    df["rank"] = df["stage"].map(STAGE_RANK)
    deepest = df.sort_values("rank").drop_duplicates("team_id", keep="last")
    return deepest


def group_to_knockout_edges(standings: pd.DataFrame,
                            advanced: pd.DataFrame) -> pd.DataFrame:
    """Sankey edges: (group letter) -> (Advance|Eliminate)."""
    adv_ids = set(advanced[advanced.stage != "Group Stage"].team_id)
    rows = []
    for _, r in standings.iterrows():
        target = "Advance" if r.team_id in adv_ids else "Out"
        rows.append((r.group, target, 1))
    return pd.DataFrame(rows, columns=["src", "tgt", "n"])
