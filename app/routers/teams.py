from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, func, asc, desc, or_
from app.database.database import get_db
from app.schemas.football import (
    TeamResponseDetail,
    TeamResponseShort,
    TeamCreate,
    TeamUpdate,
    TeamAttributesResponse,
    TeamAttributesCreate,
    TeamAttributesUpdate,
    PaginationResponse,
)
from app.models.football import Team, TeamAttributes
from app.utils.slug import slugify
from app.models.user import User
from app.dependency import require_role
from app.config.enums import UserRole, TeamSortFields, SortOrder

router = APIRouter()


@router.get("/teams", response_model=PaginationResponse[TeamResponseShort])
def get_teams(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: TeamSortFields = TeamSortFields.TEAM_SHORT_NAME,
    order_by: SortOrder = SortOrder.ASC,
    search: str | None = Query(None, min_length=1, max_length=24),
    db: Session = Depends(get_db),
):
    # get sort and order by attributes
    sort_column = getattr(Team, sort_by.value)
    order_func = desc if order_by == SortOrder.DESC else asc

    # base queryset
    queryset = select(Team)
    count_queryset = select(func.count()).select_from(Team)

    # filters
    filters = []
    # search
    if search is not None:
        filters.append(
            or_(
                Team.team_long_name.ilike(f"%{search}%"),
                Team.team_short_name.ilike(f"%{search}%"),
            )
        )

    # apply filters
    queryset = queryset.where(*filters)
    count_queryset = count_queryset.where(*filters)

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


@router.get("/teams/{team_id}", response_model=TeamResponseDetail)
def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    return db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()


@router.post("/teams", response_model=TeamResponseDetail)
def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    team_exists = db.execute(
        select(Team).where(
            Team.team_long_name == team_data.team_long_name,
        )
    ).scalar_one_or_none()

    if team_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team with same full name already exists!",
        )
    team_exists = db.execute(
        select(Team).where(
            Team.team_short_name == team_data.team_short_name,
        )
    ).scalar_one_or_none()

    if team_exists is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Team with same short name already exists!",
        )

    new_team = Team()
    for key, value in team_data.model_dump().items():
        setattr(new_team, key, value)
    existing_slugs = db.execute(select(Team.slug)).scalars().all()

    new_slug = slugify(team_data.team_short_name, existing_slugs)
    new_team.slug = new_slug
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


@router.patch("/teams/{team_id}", response_model=TeamResponseDetail)
def update_team(
    team_id: int,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    if team_data.team_short_name:
        duplicate = db.execute(
            select(Team).where(
                Team.team_short_name == team_data.team_short_name, Team.id != team_id
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team with same short name already exists!",
            )
    if team_data.team_long_name:
        duplicate = db.execute(
            select(Team).where(
                Team.team_long_name == team_data.team_long_name, Team.id != team_id
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team with same full name already exists!",
            )

    updated_data = team_data.model_dump(exclude_unset=True)
    for key, val in updated_data.items():
        setattr(team, key, val)
    if team_data.team_short_name is not None:
        existing_slugs = set(db.execute(select(Team.slug)).scalars().all())
        new_slug = slugify(team_data.team_short_name, existing_slugs)
        team.slug = new_slug
    db.commit()
    db.refresh(team)
    return team


@router.delete("/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    try:
        db.delete(team)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete team with existing matches!",
        )


@router.get("/teams/{team_id}/attributes", response_model=list[TeamAttributesResponse])
def get_team_attributes(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    return (
        db.execute(select(TeamAttributes).where(TeamAttributes.team_id == team_id))
        .scalars()
        .all()
    )


@router.get(
    "/teams/{team_id}/attributes/{attribute_id}",
    response_model=TeamAttributesResponse,
)
def get_team_attribute(
    team_id: int,
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    team_attribute = db.execute(
        select(TeamAttributes).where(
            TeamAttributes.team_id == team_id, TeamAttributes.id == attribute_id
        )
    ).scalar_one_or_none()
    if not team_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team attribute not found!"
        )
    return team_attribute


@router.post(
    "/teams/{team_id}/attributes",
    response_model=TeamAttributesResponse,
)
def create_team_attributes(
    team_id: int,
    team_attributes: TeamAttributesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    new_team_attributes = TeamAttributes()
    for key, val in team_attributes.model_dump().items():
        setattr(new_team_attributes, key, val)
    db.add(new_team_attributes)
    db.commit()
    db.refresh(new_team_attributes)
    return new_team_attributes


@router.patch(
    "/teams/{team_id}/attributes/{attribute_id}",
    response_model=TeamAttributesResponse,
)
def update_team_attribute(
    team_id: int,
    attribute_id: int,
    attribute_data: TeamAttributesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )

    team_attribute = db.execute(
        select(TeamAttributes).where(
            TeamAttributes.team_id == team_id,
            TeamAttributes.id == attribute_id,
        )
    ).scalar_one_or_none()
    if not team_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team Attribute not found!",
        )

    updated_data = attribute_data.model_dump(exclude_unset=True)
    for key, val in updated_data.items():
        setattr(team_attribute, key, val)

    db.commit()
    db.refresh(team_attribute)
    return team_attribute


@router.delete(
    "/teams/{team_id}/attributes/{attribute_id}", status_code=status.HTTP_204_NO_CONTENT
)
def delete_team_attribute(
    team_id: int,
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )

    team_attribute = db.execute(
        select(TeamAttributes).where(
            TeamAttributes.team_id == team_id,
            TeamAttributes.id == attribute_id,
        )
    ).scalar_one_or_none()
    if not team_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team Attribute not found!",
        )

    db.delete(team_attribute)
    db.commit()
