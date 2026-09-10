import os
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient

from task_tracker_api.app import app, get_db


DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://admin:password@localhost:5432/task_tracker_api_test",
)
MIGRATION_PATH = Path(__file__).parents[1] / "migrations" / "001_initial.sql"


@pytest.fixture(scope="session")
def database_connection():
    """Provide a connection to the PostgreSQL database used by integration tests."""
    try:
        connection = psycopg.connect(DATABASE_URL)
    except psycopg.OperationalError as exc:
        pytest.skip(f"Integration database is unavailable: {exc}")

    connection.execute(MIGRATION_PATH.read_text())
    connection.commit()

    yield connection
    connection.close()


@pytest.fixture(autouse=True)
def clean_database(database_connection):
    """Start each integration test with empty tables."""
    with database_connection.cursor() as cursor:
        cursor.execute("TRUNCATE tasks, users RESTART IDENTITY CASCADE")
        database_connection.commit()


@pytest.fixture
def client(database_connection):
    """Create an API client configured to use the integration-test database."""
    app.dependency_overrides[get_db] = lambda: database_connection
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Register and return a user for an integration test."""
    response = client.post(
        "/register",
        json={
            "username": "integration-user",
            "email": "integration@example.com",
            "password": "test-password",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def auth_headers(client, registered_user):
    """Return bearer headers for the registered integration-test user."""
    response = client.post(
        "/login",
        json={
            "email": "integration@example.com",
            "password": "test-password",
        },
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.mark.integration
def test_authenticated_task_workflow(client, auth_headers):
    """Exercise task creation, retrieval, update, and deletion through the API."""
    create_response = client.post(
        "/tasks",
        json={
            "title": "Integration task",
            "description": "Created against PostgreSQL",
        },
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    created_task = create_response.json()
    assert created_task["title"] == "Integration task"
    assert created_task["description"] == "Created against PostgreSQL"

    task_id = created_task["id"]
    list_response = client.get("/tasks", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json() == [created_task]

    update_response = client.patch(
        f"/tasks/{task_id}",
        json={"title": "Updated task", "description": "Updated in PostgreSQL"},
        headers=auth_headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated task"

    delete_response = client.delete(
        f"/tasks/{task_id}",
        headers=auth_headers,
    )
    assert delete_response.status_code == 204
    assert client.get("/tasks", headers=auth_headers).json() == []


@pytest.mark.integration
def test_user_cannot_access_another_users_tasks(client, auth_headers):
    """Ensure task ownership prevents another user from changing or deleting it."""
    create_response = client.post(
        "/tasks",
        json={"title": "Private task", "description": "Owned by user one"},
        headers=auth_headers,
    )
    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    second_user = client.post(
        "/register",
        json={
            "username": "second-user",
            "email": "second@example.com",
            "password": "second-password",
        },
    )
    assert second_user.status_code == 201

    second_login = client.post(
        "/login",
        json={"email": "second@example.com", "password": "second-password"},
    )
    assert second_login.status_code == 200
    second_headers = {
        "Authorization": f"Bearer {second_login.json()['access_token']}"
    }

    assert client.get("/tasks", headers=second_headers).json() == []
    assert client.patch(
        f"/tasks/{task_id}",
        json={"title": "Hijacked", "description": "Should fail"},
        headers=second_headers,
    ).status_code == 404
    assert client.delete(
        f"/tasks/{task_id}",
        headers=second_headers,
    ).status_code == 404


@pytest.mark.integration
def test_task_pagination(client, auth_headers):
    for index in range(5):
        response = client.post(
            "/tasks",
            json={
                "title": f"Task {index + 1}",
                "description": f"Description {index + 1}",
            },
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get(
        "/tasks?page=2&limit=2",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == [
        "Task 3",
        "Task 4",
    ]

@pytest.mark.integration
def test_task_filtering(client, auth_headers):
    tasks = [
        {"title": "Write report", "description": "Prepare monthly report"},
        {"title": "Buy groceries", "description": "Buy milk and bread"},
        {"title": "Review report", "description": "Check the report data"},
    ]

    for task in tasks:
        response = client.post(
            "/tasks",
            json=task,
            headers=auth_headers,
        )
        assert response.status_code == 201

    response = client.get(
        "/tasks?search=report",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert [task["title"] for task in response.json()] == ["Write report", "Review report"]