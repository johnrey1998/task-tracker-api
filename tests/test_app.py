from unittest.mock import MagicMock

import bcrypt
from fastapi.testclient import TestClient

from task_tracker_api.app import app, get_db

client = TestClient(app)


def test_register_success():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1, "testuser", "test@example.com")

    app.dependency_overrides[get_db] = lambda: db
    try:
        res = client.post("/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password"
        })

        assert res.status_code == 201
        data = res.json()
        assert data == {"id": 1, "name": "testuser", "email": "test@example.com"}
        db.commit.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_login_success():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (
        1,
        bcrypt.hashpw(b"password", bcrypt.gensalt()).decode(),
    )

    app.dependency_overrides[get_db] = lambda: db
    try:
        response = client.post(
            "/login",
            json={"email": "test@example.com", "password": "password"},
        )

        assert response.status_code == 200
        assert response.json()["token_type"] == "bearer"
        assert response.json()["access_token"]
    finally:
        app.dependency_overrides.clear()