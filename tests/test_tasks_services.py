from app.tasks.schemas import TaskCreate, TaskUpdate
from app.tasks.services import (
    create_task,
    get_tasks,
    get_task,
    update_task,
    delete_task
)

def test_create_task(database_session) -> None:
    task = create_task(
        database_session,
        user_id=1,
        task_data=TaskCreate(
            title="test-title",
            description="test-description"
        )
    )
    assert task.id is not None
    assert task.user_id == 1
    assert task.title == "test-title"
    assert task.description == "test-description"

def test_get_tasks(database_session) -> None:
    create_task(database_session, 1, TaskCreate(title="user 1 task 1"))
    create_task(database_session, 2, TaskCreate(title="user 2 task 1"))
    create_task(database_session, 1, TaskCreate(title="user 1 task 2"))

    tasks = get_tasks(database_session, user_id=1)

    assert [task.title for task in tasks] == [
        "user 1 task 1", "user 1 task 2"
    ]

def test_get_task_returns_owned_task(database_session) -> None:
    task = create_task(database_session, 1, TaskCreate(title="Find this task"))

    result = get_task(database_session, 1, task.id)

    assert result is not None

    assert result.title == "Find this task"

def test_get_task_hides_another_users_task(database_session) -> None:
    task = create_task(
        database_session,
        1,
        TaskCreate(title="Private task")

    )

    result = get_task(database_session, 2, task.id)

    assert result is None


def test_update_task_supports_partial_updates(database_session) -> None:
    task = create_task(
        database_session,
        1,
        TaskCreate(
            title="Original title",
            description="Original description"
        )
    )

    updated_task = update_task(
        database_session,
        1,
        task.id,
        TaskUpdate(title="Updated title")
    )

    assert updated_task is not None

    assert updated_task.title == "Updated title"

    assert updated_task.description == "Original description"

def test_update_task_can_clear_description(database_session) -> None:
    task = create_task(
        database_session,
        1,
        TaskCreate(title="Task", description="Remove this")
    )

    updated_task = update_task(database_session, 1, task.id, TaskUpdate(description=None))

    assert updated_task is not None
    assert updated_task.description is None

def test_update_task_returns_none_for_another_users_task(database_session) -> None:
    task = create_task(database_session, 1, TaskCreate(title="Private task"))

    result = update_task(database_session, 2, task.id, TaskUpdate(title="Should not update"))

    assert result is None

def test_delete_task_removes_owned_task(database_session) -> None:
    task = create_task(database_session, 1, TaskCreate(title="Delete this task"))

    deleted = delete_task(database_session, 1, task.id)

    assert deleted is True
    assert get_task(database_session, 1, task.id) is None

def test_delete_task_returns_false_for_another_users_task(database_session) -> None:
    task = create_task(database_session, 1, TaskCreate(title="Private task"))

    deleted = delete_task(database_session, 2, task.id)
    assert deleted is False
    assert get_task(database_session, 1, task.id) is not None