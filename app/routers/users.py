from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

from app.schemas.users import UserCreate, UserResponse
from app.security.password import hash_password, verify_password

router = APIRouter()


@router.post("/create_user", response_model=UserResponse)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user_exists = db.execute(
        select(User).where(User.username == user_data.username)
    ).scalar_one_or_none()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists!",
        )
    user_exists = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered!",
        )

    hashed_password = hash_password(user_data.password)
    new_user = User()
    for key, value in user_data.model_dump().items():
        if key == "password":
            continue
        setattr(new_user, key, value)
    new_user.hashed_password = hashed_password
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
