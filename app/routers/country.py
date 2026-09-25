from fastapi import status, Depends, APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from sqlalchemy.exc import IntegrityError
from app.database.database import get_db
from app.models.football import Country
from app.schemas.football import (
    CountryResponse,
    CountryCreate,
    CountryUpdate,
    PaginationResponse,
)
from app.models.user import User
from app.dependency import require_role
from app.config.enums import UserRole, SortOrder, CountrySortField

router = APIRouter()


@router.get("/", response_model=PaginationResponse[CountryResponse])
def get_countries(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: CountrySortField = CountrySortField.NAME,
    order_by: SortOrder = SortOrder.ASC,
    search: str | None = Query(None, min_length=1, max_length=24),
    db: Session = Depends(get_db),
):
    # get sort and order by val
    sort_column = getattr(Country, sort_by)
    order_func = desc if order_by == SortOrder.DESC else asc

    # base queryset
    queryset = select(Country)
    count_queryset = select(func.count()).select_from(Country)

    # filters -> don't have any fields to filter with, just using search
    filters = []
    # search
    if search:
        filters.append(Country.name.ilike(f"%{search}%"))

    # apply the filters
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


@router.get("/{country_id}", response_model=CountryResponse)
def get_country(
    country_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    country = db.execute(
        select(Country).where(Country.id == country_id)
    ).scalar_one_or_none()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Country does not exist!",
        )
    return country


@router.post("/", response_model=CountryResponse)
def create_Country(
    country_data: CountryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
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
    country_id: int,
    country_data: CountryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
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

    new_country_name = (
        country_data.name if country_data.name is not None else country.name
    )
    duplicate_exists = db.execute(
        select(Country).where(
            Country.name == new_country_name, Country.id != country_id
        )
    ).scalar_one_or_none()
    if duplicate_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Country with similar name already exists!",
        )
    updated_data = country_data.model_dump(exclude_unset=True)

    for key, val in updated_data.items():
        setattr(country, key, val)
    db.commit()
    db.refresh(country)
    return country


@router.delete("/{country_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_country(
    country_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    country = db.execute(
        select(Country).where(Country.id == country_id)
    ).scalar_one_or_none()
    if not country:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Country does not exist!"
        )
    try:
        db.delete(country)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete country with existing leagues!",
        )
