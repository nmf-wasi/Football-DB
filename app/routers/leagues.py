# CREATE : check nae and league id before adding, to avoid dups
# UPDATE : same, as players, use LEAGUE.id!=league_id to avoid dups
# DELETE : IF THE LEAGUE GETS DELETED, WHAT HAPPENS TO THE CLUBS AND PLAYERS? -> league doesn't contain any clubs or player so it will be fine ig?


from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database.database import get_db
from app.models.football import League, Country
from app.schemas.football import LeagueResponse, LeagueCreate, LeagueUpdate

router = APIRouter()


@router.get("/", response_model=list[LeagueResponse])
def get_leagues(db: Session = Depends(get_db)):
    return db.execute(select(League)).scalars().all()


@router.get("/{league_id}", response_model=LeagueResponse)
def get_league(league_id: int, db: Session = Depends(get_db)):
    return db.execute(select(League).where(League.id == league_id)).scalar_one_or_none()


@router.post("/", response_model=LeagueResponse)
def create_league(league_data: LeagueCreate, db: Session = Depends(get_db)):
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
    league_id: int, league_data: LeagueUpdate, db: Session = Depends(get_db)
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
    new_country_id = league_data.country_id if league_data.country_id is not None else league.country_id

    if league_data.name is not None or league_data.country_id is not None:
        duplicate_league = db.execute(
            select(League).where(
                League.name == new_name,
                League.country_id == new_country_id,
                League.id != league_id,
            )
        ).scalar_one_or_none()
        if duplicate_league:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="League with same name already exists for this country!")
    updated_data = league_data.model_dump(exclude_unset=True)

    for key, val in updated_data.items():
        setattr(league, key, val)
    db.commit()
    db.refresh(league)
    return league


@router.delete("/{league_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_league(league_id: int, db: Session = Depends(get_db)):
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