import os

os.environ["TESTING"] = "TRUE"
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database.database import Base, get_db
from app.src.main import app
from app.models.user import User
from app.models.football import Player, Team, League, Country, Match
from app.config.settings import settings
from app.security.password import hash_password
from app.config.enums import UserRole

engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture
def db_session():
    """Builds every table fresh and hands the test a working session, once test is done, closes the session and wipes every table, ensuring every single test starts from a completely clean, empty database"""
    Base.metadata.create_all(bind=engine)  # builds every table on test.db
    session = TestingSessionLocal()
    try:
        yield session  # gives a fresh session to the api
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)  # unhook everything after that


@pytest.fixture
def client(db_session):
    def override_get_db():
        """provies a session from test db instead of original get_db func of database file"""
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db_session):
    """take a fresh db session, inserts a new admin user"""

    user = User(
        username="admin_test",
        email="admin@test.com",
        hashed_password=hash_password("testPassword123"),
        user_role=UserRole.ADMIN,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_client(client, admin_user):
    """user admin user so that before login, the user exists in db and calls actual login route to login"""
    response = client.post(
        "/api/users/login",
        data={
            "username": "admin_test",
            "password": "testPassword123",
        },
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def general_user(db_session):
    """take a fresh db session, inserts a new normal user"""

    user = User(
        username="user_test",
        email="user@test.com",
        hashed_password=hash_password("testPassword123"),
        user_role=UserRole.USER,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def general_client(client, general_user):
    """user general user so that before login, the user exists in db and calls actual login route to login"""
    response = client.post(
        "/api/users/login",
        data={
            "username": "user_test",
            "password": "testPassword123",
        },
    )
    token = response.json()["access_token"]
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client
