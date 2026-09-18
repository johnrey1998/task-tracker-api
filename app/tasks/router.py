from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.deps import SessionDep, UserIDDep
from app.tasks.schemas import TaskCreate, TaskResponse, TaskUpdate
from app.tasks.services import (
    create_task as create_task_service,
    get_tasks as get_tasks_service,
    get_task as get_task_service,
    update_task as update_task_service,
    delete_task as delete_task_service
)

                                


router = APIRouter()

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(session: SessionDep, user_id: UserIDDep, task_data: TaskCreate) -> TaskResponse:
    return create_task_service(session, user_id, task_data)

@router.get("/", response_model=list[TaskResponse])
def get_tasks(session: SessionDep, user_id: UserIDDep) -> list[TaskResponse]:
    return get_tasks_service(session, user_id)

@router.get("/{task_id}", response_model=TaskResponse)
def get_task(session: SessionDep, user_id: UserIDDep, task_id: int) -> TaskResponse:
    task = get_task_service(session, user_id, task_id)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(session: SessionDep, user_id: UserIDDep, task_id: int, task_data: TaskUpdate) -> TaskResponse:
    task = update_task_service(session, user_id, task_id, task_data)

    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(session: SessionDep, user_id: UserIDDep, task_id: int) -> Response:
    deleted = delete_task_service(session, user_id, task_id)

    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
