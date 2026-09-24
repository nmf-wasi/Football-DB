# CREATE : NAME AND LONG NAME, CHECK THEM IG?
# UPDATE : CHECK ID TO AVOID COUNTING SAME THING TWICE FOR UNIQUE VALS AND EVERYTHING IS KINDA OPTIONAL, FIX THE SCHEMAS FIRST!
# DELETE : IF TEAM GETS DELETED, PLAYERS SHOULDN'T GET DELETED! BUT TEAM ATTRIBUTES SHOULD GET DELETED! -> CAN BE ARCHIVED, LIKE WE SEND A NEW PROPERTY WITH RESPONSE : ARCHIVED as status
# like we did for pagination response :
#  class PaginationResponse(BaseModel, Generic[T]):
# total: int
# skip: int
# limit: int
# items: list[T]

# TEAM ATTRIBUTES:
# CREATE : WHILE CREATING, IT'S BEST IF WE CAN SHOW A SCROLLING ELEMENT TO CHOOSE TEAMS FROM, INSTEAD OF SENDING A ID
# UPDATE : SAME LIKE OTHERS, JUST BE CAREFUL ABOUT DUPS
# DELETE : DELETING A TEAM ATTRIBUTES SHOULDN'T DELETE TEAMS!


# TODO: ADD RBAC
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.database.database import get_db
from app.schemas.football import (
    TeamResponse,
    TeamCreate,
    TeamUpdate,
    TeamAttributesResponse,
    TeamAttributesCreate,
    TeamAttributesUpdate,
)
from app.models.football import Team, TeamAttributes
from app.utils.slug import slugify

router = APIRouter()


@router.get("/teams", response_model=list[TeamResponse])
def get_teams(db: Session = Depends(get_db)):
    return db.execute(select(Team)).scalars().all()


@router.get("/teams/{team_id}", response_model=TeamResponse)
def get_team(team_id: int, db: Session = Depends(get_db)):
    return db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()


@router.post("/teams", response_model=TeamResponse)
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
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


@router.patch("/teams/{team_id}", response_model=TeamResponse)
def update_team(team_id: int, team_data: TeamUpdate, db: Session = Depends(get_db)):
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
def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    db.delete(team)
    db.commit()


@router.get("/teams/{team_id}/attributes", response_model=list[TeamAttributesResponse])
def get_team_attributes(team_id: int, db: Session = Depends(get_db)):
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
def get_team_attribute(team_id: int, attribute_id: int, db: Session = Depends(get_db)):
    team = db.execute(select(Team).where(Team.id == team_id)).scalar_one_or_none()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team not found!",
        )
    return (
        db.execute(
            select(TeamAttributes).where(
                TeamAttributes.team_id == team_id, TeamAttributes.id == attribute_id
            )
        )
        .scalars()
        .all()
    )


@router.post(
    "/teams/{team_id}/attributes",
    response_model=TeamAttributesResponse,
)
def create_team_attributes(
    team_id: int, team_attributes: TeamAttributesCreate, db: Session = Depends(get_db)
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
    team_id: int, attribute_id: int, db: Session = Depends(get_db)
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
    try:
        db.delete(team_attribute)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete team with existing matches!",
        )
