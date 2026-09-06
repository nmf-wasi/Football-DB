from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.database.database import get_db
from app.security.token import decode_token
from jose import JWTError
from app.models.user import User
from app.config.enums import UserRole

# use this route to take inputs
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """takes the jwt and finds the user and returns it"""

    # creating a credential exception, we will create that in a var

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials!",
    )
    try:
        # try decoding the jwt
        payload = decode_token(token)
        username: str | None = payload.get("sub")

        # check if user is none
        if username is None:
            raise credentials_exception

    # if it can't decode jwt
    except JWTError:
        raise credentials_exception

    # query db for username
    user = db.execute(
        select(User).where(User.username == username)
    ).scalar_one_or_none()

    # if it can't find user, raise exception
    if not user:
        raise credentials_exception
    # if user found, return it
    return user


def require_role(*allowed_roles: UserRole):
    """takes the required roles, finds the current user, checks if the current user has the rerquired roles, returns the user if current user has those roles, else raises Exceptions as forbidden"""

    # wrapper fun
    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return role_checker


# *allowed_roles -> u cna send multiple roles while calling the func