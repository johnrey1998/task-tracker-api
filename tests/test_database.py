from sqlalchemy import delete, select, text
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.users.models import User
from app.tasks.models import Task
from app.users.schemas import UserCreate
from app.users.services import create_user

def test_postgres_schema_exists(postgres_session: Session) -> None:
    users_table = postgres_session.execute(
        text("SELECT to_regclass('public.users')")
    ).scalar_one()

    tasks_table = postgres_session.execute(
        text("SELECT to_regclass('public.tasks')")
    ).scalar_one()

    assert users_table == "users"
    assert tasks_table == "tasks"


def test_postgres_persists_user_and_task(postgres_session: Session) -> None:
    user = User(
        name="John Doe",
        email="john@doe.com",
        password_hash="test-hash"
    )

    postgres_session.add(user)
    postgres_session.commit()

    task = Task(
        user_id=user.id,
        title="Database task",
        description="Persisted in PostgreSQL",
    )

    postgres_session.add(task)
    postgres_session.commit()

    stored_task = postgres_session.scalar(
        select(Task).where(Task.id == task.id)
    )

    assert stored_task is not None
    assert stored_task.user_id == user.id
    assert stored_task.title == "Database task"

def test_postgres_enforces_unique_email(postgres_session: Session) -> None:
    postgres_session.add_all(
        [
            User(
                name="First User",
                email="duplicate@example.com",
                password_hash="hash-one",
            ),
            User(
                name="Second User",
                email="duplicate@example.com",
                password_hash="hash-two",
            ),
        ]
    )

    try: postgres_session.commit()
    except IntegrityError: postgres_session.rollback()
    else: raise AssertionError("PostgreSQL allowed a duplicate user email")

def test_postgres_cascades_user_delete_to_tasks(postgres_session: Session) -> None:
    user = User(
        name="Task Owner",
        email="owner@owner.com",
        password_hash="test-hash"
    )
    postgres_session.add(user)
    postgres_session.commit()

    task = Task(
        user_id=user.id,
        title="Cascaded task"
    )

    postgres_session.add(task)
    postgres_session.commit()
    task_id = task.id

    postgres_session.execute(
        delete(User).where(User.id == user.id)
    )
    postgres_session.commit()
    deleted_task = postgres_session.scalar(
        select(Task).where(Task.id == task_id)
    )

    assert deleted_task is None
    