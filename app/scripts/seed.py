import pandas as pd
from app.models import football
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.database.database import SessionLocal
from app.utils.slug import slugify
import re
from datetime import datetime
from pathlib import Path

# Resolves the directory of seed.py -> app/scripts, then steps up to project root -> data/cleaned
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "cleaned"

# Country        -> depends on: nothing
# League         -> depends on: Country
# Team           -> depends on: nothing
# Player         -> depends on: nothing
# TeamAttributes -> depends on: Team
# PlayerAttributes -> depends on: Player
# Match          -> depends on: Country, League, Team (x2, home+away)
# Country → League → Team → Player → TeamAttributes → PlayerAttributes → Match
# DATA_DIR = "../data/cleaned"
db = SessionLocal()


def clean(value):
    """Convert pandas NaN to real None"""
    return None if pd.isna(value) else value


def create_country(db: Session, row: pd.Series):
    """Creaes a country, looks up into db to check if there's already the same country, if exitsts, return that, else returns a new country"""
    country_id = clean(row.get("id"))
    country_exits = db.get(football.Country, country_id)
    if country_exits:
        return country_exits
    new_country = football.Country(
        id=country_id,
        name=clean(row.get("name")),
    )
    db.add(new_country)
    return new_country


def create_league(db: Session, row: pd.Series):
    """looks up in a db to find similar league, if not found, creates a new league"""
    league_id = clean(row.get("id"))
    existing_league = db.get(football.League, league_id)
    if existing_league:
        return existing_league
    new_league = football.League(
        id=league_id,
        name=clean(row.get("name")),
        country_id=clean(row.get("country_id")),
    )
    db.add(new_league)
    return new_league


def create_team(db: Session, row: pd.Series, slug_tracker: set[str]):
    """Checks if there's already a team with the api id, if not, creates a new team"""
    team_api_id = clean(row.get("team_api_id"))
    team = db.execute(
        select(football.Team).where(football.Team.team_api_id == team_api_id)
    ).scalar_one_or_none()
    if team is not None:
        print("Team already exists!")
        return team

    new_team = football.Team(
        team_api_id=team_api_id,
        team_fifa_api_id=clean(row.get("team_fifa_api_id")),
        team_long_name=clean(row.get("team_long_name")),
        team_short_name=clean(row.get("team_short_name")),
        slug=slugify(row.get("team_long_name"), slug_tracker),
    )
    db.add(new_team)
    return new_team


def create_player(db: Session, row: pd.Series, slug_tracker: set[str]):
    """Checks if there's already a player with the api id, if not, creates a new player"""

    player_api_id = clean(row.get("player_api_id"))
    player = db.execute(
        select(football.Player).where(football.Player.player_api_id == player_api_id)
    ).scalar_one_or_none()

    if player is not None:
        print("Player already exists!")
        return player

    new_player = football.Player(
        player_api_id=player_api_id,
        player_name=clean(row.get("player_name")),
        player_fifa_api_id=clean(row.get("player_fifa_api_id")),
        birthday=clean(row.get("birthday")),
        height=clean(row.get("height")),
        weight=clean(row.get("weight")),
        slug=slugify(row.get("player_name"), slug_tracker),
    )

    db.add(new_player)
    return new_player


def create_team_attributes(db: Session, row: pd.Series):
    """doesn't need to check for dups, just get the data and insert in db"""
    new_attrs = football.TeamAttributes(
        team_fifa_api_id=clean(row.get("team_fifa_api_id")),
        team_api_id=clean(row.get("team_api_id")),
        creation_date=clean(row.get("date")),
        buildUpPlaySpeed=clean(row.get("buildUpPlaySpeed")),
        buildUpPlayDribbling=clean(row.get("buildUpPlayDribbling")),
        buildUpPlayPassing=clean(row.get("buildUpPlayPassing")),
        buildUpPlayPositioningClass=clean(row.get("buildUpPlayPositioningClass")),
        chanceCreationPassing=clean(row.get("chanceCreationPassing")),
        chanceCreationCrossing=clean(row.get("chanceCreationCrossing")),
        chanceCreationShooting=clean(row.get("chanceCreationShooting")),
        chanceCreationPositioningClass=clean(row.get("chanceCreationPositioningClass")),
        defencePressure=clean(row.get("defencePressure")),
        defenceAggression=clean(row.get("defenceAggression")),
        defenceTeamWidth=clean(row.get("defenceTeamWidth")),
        defenceDefenderLineClass=clean(row.get("defenceDefenderLineClass")),
    )
    db.add(new_attrs)


