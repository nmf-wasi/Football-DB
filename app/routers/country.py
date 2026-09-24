# POST : only name is required to create a countrry, but thats  fine, cause, unlike playersm there can't be duplicate counties
# UPDATE : use the same appraoch to avoid counting the country we are changing, only allowed to change : country
# DELETE : if a country gets deleted, players should be set to NULL but shouldn't the clubs be CASCADED? or set to None?


from fastapi import status, Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.database.database import get_db
from app.models.football import Country
from app.schemas.football import CountryResponse, CountryCreate, CountryUpdate

router = APIRouter()


@router.get("/", response_model=list[CountryResponse])
def get_countries(db: Session = Depends(get_db)):
    return db.execute(select(Country)).scalars().all()


@router.get("/{country_id}", response_model=CountryResponse)
def get_country(country_id: int, db: Session = Depends(get_db)):
    return db.execute(
        select(Country).where(Country.id == country_id)
    ).scalar_one_or_none()


@router.post("/", response_model=CountryResponse)
def create_Country(country_data: CountryCreate, db: Session = Depends(get_db)):
    country_exists = db.execute(
        select(Country).where(
            Country.name == country_data.name,
        )
    ).scalar_one_or_none()
    if country_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Country with same name already exists!",
        )

    new_country = Country()
    for key, val in country_data.model_dump().items():
        setattr(new_country, key, val)
    db.add(new_country)
    db.commit()
    db.refresh(new_country)
    return new_country


@router.patch("/{country_id}", response_model=CountryResponse)
def update_Country(
    country_id: int, country_data: CountryUpdate, db: Session = Depends(get_db)
):
    country = db.execute(
        select(Country).where(
            Country.id == country_id,
        )
    ).scalar_one_or_none()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country does not exist!",
        )

    updated_data = country_data.model_dump(exclude_unset=True)

    for key, val in updated_data.items():
        setattr(Country, key, val)
    db.commit()
    db.refresh(Country)
    return Country



@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(country_id: int, db: Session = Depends(get_db)):
    country = db.execute(select(Country).where(Country.id == country_id)).scalar_one_or_none()
    if not country:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Country does not exist!")
    try:
        db.delete(country)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete country with existing leagues!",
        )