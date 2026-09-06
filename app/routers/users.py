from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User

from app.schemas.users import UserCreate, UserResponse, LoginResponse
from app.security.password import hash_password, verify_password
from app.security.token import create_access_token, create_refresh_token
from datetime import datetime

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


@router.post("/login", response_model=LoginResponse)
def login(
    user_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = db.execute(
        select(User).where(User.username == user_data.username)
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist!",
        )

    verified = verify_password(user_data.password, user.hashed_password)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Check username or password and try again!",
        )

    user.last_login = datetime.now()
    db.commit()
    db.refresh(user)

    access_token = create_access_token({"sub": user.username})
    refresh_token = create_refresh_token({"sub": user.username})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

