
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.tasks.models import Task
from app.tasks.schemas import TaskCreate, TaskUpdate


def create_task(session: Session, user_id: int, task_data: TaskCreate) -> Task:
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description
    )

    session.add(task)
    session.commit()

    return task

def get_tasks(session: Session, user_id: int) -> list[Task]:
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.id)
    )

    return list(session.scalars(statement).all())

def get_task(session: Session, user_id: int, task_id: int) -> Task | None:
    statement = select(Task).where(
        Task.user_id == user_id,
        Task.id == task_id,
    )

    return session.scalar(statement)

def update_task(session: Session, user_id: int, task_id: int, task_data: TaskUpdate) -> Task | None:
    task = get_task(session, user_id, task_id)

    if task is None:
        return None

    updates = task_data.model_dump(exclude_unset=True)

    for field, value in updates.items():
        setattr(task, field, value)

    session.commit()

    return task

def delete_task(session: Session, user_id: int, task_id: int) -> bool:
    task = get_task(session, user_id, task_id)
    if task is None:
        return False

    session.delete(task)
    session.commit()

    return True

