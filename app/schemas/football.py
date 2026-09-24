from pydantic import BaseModel
from datetime import date, datetime

## TODO: check the comments, u will see what to do!


from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    total: int
    skip: int
    limit: int
    items: list[T]


class CountryBase(BaseModel):
    name: str


class CountryResponse(CountryBase):
    id: int


class CountryCreate(CountryBase):
    pass


class CountryUpdate(BaseModel):
    name: str | None = None


class LeagueBase(BaseModel):
    name: str
    country_id: int


class LeagueCreate(LeagueBase):
    pass


class LeagueResponse(LeagueBase):
    id: int
    country: CountryBase


class LeagueUpdate(BaseModel):
    name: str | None = None
    country_id: int | None = None


class TeamBase(BaseModel):
    team_long_name: str
    team_short_name: str


class TeamResponseShort(TeamBase):
    id: int
    slug: str


class TeamResponseDetail(TeamBase):
    id: int
    team_attributes: list["TeamAttributesBase"]
    home_matches: list["MatchBase"]
    away_matches: list["MatchBase"]
    slug: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    team_long_name: str | None = None
    team_short_name: str | None = None


class TeamAttributesBase(BaseModel):
    creation_date: date | None = None
    buildUpPlaySpeed: int | None = None
    buildUpPlayDribbling: float | None = None
    buildUpPlayPassing: int | None = None
    buildUpPlayPositioningClass: str | None = None
    chanceCreationPassing: int | None = None
    chanceCreationCrossing: int | None = None
    chanceCreationShooting: int | None = None
    chanceCreationPositioningClass: str | None = None
    defencePressure: int | None = None
    defenceAggression: int | None = None
    defenceTeamWidth: int | None = None
    defenceDefenderLineClass: str | None = None


class TeamAttributesResponseShort(BaseModel):
    id: int
    creation_date: date | None = None
    buildUpPlayDribbling: float | None = None
    buildUpPlayPassing: int | None = None


class TeamAttributesResponse(TeamAttributesBase):
    id: int


class TeamAttributesCreate(TeamAttributesBase):
    pass


class TeamAttributesUpdate(TeamAttributesBase):
    pass


class PlayerBase(BaseModel):
    player_api_id: int | None = None
    player_name: str
    birthday: date
    height: float | None = None
    weight: float | None = None


class PlayerCreate(PlayerBase):
    pass


class PlayerResponse(PlayerBase):
    id: int
    attributes: list["PlayerAttributesResponseShort"]
    slug: str


class PlayerUpdate(BaseModel):
    player_api_id: int | None = None
    player_name: str | None = None
    birthday: date | None = None
    height: float | None = None
    weight: float | None = None


class PlayerAttributesBase(BaseModel):
    # player_api_id: int
    # player_id:int
    creation_date: datetime | None = None
    overall_rating: float | None = None
    potential: float | None = None
    preferred_foot: str | None = None
    attacking_work_rate: str | None = None
    defensive_work_rate: str | None = None
    sprint_speed: float | None = None
    finishing: float | None = None
    short_passing: float | None = None
    dribbling: float | None = None
    standing_tackle: float | None = None
    strength: float | None = None
    gk_diving: float | None = None
    gk_handling: float | None = None
    gk_kicking: float | None = None
    gk_positioning: float | None = None
    gk_reflexes: float | None = None


class PlayerAttributesResponseShort(BaseModel):
    creation_date: datetime | None = None
    overall_rating: float | None = None
    preferred_foot: str | None = None


class PlayerAttributesResponseDetail(PlayerAttributesBase):
    id: int
    player: PlayerBase


class PlayerAttributesCreate(PlayerAttributesBase):
    pass


class MatchBase(BaseModel):
    country_id: int | None = None
    league_id: int | None = None
    season: str | None = None
    stage: int | None = None
    date: date  # required - every match has one
    match_api_id: int | None = None
    home_team_id: int  # required - matches the model's FK rename
    away_team_id: int  # required - matches the model's FK rename


class MatchResponse(MatchBase):
    id: int
    home_team: TeamBase
    away_team: TeamBase
    home_team_goal: int | None = None
    away_team_goal: int | None = None


class MatchResponseShort(BaseModel):
    id: int
    date: date
    home_team_id: int
    away_team_id: int


class MatchCreate(MatchBase):
    pass


class MatchUpdate(MatchCreate):
    pass

    # home team or away team or data can't be none or else we can't check dups
