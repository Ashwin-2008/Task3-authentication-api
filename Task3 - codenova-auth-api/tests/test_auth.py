
def test_register_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "ashwin",
            "email": "ashwin@example.com",
            "password": "SecurePass@123",
        },
    )

    assert response.status_code == 201
    assert response.json()["email"] == "ashwin@example.com"
    assert "hashed_password" not in response.json()


def test_duplicate_email(client):
    payload = {
        "username": "ashwin",
        "email": "ashwin@example.com",
        "password": "SecurePass@123",
    }

    assert client.post(
        "/api/v1/auth/register", json=payload
    ).status_code == 201

    payload["username"] = "another_user"

    response = client.post(
        "/api/v1/auth/register", json=payload
    )

    assert response.status_code == 409


def test_weak_password_rejected(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "ashwin",
            "email": "ashwin@example.com",
            "password": "weakpassword",
        },
    )

    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "ashwin",
            "email": "ashwin@example.com",
            "password": "SecurePass@123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ashwin@example.com",
            "password": "SecurePass@123",
        },
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_wrong_password(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "ashwin",
            "email": "ashwin@example.com",
            "password": "SecurePass@123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ashwin@example.com",
            "password": "WrongPass@123",
        },
    )

    assert response.status_code == 401