def create_player_attributes(db: Session, row: pd.Series):
    new_attrs = football.PlayerAttributes(
        player_fifa_api_id=clean(row.get("player_fifa_api_id")),
        player_api_id=clean(row.get("player_api_id")),
        creation_date=clean(row.get("date")),
        overall_rating=clean(row.get("overall_rating")),
        potential=clean(row.get("potential")),
        preferred_foot=clean(row.get("preferred_foot")),
        attacking_work_rate=clean(row.get("attacking_work_rate")),
        defensive_work_rate=clean(row.get("defensive_work_rate")),
        sprint_speed=clean(row.get("sprint_speed")),
        finishing=clean(row.get("finishing")),
        short_passing=clean(row.get("short_passing")),
        dribbling=clean(row.get("dribbling")),
        standing_tackle=clean(row.get("standing_tackle")),
        strength=clean(row.get("strength")),
        gk_diving=clean(row.get("gk_diving")),
        gk_handling=clean(row.get("gk_handling")),
        gk_kicking=clean(row.get("gk_kicking")),
        gk_positioning=clean(row.get("gk_positioning")),
        gk_reflexes=clean(row.get("gk_reflexes")),
    )
    db.add(new_attrs)


def create_match(db: Session, row: pd.Series):
    new_match = football.Match(
        country_id=clean(row.get("country_id")),
        league_id=clean(row.get("league_id")),
        season=clean(row.get("season")),
        stage=clean(row.get("stage")),
        date=clean(row.get("date")),
        match_api_id=clean(row.get("match_api_id")),
        home_team_api_id=clean(row.get("home_team_api_id")),
        away_team_api_id=clean(row.get("away_team_api_id")),
        home_team_goal=clean(row.get("home_team_goal")),
        away_team_goal=clean(row.get("away_team_goal")),
    )
    db.add(new_match)


def main():
    db = SessionLocal()
    team_slugs: set[str] = set()
    player_slugs: set[str] = set()

    try:
        # order follows the dependency graph: parents before children
        country_df = pd.read_csv(f"{DATA_DIR}/country.csv")
        for _, row in country_df.iterrows():
            create_country(db, row)
        db.commit()
        print(f"Seeded {len(country_df)} countries")

        league_df = pd.read_csv(f"{DATA_DIR}/league.csv")
        for _, row in league_df.iterrows():
            create_league(db, row)
        db.commit()
        print(f"Seeded {len(league_df)} leagues")

        team_df = pd.read_csv(f"{DATA_DIR}/team.csv")
        for _, row in team_df.iterrows():
            create_team(db, row, team_slugs)
        db.commit()
        print(f"Seeded {len(team_df)} teams")

        player_df = pd.read_csv(f"{DATA_DIR}/player.csv")
        for _, row in player_df.iterrows():
            create_player(db, row, player_slugs)
        db.commit()
        print(f"Seeded {len(player_df)} players")

        team_attrs_df = pd.read_csv(f"{DATA_DIR}/team_attributes.csv")
        for _, row in team_attrs_df.iterrows():
            create_team_attributes(db, row)
        db.commit()
        print(f"Seeded {len(team_attrs_df)} team_attributes rows")

        player_attrs_df = pd.read_csv(f"{DATA_DIR}/player_attributes.csv")
        for _, row in player_attrs_df.iterrows():
            create_player_attributes(db, row)
        db.commit()
        print(f"Seeded {len(player_attrs_df)} player_attributes rows")

        match_df = pd.read_csv(f"{DATA_DIR}/match.csv")
        for _, row in match_df.iterrows():
            create_match(db, row)
        db.commit()
        print(f"Seeded {len(match_df)} matches")

    finally:
        db.close()


if __name__ == "__main__":
    main()


# db.get is primary key lookup shortcut
# TeamAttributes/PlayerAttributes/Match have no existence check
# One db.commit() per table
