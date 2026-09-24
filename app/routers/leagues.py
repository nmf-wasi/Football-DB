from fastapi import status, Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from sqlalchemy.exc import IntegrityError
from app.database.database import get_db
from app.models.football import League, Country
from app.schemas.football import (
    LeagueResponse,
    LeagueCreate,
    LeagueUpdate,
    PaginationResponse,
)
from app.models.user import User
from app.dependency import require_role
from app.config.enums import UserRole, SortOrder, LeagueSortField

router = APIRouter()


@router.get("/", response_model=PaginationResponse[LeagueResponse])
def get_leagues(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: LeagueSortField = LeagueSortField.NAME,
    order_by: SortOrder = SortOrder.ASC,
    country_id: int | None = Query(None),
    search:str=Query(None, min_length=1, max_length=24),
    db: Session = Depends(get_db),
):
    # get sort and order by val
    sort_column = getattr(League, sort_by)
    order_func = desc if order_by == SortOrder.DESC else asc

    # base queryset
    queryset = select(League)
    count_queryset = select(func.count()).select_from(League)
    # filters 
    filters=[]
    # search
    if search is not None:
        filters.append(League.name.ilike(f"%{search}%"))

    # filters
    if country_id is not None:
        filters.append(League.country_id==country_id)

    # apply filters
    queryset=queryset.where(*filters)
    count_queryset=count_queryset.where(*filters)

    # sort
    queryset = queryset.order_by(order_func(sort_column))

    # pagination
    queryset = queryset.offset(skip).limit(limit)
    return {
        "total": db.execute(count_queryset).scalar_one(),
        "skip": skip,
        "limit": limit,
        "items": db.execute(queryset).scalars().all(),
    }


@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(
    league_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    league = db.execute(
        select(League).where(League.id == league_id)
    ).scalar_one_or_none()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="League does not exist!",
        )
    return league


@router.post("/", response_model=LeagueResponse)
def create_league(
    league_data: LeagueCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    league_exists = db.execute(
        select(League).where(
            League.name == league_data.name,
            League.country_id == league_data.country_id,
        )
    ).scalar_one_or_none()
    if league_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="League with same name already exists for this country!",
        )

    country = db.execute(
        select(Country).where(Country.id == league_data.country_id)
    ).scalar_one_or_none()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country not found!",
        )
    new_league = League()
    for key, val in league_data.model_dump().items():
        setattr(new_league, key, val)
    db.add(new_league)
    db.commit()
    db.refresh(new_league)
    return new_league


@router.patch("/{league_id}", response_model=LeagueResponse)
def update_league(
    league_id: int,
    league_data: LeagueUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    league = db.execute(
        select(League).where(
            League.id == league_id,
        )
    ).scalar_one_or_none()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="league does not exist!",
        )

    if league_data.country_id is not None:
        country = db.execute(
            select(Country).where(Country.id == league_data.country_id)
        ).scalar_one_or_none()
        if not country:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Country not found!",
            )

    new_name = league_data.name if league_data.name is not None else league.name
    new_country_id = (
        league_data.country_id
        if league_data.country_id is not None
        else league.country_id
    )

    if league_data.name is not None or league_data.country_id is not None:
        duplicate_league = db.execute(
            select(League).where(
                League.name == new_name,
                League.country_id == new_country_id,
                League.id != league_id,
            )
        ).scalar_one_or_none()
        if duplicate_league:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="League with same name already exists for this country!",
            )
    updated_data = league_data.model_dump(exclude_unset=True)

    for key, val in updated_data.items():
        setattr(league, key, val)
    db.commit()
    db.refresh(league)
    return league


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league(
    league_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    league = db.execute(
        select(League).where(
            League.id == league_id,
        )
    ).scalar_one_or_none()
    if not league:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="league does not exist!",
        )
    try:
        db.delete(league)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete league with existing matches!",
        )
