from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.schemas.users import UserCreate, UserResponse, LoginResponse, RefreshRequest
from app.security.password import hash_password, verify_password
from app.security.token import create_access_token, create_refresh_token
from app.dependency import get_current_user
from app.security.token import decode_token

from datetime import datetime
from jose import JWTError

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


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    """The dependency returns the current user and it returns that user"""
    return current_user


@router.post("/refresh", response_model=LoginResponse)
def refresh_access_token(request: RefreshRequest, db: Session = Depends(get_db)):
    """take the old refresh token, check if the user exists from payload and return new access and refresh tokens"""
    try:
        # find the username from payload and find user with it
        payload = decode_token(request.refresh_token)
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Refresh Token!",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Refresh Token!",
        )

    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found!",
        )

    new_access_token = create_access_token({"sub": username})
    new_refresh_token = create_refresh_token({"sub": username})

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }

