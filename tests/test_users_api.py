from fastapi.testclient import TestClient
from app.config import settings

def test_register_user(api_client: TestClient) -> None:
    response = api_client.post(
        f"{settings.api_prefix}/users/",
        json={
            "name": "John Doe",
            "email": "johndoe@example.com",
            "password": "janedoe123" 
        }
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "name": "John Doe",
        "email": "johndoe@example.com"
    }

def test_register_duplicate_email_returns_409(api_client: TestClient) -> None:
    user_data = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "password": "janedoe123" 
    }

    first_response = api_client.post(
        f"{settings.api_prefix}/users/",
        json=user_data,
    )
    second_response = api_client.post(
        f"{settings.api_prefix}/users/",
        json=user_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409

def test_register_user_rejects_invalid_data(api_client: TestClient) -> None:
    response = api_client.post(
        f"{settings.api_prefix}/users/",
        json={},
    )
    assert response.status_code == 422

