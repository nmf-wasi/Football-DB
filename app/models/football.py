from sqlalchemy import Integer, Float, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database.database import Base
from datetime import date as date_type, datetime

## TODO: FIXED AN ERROR IN DB OUTLINE, RUN ANOTHER MIGRATION!!!


class Country(Base):
    """for countries, only name is required, id is auto generated"""

    __tablename__ = "countries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)


class League(Base):
    """for leagues, we need the name of the league and country_id as fk, country obj is kept for pydantic"""

    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), index=True)
    country: Mapped["Country"] = relationship(back_populates="leagues")


class Team(Base):
    """Team has id, and API ID too, api id is used as fk to other tables, fifa api id is for fifa api. Team attr, home and away matches are for pydantic"""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_api_id: Mapped[int] = mapped_column(unique=True)
    team_fifa_api_id: Mapped[float | None] = mapped_column(default=None)
    team_long_name: Mapped[str | None] = mapped_column(nullable=True)
    team_short_name: Mapped[str] = mapped_column()

    team_attributes: Mapped[list["TeamAttributes"]] = relationship(
        back_populates="team"
    )
    home_matches: Mapped[list["Match"]] = relationship(
        foreign_keys="Match.home_team_api_id", back_populates="home_team"
    )
    away_matches: Mapped[list["Match"]] = relationship(
        foreign_keys="Match.away_team_api_id", back_populates="away_team"
    )


class TeamAttributes(Base):
    """Different attributes of the team is stored on this table, team attr here is to access the team from an Attributes Row using pydantic"""

    __tablename__ = "team_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_fifa_api_id: Mapped[int | None] = mapped_column(default=None)
    team_api_id: Mapped[int] = mapped_column(
        ForeignKey("teams.team_api_id", ondelete="CASCADE"),
        index=True,
    )
    team: Mapped[Team] = relationship(back_populates="team_attributes")
    creation_date: Mapped[datetime | None] = mapped_column(nullable=True)
    buildUpPlaySpeed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    buildUpPlayDribbling: Mapped[float | None] = mapped_column(Integer, nullable=True)
    buildUpPlayPassing: Mapped[int | None] = mapped_column(Integer, nullable=True)
    buildUpPlayPositioningClass: Mapped[str] = mapped_column(String, nullable=True)
    chanceCreationPassing: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chanceCreationCrossing: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chanceCreationShooting: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chanceCreationPositioningClass: Mapped[str | None] = mapped_column(
        String, nullable=True
    )
    defencePressure: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defenceAggression: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defenceTeamWidth: Mapped[int | None] = mapped_column(Integer, nullable=True)
    defenceDefenderLineClass: Mapped[str | None] = mapped_column(String, nullable=True)


class Player(Base):
    """Only player name is required to create a player, Attributes is used to access attributes of a player"""

    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_api_id: Mapped[int | None] = mapped_column(
        Integer, unique=True, nullable=True
    )
    player_name: Mapped[str] = mapped_column(String)
    player_fifa_api_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    birthday: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    attributes: Mapped[list["PlayerAttributes"]] = relationship(back_populates="player")


class PlayerAttributes(Base):
    """Every player's attributes are stored in this table, player is a relationship to access player through foreign key"""

    __tablename__ = "player_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_fifa_api_id: Mapped[int] = mapped_column(Integer, nullable=False)
    player_api_id: Mapped[int] = mapped_column(
        ForeignKey("players.player_api_id", ondelete="CASCADE"), index=True
    )
    player: Mapped[Player] = relationship(back_populates="attributes")
    creation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    overall_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_foot: Mapped[str] = mapped_column(String, nullable=False)
    attacking_work_rate: Mapped[str] = mapped_column(String, nullable=False)
    defensive_work_rate: Mapped[str] = mapped_column(String, nullable=False)
    sprint_speed: Mapped[float | None] = mapped_column(Float, nullable=True)
    finishing: Mapped[float | None] = mapped_column(Float, nullable=True)
    short_passing: Mapped[float | None] = mapped_column(Float, nullable=True)
    dribbling: Mapped[float | None] = mapped_column(Float, nullable=True)
    standing_tackle: Mapped[float | None] = mapped_column(Float, nullable=True)
    strength: Mapped[float | None] = mapped_column(Float, nullable=True)
    gk_diving: Mapped[float | None] = mapped_column(Float, nullable=True)
    gk_handling: Mapped[float | None] = mapped_column(Float, nullable=True)
    gk_kicking: Mapped[float | None] = mapped_column(Float, nullable=True)
    gk_positioning: Mapped[float | None] = mapped_column(Float, nullable=True)
    gk_reflexes: Mapped[float | None] = mapped_column(Float, nullable=True)


class Match(Base):
    """Every match has some infos and home and away teams are used to access the related teams"""

    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id"), nullable=True, index=True
    )
    league_id: Mapped[int | None] = mapped_column(
        ForeignKey("leagues.id"), nullable=True
    )
    season: Mapped[str | None] = mapped_column(String, nullable=True)
    stage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    match_api_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_team_api_id: Mapped[int] = mapped_column(ForeignKey("teams.team_api_id"))
    away_team_api_id: Mapped[int] = mapped_column(ForeignKey("teams.team_api_id"))
    home_team: Mapped[Team] = relationship(
        foreign_keys=[home_team_api_id], back_populates="home_matches"
    )
    away_team: Mapped[Team] = relationship(
        foreign_keys=[away_team_api_id], back_populates="away_matches"
    )
    home_team_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_team_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
