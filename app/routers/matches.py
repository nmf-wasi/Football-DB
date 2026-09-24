# TODDO : <front-end> CHECK IF THE COUNTRY THEY ARE SETTING, EXISTS OR NOT, BETTER, GIVE THEM A SCROLLABLE LIST TO PICK FROM, DONT GIVE THEM OPTIONS TO SEND

from fastapi import status, Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import select, func, asc, desc,  or_
from app.database.database import get_db
from app.models.football import Match, Team, Country, League
from app.schemas.football import (
    MatchResponse,
    MatchCreate,
    MatchUpdate,
    PaginationResponse,
)
from app.models.user import User
from app.dependency import require_role
from app.config.enums import UserRole, MatchSortFields, SortOrder

router = APIRouter()

## TODO (v2): sort/filter on Team/PlayerAttributes - skipped for v1, low value vs. effort (nobody browses raw attribute snapshots the way they browse matches/players)


@router.get("/", response_model=PaginationResponse[MatchResponse])
def get_matches(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: MatchSortFields = MatchSortFields.DATE,
    order_by: SortOrder = SortOrder.ASC,
    season: str | None = Query(None),
    league_id: int | None = Query(None),
    team_id: int | None = None,
    db: Session = Depends(get_db),
):
    # get the attr for sort and order
    sort_column = getattr(Match, sort_by)
    order_func = desc if order_by == SortOrder.DESC else asc

    # base queryset
    queryset = select(Match).options(joinedload(Match.home_team), joinedload(Match.away_team))
    count_queryset = select(func.count()).select_from(Match)
    # filters
    filters=[]
    if season is not None:
        filters.append(Match.season==season)
    if league_id is not None:
        filters.append(Match.league_id==league_id)
    if team_id is not None:
        filters.append(
            or_(
                Match.home_team_id==team_id,
                Match.away_team_id==team_id,
            )
        )

    # apply filters
    queryset=queryset.where(*filters)
    count_queryset=count_queryset.where(*filters)

    # sort
    queryset = queryset.order_by(order_func(sort_column))

    # TODO: use this for sorting by team names, not required now -> sort by HOME_TEAM / AWAY_TEAM
    # queryset = queryset.join(Team, Match.home_team_id == Team.id).order_by(order_func(Team.team_long_name))

    # pagination
    queryset = queryset.offset(skip).limit(limit)
    return {
        "total": db.execute(count_queryset).scalar_one(),
        "skip": skip,
        "limit": limit,
        "items": db.execute(queryset).scalars().all(),
    }


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    match = db.execute(select(Match).options(joinedload(Match.home_team), joinedload(Match.away_team)).where(Match.id == match_id)).scalar_one_or_none()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match does not exist!",
        )
    return match


@router.post("/", response_model=MatchResponse)
def create_match(
    match_data: MatchCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    match_exists = db.execute(
        select(Match).where(
            Match.home_team_id == match_data.home_team_id,
            Match.away_team_id == match_data.away_team_id,
            Match.date == match_data.date,
        )
    ).scalar_one_or_none()
    if match_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Match with same date and teams already exists!",
        )

    home_team = db.execute(
        select(Team).where(Team.id == match_data.home_team_id)
    ).scalar_one_or_none()
    if not home_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home team not found!",
        )
    away_team = db.execute(
        select(Team).where(Team.id == match_data.away_team_id)
    ).scalar_one_or_none()
    if not away_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Away team not found!",
        )
    if match_data.country_id:
        country = db.execute(
            select(Country).where(Country.id == match_data.country_id)
        ).scalar_one_or_none()
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found!",
            )
    if match_data.league_id:
        league = db.execute(
            select(League).where(League.id == match_data.league_id)
        ).scalar_one_or_none()
        if not league:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League not found!",
            )

    new_match = Match()
    for key, val in match_data.model_dump().items():
        setattr(new_match, key, val)

    db.add(new_match)
    db.commit()
    db.refresh(new_match)
    return new_match


@router.patch("/{match_id}", response_model=MatchResponse)
def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    match = db.execute(
        select(Match).where(
            Match.id == match_id,
        )
    ).scalar_one_or_none()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match does not exist!",
        )

    updated_data = match_data.model_dump(exclude_unset=True)

    new_home_team_id = (
        match_data.home_team_id
        if match_data.home_team_id is not None
        else match.home_team_id
    )
    new_away_team_id = (
        match_data.away_team_id
        if match_data.away_team_id is not None
        else match.away_team_id
    )
    new_date = match_data.date if match_data.date is not None else match.date

    home_team = db.execute(
        select(Team).where(Team.id == new_home_team_id)
    ).scalar_one_or_none()
    if not home_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Home team not found!",
        )
    away_team = db.execute(
        select(Team).where(Team.id == new_away_team_id)
    ).scalar_one_or_none()
    if not away_team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Away team not found!",
        )
    if match_data.country_id:
        country = db.execute(
            select(Country).where(Country.id == match_data.country_id)
        ).scalar_one_or_none()
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found!",
            )
    if match_data.league_id:
        league = db.execute(
            select(League).where(League.id == match_data.league_id)
        ).scalar_one_or_none()
        if not league:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="League not found!",
            )

    if (
        match_data.home_team_id is not None
        or match_data.away_team_id is not None
        or match_data.date is not None
    ):
        duplicate_match = db.execute(
            select(Match).where(
                Match.id != match_id,
                Match.home_team_id == new_home_team_id,
                Match.away_team_id == new_away_team_id,
                Match.date == new_date,
            )
        ).scalar_one_or_none()

        if duplicate_match:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Match with same date and teams already exists!",
            )

    for key, val in updated_data.items():
        setattr(match, key, val)
    db.commit()
    db.refresh(match)
    return match


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_match(
    match_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    match = db.execute(
        select(Match).where(
            Match.id == match_id,
        )
    ).scalar_one_or_none()
    if not match:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Match does not exist!",
        )
    db.delete(match)
    db.commit()
