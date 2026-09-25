import pytest
from app.models.football import League, Country

LEAGUE_PATH = "api/leagues"
LEAGUE_ID = 5


@pytest.mark.leagues
def test_get_leagues(client):
    response = client.get(f"{LEAGUE_PATH}")
    assert response.status_code == 200


@pytest.mark.leagues
def test_get_league_without_login(client):
    response = client.get(f"{LEAGUE_PATH}/{LEAGUE_ID}")
    assert response.status_code == 401


@pytest.mark.leagues
def test_get_league_with_login(general_client):
    response = general_client.get(f"{LEAGUE_PATH}/{LEAGUE_ID}")
    assert response.status_code == 404


@pytest.mark.leagues
def test_get_league_with_data(general_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    new_league = League(name="Test League", country_id=new_country.id)
    db_session.add(new_league)
    db_session.commit()
    db_session.refresh(new_league)

    response = general_client.get(f"{LEAGUE_PATH}/{new_league.id}")
    assert response.status_code == 200


@pytest.mark.leagues
def test_create_league(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    response = admin_client.post(
        f"{LEAGUE_PATH}",
        json={
            "name": "Test League",
            "country_id": new_country.id,
        },
    )

    assert response.status_code == 200


@pytest.mark.leagues
def test_create_league_duplicate(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    response = admin_client.post(
        f"{LEAGUE_PATH}",
        json={
            "name": "Test League",
            "country_id": new_country.id,
        },
    )

    assert response.status_code == 200
    response = admin_client.post(
        f"{LEAGUE_PATH}",
        json={
            "name": "Test League",
            "country_id": new_country.id,
        },
    )

    assert response.status_code == 409


@pytest.mark.leagues
def test_update_league(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    new_league = League(name="Test League", country_id=new_country.id)
    db_session.add(new_league)
    db_session.commit()
    db_session.refresh(new_league)

    response = admin_client.patch(
        f"{LEAGUE_PATH}/{new_league.id}",
        json={
            "name": "Test League Updated",
            "country_id": new_country.id,
        },
    )
    assert response.status_code == 200


@pytest.mark.leagues
def test_update_league_duplicate(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    first_league = League(name="first League", country_id=new_country.id)
    second_league = League(name="second League", country_id=new_country.id)
    db_session.add(first_league)
    db_session.add(second_league)
    db_session.commit()
    db_session.refresh(first_league)
    db_session.refresh(second_league)

    response = admin_client.patch(
        url=f"{LEAGUE_PATH}/{second_league.id}",
        json={
            "name": "first League",
        },
    )

    assert response.status_code == 409


@pytest.mark.leagues
def test_delete_league(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    new_league = League(name="test League", country_id=new_country.id)
    db_session.add(new_league)
    db_session.commit()
    db_session.refresh(new_league)
    response = admin_client.delete(url=f"{LEAGUE_PATH}/{new_league.id}")
    assert response.status_code == 204
