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