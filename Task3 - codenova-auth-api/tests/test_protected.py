
def test_profile_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401


def test_profile_with_invalid_token(client):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )

    assert response.status_code == 401


def test_profile_with_valid_token(client):
    client.post(
        "/api/v1/auth/register",
        json={
            "username": "ashwin",
            "email": "ashwin@example.com",
            "password": "SecurePass@123",
        },
    )

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "ashwin@example.com",
            "password": "SecurePass@123",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "ashwin@example.com"
    assert "hashed_password" not in response.json()


def test_health_endpoint(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
