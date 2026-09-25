import pytest
from app.models.football import Team, Match, Player
from datetime import date, timedelta

PLAYER_PATH = "/api/players"
OLD_DATE = "2026-05-30"
FUTURE_DATE = (date.today() + timedelta(days=1)).isoformat()


@pytest.mark.players
def test_get_players(client):
    response = client.get(
        PLAYER_PATH,
    )
    assert response.status_code == 200


@pytest.mark.players
def test_get_player_blank(general_client):
    response = general_client.get(
        f"{PLAYER_PATH}/25",
    )
    assert response.status_code == 404


@pytest.mark.players
def test_get_players_with_data(general_client, db_session):
    new_player = Player(
        player_name="test player",
        birthday=OLD_DATE,
        slug="test",
    )
    db_session.add(new_player)
    db_session.commit()
    db_session.refresh(new_player)

    response = general_client.get(
        f"{PLAYER_PATH}/{new_player.id}",
    )
    assert response.status_code == 200


@pytest.mark.players
def test_create_player_as_general_user(general_client):
    response = general_client.post(
        f"{PLAYER_PATH}",
        json={
            "player_name": "test player",
            "birthday": OLD_DATE,
        },
    )
    assert response.status_code == 403


@pytest.mark.players
def test_create_player_as_admin(admin_client):
    response = admin_client.post(
        f"{PLAYER_PATH}",
        json={
            "player_name": "test player",
            "birthday": OLD_DATE,
        },
    )
    assert response.status_code == 200


@pytest.mark.players
def test_create_player_with_future_date(admin_client):
    response = admin_client.post(
        f"{PLAYER_PATH}",
        json={
            "player_name": "test player",
            "birthday": FUTURE_DATE,
        },
    )
    assert response.status_code == 422
    errors = response.json()["detail"]

    assert any(
        error["loc"] == ["body", "birthday"]
        and "Birthday cannot be in the future" in error["msg"]
        for error in errors
    )


@pytest.mark.players
def test_create_player_duplicate(admin_client):
    first_response = admin_client.post(
        f"{PLAYER_PATH}",
        json={
            "player_name": "first test player",
            "birthday": OLD_DATE,
        },
    )
    assert first_response.status_code == 200
    second_response = admin_client.post(
        f"{PLAYER_PATH}",
        json={
            "player_name": "first test player",
            "birthday": OLD_DATE,
        },
    )
    assert second_response.status_code == 409


@pytest.mark.players
def test_update_player(admin_client, db_session):
    first_player = Player(
        player_name="first test player",
        birthday=OLD_DATE,
        slug="first",
    )
    second_player = Player(
        player_name="second test player",
        birthday=OLD_DATE,
        slug="second",
    )
    db_session.add_all([first_player, second_player])
    db_session.commit()
    db_session.refresh(first_player)
    db_session.refresh(second_player)

    first_response = admin_client.patch(
        f"{PLAYER_PATH}/{first_player.id}",
        json={
            "player_name": "First test player",
        },
    )
    assert first_response.status_code == 200
    second_response = admin_client.patch(
        f"{PLAYER_PATH}/{second_player.id}",
        json={
            "player_name": "First test player",
        },
    )
    assert second_response.status_code == 409

@pytest.mark.players
def test_delete_player(admin_client, db_session):
    first_player = Player(
        player_name="first test player",
        birthday=OLD_DATE,
        slug="first",
    )

    db_session.add(first_player)
    db_session.commit()
    db_session.refresh(first_player)

    response = admin_client.delete(
        f"{PLAYER_PATH}/{first_player.id}",
    )
    assert response.status_code == 204
