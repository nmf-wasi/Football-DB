# CREATE : IDK HOW TO CHECK DUPLICATES HERE TBH, BUT I WILL THINK ABOUT IT WHEN I DO IT
# UPDATE : CHECK IF THE COUNTRY THEY ARE SETTING, EXISTS OR NOT, BETTER, GIVE THEM A SCROLLABLE LIST TO PICK FROM, DONT GIVE THEM OPTIONS TO SEND
# DELETE : DELETING MATCHES SHOULDN'T BE DELETING TEAMS OR LEAGUES

from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.database import get_db
from app.models.football import Match, Team, Country, League
from app.schemas.football import MatchResponse, MatchCreate, MatchUpdate

router = APIRouter()


@router.get("/", response_model=list[MatchResponse])
def get_matches(db: Session = Depends(get_db)):
    return db.execute(select(Match)).scalars().all()


@router.get("/{match_id}", response_model=MatchResponse)
def get_match(match_id: int, db: Session = Depends(get_db)):
    return db.execute(select(Match).where(Match.id == match_id)).scalar_one_or_none()


@router.post("/", response_model=MatchResponse)
def create_match(match_data: MatchCreate, db: Session = Depends(get_db)):
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
def update_match(match_id: int, match_data: MatchUpdate, db: Session = Depends(get_db)):
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
def delete_match(match_id: int, db: Session = Depends(get_db)):
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
