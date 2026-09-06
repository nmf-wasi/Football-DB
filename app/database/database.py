from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config.settings import settings

engine = create_engine(settings.DATABASE_URL)
connect_args = {"check_same_thread": False}

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)


class Base(DeclarativeBase):
    """Every model on this project inherit from this Base Class"""

    pass


def get_db():
    """fast api dependency, yields a db session for duration of one one request and then closes it"""
    with SessionLocal() as db:
        yield db
