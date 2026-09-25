import pytest
from app.models.football import Country

COUNTRY_PATH = "api/countries"
COUNTRY_ID = 5


@pytest.mark.countries
def test_get_countries(client):
    response = client.get(url=COUNTRY_PATH)
    assert response.status_code == 200


@pytest.mark.countries
def test_get_country_without_login(client):
    response = client.get(url=f"{COUNTRY_PATH}/{COUNTRY_ID}")
    assert response.status_code == 401


@pytest.mark.countries
def test_get_country_with_login(general_client):
    response = general_client.get(f"{COUNTRY_PATH}/{COUNTRY_ID}")
    assert response.status_code == 404


@pytest.mark.countries
def test_get_country_with_data(general_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    response = general_client.get(f"{COUNTRY_PATH}/{new_country.id}")
    assert response.status_code == 200


@pytest.mark.countries
def test_create_country(admin_client):
    response = admin_client.post(url=f"{COUNTRY_PATH}", json={"name": "Test Country"})
    assert response.status_code == 200


@pytest.mark.countries
def test_duplicate_create_country(admin_client):
    response = admin_client.post(url=f"{COUNTRY_PATH}", json={"name": "Test Country"})
    assert response.status_code == 200
    response = admin_client.post(url=f"{COUNTRY_PATH}", json={"name": "Test Country"})
    assert response.status_code == 409


@pytest.mark.countries
def test_update_country(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)
    response = admin_client.patch(
        f"{COUNTRY_PATH}/{new_country.id}", json={"name": "Updated Country"}
    )
    assert response.status_code == 200


@pytest.mark.countries
def test_duplicate_update_country(admin_client, db_session):
    first_country = Country(name="first Country")
    second_country = Country(name="second Country")
    db_session.add_all([first_country, second_country])
    db_session.commit()
    db_session.refresh(first_country)
    db_session.refresh(second_country)

    response = admin_client.patch(
        url=f"{COUNTRY_PATH}/{second_country.id}", json={"name": "first Country"}
    )
    assert response.status_code == 409


@pytest.mark.countries
def test_delete_country(admin_client, db_session):
    new_country = Country(name="Test Country")
    db_session.add(new_country)
    db_session.commit()
    db_session.refresh(new_country)

    response = admin_client.delete(url=f"{COUNTRY_PATH}/{new_country.id}")
    assert response.status_code == 204
