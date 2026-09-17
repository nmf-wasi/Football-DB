from pydantic import BaseModel
from datetime import date, datetime

## TODO: check the comments, u will see what to do!


class CountryBase(BaseModel):
    name: str


class CountryResponse(CountryBase):
    id: int


class CountryCreate(CountryBase):
    pass


class LeagueBase(BaseModel):
    name: str
    country_id: int


class LeagueCreate(LeagueBase):
    pass


class LeagueResponse(LeagueBase):
    id: int
    country: CountryBase


class TeamBase(BaseModel):
    team_long_name: str
    team_short_name: str
    team_api_id: int  # CHECK IF U CAN MAKE THIS NULLABLE, DONT TRUST THE DATASET, USE BRAIN TO IDENTIFY THE CLASS AND IF IT'S NULABLE OR NOT
    team_fifa_api_id: float | None
    # CHECK IF U CAN MAKE THIS NULLABLE, DONT TRUST THE DATASET, USE BRAIN TO IDENTIFY THE CLASS AND IF IT'S NULABLE OR NOT


class TeamResponse(TeamBase):
    id: int
    team_attributes: list["TeamAttributesBase"]
    home_matches: list["MatchBase"]
    away_matches: list["MatchBase"]
    slug: str


class TeamCreate(TeamBase):
    pass


class TeamAttributesBase(BaseModel):
    team_fifa_api_id: int | None = None
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


class TeamAttributesResponse(TeamAttributesBase):
    id: int


class TeamAttributesCreate(TeamAttributesBase):
    pass


class PlayerBase(BaseModel):
    player_api_id: int | None = None
    player_name: str
    player_fifa_api_id: int | None = None
    birthday: date
    height: float | None = None
    weight: float | None = None


class PlayerCreate(PlayerBase):
    pass


class PlayerResponse(PlayerBase):
    id: int
    attributes: list["PlayerAttributesBase"]
    slug: str


class PlayerUpdate(BaseModel):
    player_api_id: int | None = None
    player_name: str | None = None
    player_fifa_api_id: int | None = None
    birthday: date | None = None
    height: float | None = None
    weight: float | None = None


class PlayerAttributesBase(BaseModel):
    # player_fifa_api_id: int
    # player_api_id: int
    # player_id:int
    creation_date: datetime | None = None
    overall_rating: float | None = None
    potential: float | None = None
    preferred_foot: str
    attacking_work_rate: str
    defensive_work_rate: str
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


class PlayerAttributesResponse(PlayerAttributesBase):
    id: int
    player: PlayerBase


class PlayerAttributesCreate(PlayerAttributesBase):
    pass


class MatchBase(BaseModel):
    country_id: int | None = None
    league_id: int | None = None
    season: str | None = (
        None  # make it like seaons availble till current year, also auto update for next year
    )
    stage: int | None = None
    date: date | None
    match_api_id: int | None
    home_team_api_id: (
        int | None
    )  # make these scrollable,  select from the scroll, not just pass a value
    away_team_api_id: int | None


class MatchResponse(MatchBase):
    id: int  # use uuid
    home_team: TeamBase
    away_team: TeamBase
    home_team_goal: int | None = None
    away_team_goal: int | None = None


class MatchCreate(MatchBase):
    pass
