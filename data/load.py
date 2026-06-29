"""Loaders for the tidy WC-2026 frames used by every viz module."""
from __future__ import annotations

from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent


def _read(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / name)


def teams() -> pd.DataFrame:
    return _read("teams.csv")


def matches_raw() -> pd.DataFrame:
    return _read("matches.csv")


def matches_detailed() -> pd.DataFrame:
    return _read("matches_detailed.csv")


def stages() -> pd.DataFrame:
    return _read("tournament_stages.csv")


def venues() -> pd.DataFrame:
    return _read("venues.csv")


def team_stats() -> pd.DataFrame:
    return _read("match_team_stats.csv")


def events() -> pd.DataFrame:
    return _read("match_events.csv")


def lineups() -> pd.DataFrame:
    return _read("match_lineups.csv")


def players() -> pd.DataFrame:
    return _read("squads_and_players.csv")


def referees() -> pd.DataFrame:
    return _read("referees.csv")


def tournament_frame() -> pd.DataFrame:
    """One row per match, with stage, venue, both team names and confederations."""
    m = matches_raw().merge(stages(), on="stage_id")
    m = m.merge(venues()[["venue_id", "stadium_name", "city", "country",
                          "capacity", "latitude", "longitude", "elevation_meters"]],
                on="venue_id", how="left")
    t = teams()[["team_id", "team_name", "fifa_code", "group_letter",
                 "confederation", "fifa_ranking_pre_tournament", "elo_rating"]]
    m = m.merge(t.add_prefix("home_"), left_on="home_team_id",
                right_on="home_team_id", how="left")
    m = m.merge(t.add_prefix("away_"), left_on="away_team_id",
                right_on="away_team_id", how="left")
    m["completed"] = m["status"] == "Completed"
    m["total_goals"] = m["home_score"].fillna(0) + m["away_score"].fillna(0)
    m["goal_diff"] = m["home_score"].fillna(0) - m["away_score"].fillna(0)
    m["date"] = pd.to_datetime(m["date"])
    return m


def group_standings() -> pd.DataFrame:
    """Compute standings from completed group-stage matches."""
    m = tournament_frame()
    g = m[(m.stage_name == "Group Stage") & m.completed].copy()
    rows = []
    for _, r in g.iterrows():
        rows.append(dict(team_id=r.home_team_id, team_name=r.home_team_name,
                         group=r.home_group_letter, conf=r.home_confederation,
                         gf=r.home_score, ga=r.away_score,
                         w=int(r.home_score > r.away_score),
                         d=int(r.home_score == r.away_score),
                         l=int(r.home_score < r.away_score)))
        rows.append(dict(team_id=r.away_team_id, team_name=r.away_team_name,
                         group=r.away_group_letter, conf=r.away_confederation,
                         gf=r.away_score, ga=r.home_score,
                         w=int(r.away_score > r.home_score),
                         d=int(r.away_score == r.home_score),
                         l=int(r.away_score < r.home_score)))
    df = pd.DataFrame(rows)
    s = df.groupby(["team_id", "team_name", "group", "conf"], as_index=False).agg(
        played=("gf", "size"),
        w=("w", "sum"), d=("d", "sum"), l=("l", "sum"),
        gf=("gf", "sum"), ga=("ga", "sum"),
    )
    s["gd"] = s["gf"] - s["ga"]
    s["pts"] = s["w"] * 3 + s["d"]
    s = s.sort_values(["group", "pts", "gd", "gf"],
                      ascending=[True, False, False, False])
    s["rank_in_group"] = s.groupby("group").cumcount() + 1
    return s


def team_match_long() -> pd.DataFrame:
    """One row per (match, team) — useful for upset/swarm/heatmap analyses."""
    m = tournament_frame()
    rows = []
    for _, r in m.iterrows():
        rows.append(dict(match_id=r.match_id, stage=r.stage_name,
                         date=r.date, team_id=r.home_team_id,
                         team_name=r.home_team_name, opp_name=r.away_team_name,
                         conf=r.home_confederation, opp_conf=r.away_confederation,
                         elo=r.home_elo_rating, opp_elo=r.away_elo_rating,
                         rank=r.home_fifa_ranking_pre_tournament,
                         opp_rank=r.away_fifa_ranking_pre_tournament,
                         home_away="H", gf=r.home_score, ga=r.away_score,
                         status=r.status, group=r.home_group_letter,
                         xg=r.home_xg, opp_xg=r.away_xg))
        rows.append(dict(match_id=r.match_id, stage=r.stage_name,
                         date=r.date, team_id=r.away_team_id,
                         team_name=r.away_team_name, opp_name=r.home_team_name,
                         conf=r.away_confederation, opp_conf=r.home_confederation,
                         elo=r.away_elo_rating, opp_elo=r.home_elo_rating,
                         rank=r.away_fifa_ranking_pre_tournament,
                         opp_rank=r.home_fifa_ranking_pre_tournament,
                         home_away="A", gf=r.away_score, ga=r.home_score,
                         status=r.status, group=r.away_group_letter,
                         xg=r.away_xg, opp_xg=r.home_xg))
    return pd.DataFrame(rows)
