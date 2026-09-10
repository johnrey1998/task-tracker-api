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


def test_create_task_success():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1, 1, "First task", "Test task creation")

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1
    try:
        response = client.post(
            "/tasks",
            json={
                "title": "First task",
                "description": "Test task creation",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 201
        assert response.json() == {
            "id": 1,
            "user_id": 1,
            "title": "First task",
            "description": "Test task creation",
        }
        db.commit.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_get_tasks_success():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        (1, 1, "First task", "Test task creation"),
        (2, 1, "Second task", "Another task"),
    ]

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1
    try:
        response = client.get(
            "/tasks",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 1,
                "user_id": 1,
                "title": "First task",
                "description": "Test task creation",
            },
            {
                "id": 2,
                "user_id": 1,
                "title": "Second task",
                "description": "Another task",
            },
        ]
    finally:
        app.dependency_overrides.clear()


def test_update_task_success():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = (1, 1, "Updated task", "Updated description")

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1
    try:
        response = client.patch(
            "/tasks/1",
            json={
                "title": "Updated task",
                "description": "Updated description",
            },
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        assert response.json() == {
            "id": 1,
            "user_id": 1,
            "title": "Updated task",
            "description": "Updated description",
        }
        db.commit.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_update_task_not_found():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchone.return_value = None

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1
    try:
        response = client.patch(
            "/tasks/999",
            json={"title": "Missing", "description": "Missing"},
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}
        db.commit.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_delete_task_success():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.rowcount = 1

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1
    try:
        response = client.delete(
            "/tasks/1",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 204
        assert response.content == b""
        db.commit.assert_called_once()
    finally:
        app.dependency_overrides.clear()


def test_delete_task_not_found():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.rowcount = 0

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1
    try:
        response = client.delete(
            "/tasks/999",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 404
        assert response.json() == {"detail": "Task not found"}
        db.commit.assert_not_called()
    finally:
        app.dependency_overrides.clear()


def test_get_current_user_valid_token():
    token = jwt.encode({"sub": "1"}, JWT_SECRET, algorithm="HS256")

    assert get_current_user(token) == 1


def test_get_current_user_invalid_token():
    with pytest.raises(Exception) as error:
        get_current_user("not-a-valid-token")

    assert error.value.status_code == 401

def test_get_tasks_with_pagination():
    db = MagicMock()
    cursor = db.cursor.return_value.__enter__.return_value
    cursor.fetchall.return_value = [
        (2, 1, "Second task", "Second description"),
    ]

    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: 1

    try:
        response = client.get(
            "/tasks?page=2&limit=1",
            headers={"Authorization": "Bearer test-token"},
        )

        assert response.status_code == 200
        assert response.json() == [
            {
                "id": 2,
                "user_id": 1,
                "title": "Second task",
                "description": "Second description",
            }
        ]

        cursor.execute.assert_called_once()
        query_params = cursor.execute.call_args.args[1]
        assert query_params == (1, 1, 1)
    finally:
        app.dependency_overrides.clear()