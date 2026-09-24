from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc
from app.database.database import get_db
from app.models.football import Player, PlayerAttributes
from app.schemas.football import (
    PlayerResponse,
    PlayerCreate,
    PlayerUpdate,
    PlayerAttributesCreate,
    PlayerAttributesResponse,
    PaginationResponse,
)
from app.utils.slug import slugify
from app.models.user import User
from app.dependency import require_role
from app.config.enums import UserRole, PlayerSortFields, SortOrder

router = APIRouter()


@router.get("/", response_model=PaginationResponse[PlayerResponse])
def get_players(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: PlayerSortFields = PlayerSortFields.NAME,
    order_by: SortOrder = SortOrder.ASC,
    db: Session = Depends(get_db),
):
    # get value for sort and order bby
    sort_column = getattr(Player, sort_by.value)
    order_func = desc if order_by == SortOrder.DESC else asc

    # base queryset
    queryset = select(Player)
    count_queryset = select(func.count()).select_from(Player)

    # sort
    queryset=queryset.order_by(order_func(sort_column))

    # pagination
    queryset = queryset.offset(skip).limit(limit)
    return {
        "total": db.execute(count_queryset).scalar_one(),
        "skip": skip,
        "limit": limit,
        "items": db.execute(queryset).scalars().all(),
    }


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player does not exist!",
        )
    return player


@router.post("/", response_model=PlayerResponse)
def create_player(
    player_data: PlayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """We use player name and birth date to check already existing player, if not found, then create player"""

    player_exists = db.execute(
        select(Player).where(
            Player.player_name == player_data.player_name,
            Player.birthday == player_data.birthday,
        )
    ).scalar_one_or_none()

    if player_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Player already exists!",
        )
    new_player = Player()
    for key, value in player_data.model_dump().items():
        setattr(new_player, key, value)

    existing_slugs = set(db.execute(select(Player.slug)).scalars().all())
    new_slug = slugify(player_data.player_name, existing_slugs)
    new_player.slug = new_slug
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return new_player


@router.patch("/{player_id}", response_model=PlayerResponse)
def update_player(
    player_id: int,
    player_data: PlayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player does not exist!",
        )

    new_name = (
        player_data.player_name
        if player_data.player_name is not None
        else player.player_name
    )
    new_birthday = (
        player_data.birthday if player_data.birthday is not None else player.birthday
    )

    if player_data.player_name is not None or player_data.birthday is not None:
        duplicate = db.execute(
            select(Player).where(
                Player.player_name == new_name,
                Player.birthday == new_birthday,
                Player.id != player_id,  # exclude the player being updated themselves
            )
        ).scalar_one_or_none()
        if duplicate:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Player already exists!"
            )

    updated_data = player_data.model_dump(exclude_unset=True)
    for key, val in updated_data.items():
        setattr(player, key, val)

    if player_data.player_name:
        existing_slugs = set(
            db.execute(select(Player.slug).where(Player.id != player_id))
            .scalars()
            .all()
        )  # getting slugs like this is costly, need better way to handle it later
        new_slug = slugify(player_data.player_name, existing_slugs)
        player.slug = new_slug
    db.commit()
    db.refresh(player)
    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_player(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if player is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player does not exist!",
        )
    db.delete(player)
    db.commit()


# PLAYER ATTRIBUTES


@router.get("/{player_id}/attributes", response_model=list[PlayerAttributesResponse])
def get_player_attributes(
    player_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player does not exist!",
        )
    return (
        db.execute(
            select(PlayerAttributes).where(PlayerAttributes.player_id == player_id)
        )
        .scalars()
        .all()
    )


@router.get(
    "/{player_id}/attributes/{attribute_id}", response_model=PlayerAttributesResponse
)
def get_player_attribute(
    player_id: int,
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player does not exist!",
        )
    player_attribute = db.execute(
        select(PlayerAttributes).where(
            PlayerAttributes.id == attribute_id,
            PlayerAttributes.player_id == player_id,
        )
    ).scalar_one_or_none()
    if not player_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player attribute does not exist!",
        )

    return player_attribute


@router.post("/{player_id}/attributes", response_model=PlayerAttributesResponse)
def create_player_attributes(
    player_id: int,
    player_attr_data: PlayerAttributesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.USER)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player does not exist!",
        )
    new_player_attribute = PlayerAttributes()
    for key, value in player_attr_data.model_dump().items():
        setattr(new_player_attribute, key, value)
    new_player_attribute.player = player
    db.add(new_player_attribute)
    db.commit()
    db.refresh(new_player_attribute)
    return new_player_attribute


@router.delete(
    "/{player_id}/attributes/{attribute_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_player_attribute(
    player_id: int,
    attribute_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    player = db.execute(
        select(Player).where(Player.id == player_id)
    ).scalar_one_or_none()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found!",
        )

    player_attribute = db.execute(
        select(PlayerAttributes).where(
            PlayerAttributes.player_id == player_id,
            PlayerAttributes.id == attribute_id,
        )
    ).scalar_one_or_none()
    if not player_attribute:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Team Attribute not found!",
        )

    db.delete(player_attribute)
    db.commit()
