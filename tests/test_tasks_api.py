from fastapi.testclient import TestClient
from app.config import settings

def test_tasks_require_authentication(api_client: TestClient) -> None:
    response = api_client.get(f"{settings.api_prefix}/tasks/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

def test_create_task(authenticated_api_client: TestClient) -> None:
    response = authenticated_api_client.post(
        f"{settings.api_prefix}/tasks/",
        json={
            "title": "Write API tests",
            "description": "Verify task creation"
        }
    )
    assert response.status_code == 201

    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "title": "Write API tests",
        "description": "Verify task creation"
    }

def test_get_tasks(authenticated_api_client: TestClient) -> None:
    first = authenticated_api_client.post(
        f"{settings.api_prefix}/tasks/",
        json={
            "title": "First task",
        }
    )
    second = authenticated_api_client.post(
        f"{settings.api_prefix}/tasks/",
        json={
            "title": "Second task",
        }
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = authenticated_api_client.get(f"{settings.api_prefix}/tasks/")

    assert response.status_code == 200

    assert [task["title"] for task in response.json()] == [
        "First task",
        "Second task"

    ]


def test_get_task(authenticated_api_client: TestClient) -> None:
    create_response = authenticated_api_client.post(
        f"{settings.api_prefix}/tasks/",
        json={"title": "Find this task"}
    )
    task_id = create_response.json()["id"]

    response = authenticated_api_client.get(
        f"{settings.api_prefix}/tasks/{task_id}",
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Find this task"


def test_update_task(authenticated_api_client: TestClient) -> None:
    create_response = authenticated_api_client.post(
        f"{settings.api_prefix}/tasks/",
        json={
            "title": "Original title",
            "description": "Original description"
        }

    )
    task_id = create_response.json()["id"]

    response = authenticated_api_client.patch(
        f"{settings.api_prefix}/tasks/{task_id}",
        json={
            "title": "Updated title",
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "id": task_id,
        "user_id": 1, 
        "title": "Updated title",
        "description": "Original description"
    }

def test_delete_task(authenticated_api_client: TestClient) -> None:
    create_response = authenticated_api_client.post(
        f"{settings.api_prefix}/tasks/",
        json={"title": "Delete this task"}
        
    )

    task_id = create_response.json()["id"]

    response = authenticated_api_client.delete(
        f"{settings.api_prefix}/tasks/{task_id}",
    )

    assert response.status_code == 204
    assert response.content == b""

def test_get_missing_task_returns_404(authenticated_api_client: TestClient) -> None:
    response = authenticated_api_client.get(
        f"{settings.api_prefix}/tasks/123"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


    