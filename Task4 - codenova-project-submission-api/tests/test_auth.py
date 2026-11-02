import time
from datetime import timedelta
import jwt
from app.core.config import settings
from app.core.security import create_access_token


def test_login_success(client, admin_user, admin_credentials):
    """Valid credentials return a signed JWT token."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"],
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    # Verify token payload
    decoded = jwt.decode(
        data["access_token"],
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM],
    )
    assert decoded["sub"] == admin_credentials["username"]


def test_login_invalid_password(client, admin_user, admin_credentials):
    """Incorrect password returns 401 Unauthorized with generic message."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": "WrongPassword!",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert "Invalid username or password" in response.json()["error"]["message"]


def test_login_nonexistent_user(client, db_session):
    """Non-existent username returns 401 Unauthorized without leaking account existence."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": "nonexistent_admin",
            "password": "AnyPassword123!",
        },
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert "Invalid username or password" in response.json()["error"]["message"]


def test_password_not_stored_as_plaintext(admin_user, admin_credentials):
    """Database record must store an Argon2 hash, never the plaintext password."""
    assert admin_user.password_hash != admin_credentials["password"]
    assert admin_user.password_hash.startswith("$argon2")


def test_password_hash_not_exposed_in_token(client, admin_user, admin_credentials):
    """Token payload must never contain password or password hashes."""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "username": admin_credentials["username"],
            "password": admin_credentials["password"],
        },
    )
    token = response.json()["access_token"]
    decoded = jwt.decode(token, options={"verify_signature": False})
    assert "password" not in decoded
    assert "password_hash" not in decoded


def test_missing_token_on_protected_route(client):
    """Requesting protected admin route without authorization header returns 401."""
    response = client.get("/api/v1/admin/submissions")
    assert response.status_code == 401


def test_invalid_token_on_protected_route(client):
    """Requesting protected admin route with an invalid token returns 401."""
    response = client.get(
        "/api/v1/admin/submissions",
        headers={"Authorization": "Bearer invalid.malformed.token"},
    )
    assert response.status_code == 401


def test_expired_token_on_protected_route(client, admin_user):
    """Expired tokens must be rejected with 401."""
    expired_token = create_access_token(
        data={"sub": admin_user.username},
        expires_delta=timedelta(seconds=-10),
    )
    response = client.get(
        "/api/v1/admin/submissions",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
    assert "expired" in response.json()["error"]["message"].lower()

