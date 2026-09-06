from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from datetime import date, datetime


class UserBase(BaseModel):
    """Base schema for creating user"""

    first_name: str | None = None
    last_name: str | None = None
    username: str
    birth_date: date | None = None
    phone_number: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating User"""

    password:str

    @field_validator("username")
    @classmethod
    def validate_username(cls, username: str) -> str:
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters!")
        return username

    @field_validator("birth_date")
    @classmethod
    def validate_birthdate(cls, birth_date: date) -> date | None:
        if birth_date and birth_date > date.today():
            raise ValueError("Future dates aren't allowed!")
        return birth_date


class UserResponse(UserBase):
    id:int
    model_config=ConfigDict(from_attributes=True)




class LoginResponse(BaseModel):
    access_token:str
    refresh_token:str
