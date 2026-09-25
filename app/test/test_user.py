import pytest


@pytest.mark.user
def test_create_user(client):
    response = client.post(
        "/api/users/create_user",
        json={
            "username": "testuser",
            "email": "test@user.com",
            "password": "testpassword123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@user.com"
    assert "hashed_password" not in data


@pytest.mark.user
def test_duplicate_create_user(client):
    first_response = client.post(
        "/api/users/create_user",
        json={
            "username": "testuser",
            "email": "test@user.com",
            "password": "testpassword123",
        },
    )
    assert first_response.status_code == 200
    data = first_response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@user.com"
    assert "hashed_password" not in data

    second_response = client.post(
        "/api/users/create_user",
        json={
            "username": "testuser",
            "email": "test@user.com",
            "password": "testpassword123",
        },
    )
    assert second_response.status_code == 409
    data = second_response.json()
    assert data["detail"] == "Username already exists!"


@pytest.mark.user
def test_login(client):
    response = client.post(
        "api/users/create_user",
        json={
            "username": "testuser",
            "email": "test@user.com",
            "password": "testpassword123",
        },
    )
    data = response.json()
    assert data["username"] == "testuser"

    login_response = client.post(
        "api/users/login",
        data={
            "username": "testuser",
            "password": "testpassword123",
        },
    )
    assert login_response.status_code == 200
    login_data = login_response.json()
    assert "access_token" in login_data
    assert "refresh_token" in login_data

# test update user role later
