from pydantic import BaseModel, ConfigDict, field_validator
from datetime import date as date_type, datetime

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
    model_config = ConfigDict(from_attributes=True)


class CountryCreate(CountryBase):
    @field_validator("name")
    @classmethod
    def capitalize_name(cls, name: str) -> str:
        return name.capitalize()


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
    model_config = ConfigDict(from_attributes=True)


class LeagueUpdate(BaseModel):
    name: str | None = None
    country_id: int | None = None


class TeamBase(BaseModel):
    team_long_name: str
    team_short_name: str


class TeamResponseShort(TeamBase):
    id: int
    slug: str
    model_config = ConfigDict(from_attributes=True)


class TeamResponseDetail(TeamBase):
    id: int
    team_attributes: list["TeamAttributesBase"]
    home_matches: list["MatchBase"]
    away_matches: list["MatchBase"]
    slug: str
    model_config = ConfigDict(from_attributes=True)


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):
    team_long_name: str | None = None
    team_short_name: str | None = None


class TeamAttributesBase(BaseModel):
    creation_date: date_type | None = None
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
    creation_date: date_type | None = None
    buildUpPlayDribbling: float | None = None
    buildUpPlayPassing: int | None = None
    model_config = ConfigDict(from_attributes=True)


class TeamAttributesResponse(TeamAttributesBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


class TeamAttributesCreate(TeamAttributesBase):
    pass


class TeamAttributesUpdate(TeamAttributesBase):
    pass


class PlayerBase(BaseModel):
    player_api_id: int | None = None
    player_name: str
    birthday: date_type
    height: float | None = None
    weight: float | None = None


class PlayerCreate(PlayerBase):
    @field_validator("birthday")
    @classmethod
    def validate_date_not_in_future(cls, birthday: date_type) -> date_type:
        if birthday > date_type.today():
            raise ValueError("Birthday cannot be in the future")
        return birthday


class PlayerResponse(PlayerBase):
    id: int
    attributes: list["PlayerAttributesResponseShort"]
    slug: str
    model_config = ConfigDict(from_attributes=True)


class PlayerUpdate(BaseModel):
    player_api_id: int | None = None
    player_name: str | None = None
    birthday: date_type | None = None
    height: float | None = None
    weight: float | None = None

    @field_validator("birthday")
    @classmethod
    def validate_date_not_in_future(
        cls, birthday: date_type | None
    ) -> date_type | None:
        if birthday is not None and birthday > date_type.today():
            raise ValueError("Birthday cannot be in the future")
        return birthday


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
    model_config = ConfigDict(from_attributes=True)


class PlayerAttributesResponseDetail(PlayerAttributesBase):
    id: int
    player: PlayerBase
    model_config = ConfigDict(from_attributes=True)


class PlayerAttributesCreate(PlayerAttributesBase):
    @field_validator("creation_date")
    @classmethod
    def validate_date_not_in_future(cls, value: datetime | None) -> datetime | None:
        if value is not None and value > datetime.now():
            raise ValueError("Creation date cannot be in the future")
        return value


class MatchBase(BaseModel):
    country_id: int | None = None
    league_id: int | None = None
    season: str | None = None
    stage: int | None = None
    date: date_type  # required - every match has one
    match_api_id: int | None = None
    home_team_id: int  # required - matches the model's FK rename
    away_team_id: int  # required - matches the model's FK rename


class MatchResponse(MatchBase):
    id: int
    home_team: TeamBase
    away_team: TeamBase
    home_team_goal: int | None = None
    away_team_goal: int | None = None
    model_config = ConfigDict(from_attributes=True)


class MatchResponseShort(BaseModel):
    id: int
    date: date_type
    home_team_id: int
    away_team_id: int
    model_config = ConfigDict(from_attributes=True)


class MatchCreate(MatchBase):

    @field_validator("date")
    @classmethod
    def validate_date_not_in_future(cls, value: date_type) -> date_type:
        if value > date_type.today():
            raise ValueError("Match date cannot be in the future")
        return value


class MatchUpdate(BaseModel):
    country_id: int | None = None
    league_id: int | None = None
    season: str | None = None
    stage: int | None = None
    date: date_type | None = None
    match_api_id: int | None = None
    home_team_id: int | None = None
    away_team_id: int | None = None

    @field_validator("date")
    @classmethod
    def validate_date_not_in_future(
        cls, birthday: date_type | None
    ) -> date_type | None:
        if birthday is not None and birthday > date_type.today():
            raise ValueError("Birthday cannot be in the future")
        return birthday

    # home team or away team or data can't be none or else we can't check dups
