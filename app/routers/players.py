from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.database import get_db
from app.models.football import Player
from app.schemas.football import PlayerResponse, PlayerCreate

router = APIRouter()


@router.get("/", response_model=list[PlayerResponse])
def get_players(db: Session = Depends(get_db)):
    return db.execute(select(Player)).scalars().all()


@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    return db.execute(select(Player).where(Player.id == player_id)).scalar_one_or_none()


@router.post("/", response_model=PlayerResponse)
def create_player(player_data: PlayerCreate, db: Session = Depends(get_db)):
    """a dummy version, we will check duplicate players later"""
    pass
    # we don't have any solid check if some someone wanted to create duplciate players, we can either go with one more mandatory attribute or something that can check it, another way could be, add nation first, before adding a player from that nation


# UPDATE : we can check using ID to see duplicates, can use Player.id!=player_id for excluding same player
# DELTE : WHEN WE DELETE A PLAYER, DO THEIR ATTRIBUTES DISAPPEAR TOO?

# PLAYER ATTRIBUTES

# POST : USE RBAC TO restrict commoners, just let the admins in
# UPDATE : patch
# DELETE : Set player's attr to none, players shouldnt be deleted
