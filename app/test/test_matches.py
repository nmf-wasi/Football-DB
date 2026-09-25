import pytest
from app.models.football import Team, Match

MATCH_PATH = "api/matches"
MATCH_ID = 55


@pytest.mark.matches
def test_get_matches(client):
    response = client.get(f"{MATCH_PATH}")
    assert response.status_code == 200


@pytest.mark.matches
def test_get_match_without_login(client):
    response = client.get(f"{MATCH_PATH}/{MATCH_ID}")
    assert response.status_code == 401


@pytest.mark.matches
def test_get_match_with_login(general_client):
    response = general_client.get(f"{MATCH_PATH}/{MATCH_ID}")
    assert response.status_code == 404


@pytest.mark.matches
def test_get_match_with_data(general_client, db_session):
    first_team = Team(
        team_long_name="first Team", team_short_name="first", slug="first"
    )
    second_team = Team(
        team_long_name="second Team", team_short_name="second", slug="second"
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
    db_session.refresh(new_match)
    response = general_client.get(f"{MATCH_PATH}/{new_match.id}")
    assert response.status_code == 200


@pytest.mark.matches
def test_create_match(admin_client, db_session):
    first_team = Team(
        team_long_name="first Team", team_short_name="first", slug="first"
    )
    second_team = Team(
        team_long_name="second Team", team_short_name="second", slug="second"
    )
    db_session.add_all([first_team, second_team])
    db_session.commit()
    db_session.refresh(first_team)
    db_session.refresh(second_team)

    response = admin_client.post(
        url=f"{MATCH_PATH}",
        json={
            "home_team_id": first_team.id,
            "away_team_id": second_team.id,
            "date": "2026-05-30",
        },
    )
    assert response.status_code == 200


@pytest.mark.matches
def test_duplicate_create_match(admin_client, db_session):
    first_team = Team(
        team_long_name="first Team", team_short_name="first", slug="first"
    )
    second_team = Team(
        team_long_name="second Team", team_short_name="second", slug="second"
    )
    db_session.add_all([first_team, second_team])
    db_session.commit()
    db_session.refresh(first_team)
    db_session.refresh(second_team)

    response = admin_client.post(
        url=f"{MATCH_PATH}",
        json={
            "home_team_id": first_team.id,
            "away_team_id": second_team.id,
            "date": "2026-05-30",
        },
    )
    assert response.status_code == 200
    response = admin_client.post(
        url=f"{MATCH_PATH}",
        json={
            "home_team_id": first_team.id,
            "away_team_id": second_team.id,
            "date": "2026-05-30",
        },
    )
    assert response.status_code == 409


@pytest.mark.matches
def test_update_match(admin_client, db_session):
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
    db_session.refresh(new_match)

    response = admin_client.patch(
        f"{MATCH_PATH}/{new_match.id}",
        json={
            "home_team_id": first_team.id,
            "away_team_id": second_team.id,
            "date": "2026-05-30",
        },
    )
    assert response.status_code == 200


@pytest.mark.matches
def test_duplicate_update_match(admin_client, db_session):
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

    first_match = Match(
        home_team_id=first_team.id, away_team_id=second_team.id, date="2026-05-30"
    )
    second_match = Match(
        home_team_id=first_team.id, away_team_id=second_team.id, date="2026-04-30"
    )
    db_session.add_all([first_match, second_match])
    db_session.commit()
    db_session.refresh(first_match)
    db_session.refresh(second_match)

    response = admin_client.patch(
        f"{MATCH_PATH}/{second_match.id}",
        json={
            "home_team_id": first_team.id,
            "away_team_id": second_team.id,
            "date": "2026-05-30",
        },
    )
    assert response.status_code == 409


@pytest.mark.matches
def test_delete_match(admin_client, db_session):
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

    first_match = Match(
        home_team_id=first_team.id, away_team_id=second_team.id, date="2026-05-30"
    )
    db_session.add(first_match)
    db_session.commit()
    db_session.refresh(first_match)

    response = admin_client.delete(f"{MATCH_PATH}/{first_match.id}")
    assert response.status_code == 204

@pytest.mark.matches
def test_partial_update_match(admin_client, db_session):
    first_team = Team(team_long_name="first Team", team_short_name="first", slug="first")
    second_team = Team(team_long_name="second Team", team_short_name="second", slug="second")
    db_session.add_all([first_team, second_team])
    db_session.commit()
    db_session.refresh(first_team)
    db_session.refresh(second_team)

    new_match = Match(
        home_team_id=first_team.id, away_team_id=second_team.id, date="2026-05-30"
    )
    db_session.add(new_match)
    db_session.commit()
    db_session.refresh(new_match)

    response = admin_client.patch(
        f"{MATCH_PATH}/{new_match.id}",
        json={"stage": 3},
    )
    assert response.status_code == 200
    assert response.json()["stage"] == 3