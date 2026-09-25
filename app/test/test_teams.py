import pytest
from app.models.football import Team, Match

TEAM_PATH = "/api/teams"


@pytest.mark.teams
def test_get_teams(client):
    response = client.get(
        TEAM_PATH,
    )
    assert response.status_code == 200


@pytest.mark.teams
def test_get_team_blank(general_client):
    response = general_client.get(
        f"{TEAM_PATH}/25",
    )
    assert response.status_code == 404


@pytest.mark.teams
def test_get_team_with_data(general_client, db_session):
    new_team = Team(
        team_long_name="Test Team",
        team_short_name="test",
        slug="test",
    )
    db_session.add(new_team)
    db_session.commit()
    db_session.refresh(new_team)

    response = general_client.get(
        f"{TEAM_PATH}/{new_team.id}",
    )
    assert response.status_code == 200


@pytest.mark.teams
def test_create_team_as_general_user(general_client):
    response = general_client.post(
        f"{TEAM_PATH}",
        json={
            "team_long_name": "Test Team",
            "team_short_name": "test",
            "slug": "test",
        },
    )
    assert response.status_code == 403


@pytest.mark.teams
def test_create_team_as_admin(
    admin_client,
):
    response = admin_client.post(
        f"{TEAM_PATH}",
        json={
            "team_long_name": "Test Team",
            "team_short_name": "test",
            "slug": "test",
        },
    )
    assert response.status_code == 200


@pytest.mark.teams
def test_create_team_duplicate(admin_client):
    first_response = admin_client.post(
        f"{TEAM_PATH}",
        json={
            "team_long_name": "Test Team",
            "team_short_name": "test",
            "slug": "test",
        },
    )
    assert first_response.status_code == 200
    second_response = admin_client.post(
        f"{TEAM_PATH}",
        json={
            "team_long_name": "Test Team",
            "team_short_name": "test",
            "slug": "test",
        },
    )
    assert second_response.status_code == 409


@pytest.mark.teams
def test_update_team(admin_client, db_session):
    first_team = Team(
        team_long_name="first Team",
        team_short_name="first",
        slug="first",
    )
    second_team = Team(
        team_long_name="second Team",
        team_short_name="second",
        slug="second",
    )
    db_session.add_all([first_team, second_team])
    db_session.commit()
    db_session.refresh(first_team)
    db_session.refresh(second_team)

    response = admin_client.patch(
        f"{TEAM_PATH}/{second_team.id}",
        json={
            "team_long_name": "first Team",
            "team_short_name": "first",
            "slug": "first",
        },
    )
    assert response.status_code == 409


@pytest.mark.teams
def test_delete_team(admin_client):
    first_response = admin_client.post(
        f"{TEAM_PATH}",
        json={
            "team_long_name": "Test Team",
            "team_short_name": "test",
            "slug": "test",
        },
    )
    first_response_data = first_response.json()
    team_id = first_response_data["id"]

    second_response = admin_client.delete(
        f"{TEAM_PATH}/{team_id}",
    )
    assert second_response.status_code == 204


@pytest.mark.teams
def test_delete_team_prevention(admin_client, db_session):
    first_team = Team(
        team_long_name="first Team",
        team_short_name="first",
        slug="first",
    )
    second_team = Team(
        team_long_name="second Team",
        team_short_name="second",
        slug="second",
    )
    db_session.add_all([first_team, second_team])
    db_session.commit()
    db_session.refresh(first_team)
    db_session.refresh(second_team)

    new_match = Match(
        home_team_id=first_team.id, away_team_id=second_team.id, date="2026-05-30"
    )
    db_session.add(new_match)
    db_session.commit()
    deletion_response = admin_client.delete(
        url=f"{TEAM_PATH}/{first_team.id}",
    )
    assert deletion_response.status_code == 409
