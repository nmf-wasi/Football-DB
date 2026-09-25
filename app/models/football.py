from sqlalchemy import Integer, Float, String, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from app.database.database import Base
from datetime import date as date_type, datetime
## TODO: FIXED AN ERROR IN DB OUTLINE, RUN ANOTHER MIGRATION!!!


class Country(Base):
    """for countries, only name is required, id is auto generated, and id is fk for league/Match"""

    __tablename__ = "countries"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    leagues: Mapped[list["League"]] = relationship(back_populates="country")


class League(Base):
    """for leagues, we need the name of the league and country_id as fk, country obj is kept for pydantic"""

    __tablename__ = "leagues"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id", ondelete="RESTRICT"), index=True)
    country: Mapped["Country"] = relationship(back_populates="leagues")


class Team(Base):
    """id is the FK target everywhere. team_api_id is kept ONLY as a unique
    natural key for the seed script's idempotency check - no FK ever points at it. Team attr, home and away matches are for pydantic
    """

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_api_id: Mapped[int | None] = mapped_column(
        unique=True, index=True, nullable=True
    )
    team_long_name: Mapped[str | None] = mapped_column(nullable=True)
    team_short_name: Mapped[str] = mapped_column()
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)

    team_attributes: Mapped[list["TeamAttributes"]] = relationship(
        back_populates="team"
    )
    home_matches: Mapped[list["Match"]] = relationship(
        foreign_keys="Match.home_team_id", back_populates="home_team"
    )
    away_matches: Mapped[list["Match"]] = relationship(
        foreign_keys="Match.away_team_id", back_populates="away_team"
    )


class TeamAttributes(Base):
    """Different attributes of the team is stored on this table, team attr here is to access the team from an Attributes Row using pydantic. team_id FKs to Team.id - works for every team, seeded or manually created."""

    __tablename__ = "team_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), index=True
    )
    team: Mapped["Team"] = relationship(back_populates="team_attributes")
    creation_date: Mapped[datetime | None] = mapped_column(nullable=True)
    buildUpPlaySpeed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    buildUpPlayDribbling: Mapped[float | None] = mapped_column(Float, nullable=True)
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
    """Only player name is required to create a player, Attributes is used to access attributes of a player, id is the FK target everywhere. player_api_id is kept ONLY as a unique natural key for the seed script's idempotency check - no FK ever points at it."""

    __tablename__ = "players"
    id: Mapped[int] = mapped_column(primary_key=True)
    player_api_id: Mapped[int | None] = mapped_column(
        Integer, unique=True, nullable=True
    )
    player_name: Mapped[str] = mapped_column(String)
    birthday: Mapped[date_type | None] = mapped_column(Date, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    attributes: Mapped[list["PlayerAttributes"]] = relationship(back_populates="player")


class PlayerAttributes(Base):
    """Every player's attributes are stored in this table, player is a relationship to access player through foreign key, player_id FKs to Player.id - works for every player, seeded or manually created."""

    __tablename__ = "player_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)
    player_id: Mapped[int] = mapped_column(
        ForeignKey("players.id", ondelete="CASCADE"), index=True
    )
    player: Mapped[Player] = relationship(back_populates="attributes")
    creation_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    overall_rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    potential: Mapped[float | None] = mapped_column(Float, nullable=True)
    preferred_foot: Mapped[str | None] = mapped_column(String, nullable=True)
    attacking_work_rate: Mapped[str | None] = mapped_column(String, nullable=True)
    defensive_work_rate: Mapped[str | None] = mapped_column(String, nullable=True)
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
    """Every match has some infos and home and away teams are used to access the related teams, home_team_id / away_team_id both FK to Team.id"""

    __tablename__ = "matches"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    country_id: Mapped[int | None] = mapped_column(
        ForeignKey("countries.id", ondelete="RESTRICT"), nullable=True, index=True
    )
    league_id: Mapped[int | None] = mapped_column(
        ForeignKey("leagues.id",ondelete="RESTRICT"), nullable=True
    )
    season: Mapped[str | None] = mapped_column(String, nullable=True)
    stage: Mapped[int | None] = mapped_column(Integer, nullable=True)
    date: Mapped[date_type] = mapped_column(Date,nullable=False)
    match_api_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    home_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id",ondelete="RESTRICT"), index=True)
    away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id",ondelete="RESTRICT"))
    home_team: Mapped[Team] = relationship(
        foreign_keys=[home_team_id], back_populates="home_matches"
    )
    away_team: Mapped[Team] = relationship(
        foreign_keys=[away_team_id], back_populates="away_matches"
    )
    home_team_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_team_goal: Mapped[int | None] = mapped_column(Integer, nullable=True)
