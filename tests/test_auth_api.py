from fastapi.testclient import TestClient

from app.config import settings

def test_login_returns_access_token(api_client: TestClient) -> None:
    user_data = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "password": "janedoe123",
    }

    register_response = api_client.post(
        f"{settings.api_prefix}/users/",
        json=user_data
    )

    assert register_response.status_code == 201

    response = api_client.post(
        f"{settings.api_prefix}/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"]
        }
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]

def test_login_rejects_invalid_credentials(api_client: TestClient) -> None:
    response = api_client.post(
        f"{settings.api_prefix}/auth/login",
        json={
            "email": "unknown@unknown.com",
            "password": "wrong-password"
        }
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid email or password"
    }
    assert response.headers["www-authenticate"] == "Bearer"

