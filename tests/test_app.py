from unittest.mock import MagicMock

import bcrypt
import jwt
import psycopg
import pytest
from fastapi.testclient import TestClient

from task_tracker_api.app import JWT_SECRET, app, get_current_user, get_db

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


def test_register_duplicate_email():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.execute.side_effect = psycopg.errors.UniqueViolation()

    app.dependency_overrides[get_db] = lambda: db
    try:
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "password",
            },
        )

        assert response.status_code == 409
        assert response.json() == {"detail": "Email already registered"}
        db.rollback.assert_called_once()
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


def test_login_invalid_password():
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
            json={"email": "test@example.com", "password": "wrong"},
        )

        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid credentials"}
    finally:
        app.dependency_overrides.clear()


def test_get_current_user_valid_token():
    token = jwt.encode({"sub": "1"}, JWT_SECRET, algorithm="HS256")

    assert get_current_user(token) == 1


def test_get_current_user_invalid_token():
    with pytest.raises(Exception) as error:
        get_current_user("not-a-valid-token")

    assert error.value.status_code == 401