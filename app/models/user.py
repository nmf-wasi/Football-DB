from sqlalchemy import Integer, String, Date, DateTime, Enum as SQLEnum
from sqlalchemy.orm import mapped_column, Mapped
from app.database.database import Base
from datetime import date, datetime
from app.config.enums import UserRole


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String, nullable=True, unique=True)
    email: Mapped[str] = mapped_column(String, unique=True)

    user_role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole, name="user_role"),default=UserRole.USER)

    hashed_password: Mapped[str] = mapped_column(String)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now, onupdate=datetime.now
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )
    # dont call datetime.now() or else it will be executed everytime we touch a row
