from enum import Enum


class UserRole(Enum):
    """Add user roles here, when new roles are added, do alembic migrations"""

    USER = "User"
    ADMIN = "Admin"


class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class TeamSortFields(str, Enum):
    """Allowed sort fields for team"""

    ID = "id"
    TEAM_LONG_NAME = "team_long_name"
    TEAM_SHORT_NAME = "team_short_name"


class PlayerSortFields(str, Enum):
    """Allowed sort fields for player"""

    ID = "id"
    NAME = "player_name"
    birthday = "birthday"


class MatchSortFields(str, Enum):
    """Allowed sort fields for Match"""

    ID = "id"
    DATE = "date"
    COUNTRY_ID = "country_id"
    LEAGUE_ID = "league_id"
    SEASON = "season"


class LeagueSortField(str, Enum):
    """Allowed sort fields for League"""

    ID = "id"
    NAME = "name"
    COUNTRY_ID = "country_id"
class CountrySortField(str, Enum):
    """Allowed sort fields for Country"""

    ID = "id"
    NAME = "name"
