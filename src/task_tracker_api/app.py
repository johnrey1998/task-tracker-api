import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import psycopg
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "task_tracker_api")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-this-secret")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")


def get_db():
    with psycopg.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    ) as connection:
        yield connection


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@app.post("/register")
def register(user: RegisterRequest, connection=Depends(get_db)):
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
                RETURNING id, name, email
                """,
                (user.username, user.email, password_hash),
            )
            row = cursor.fetchone()
            connection.commit()
    except psycopg.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")

    return {"id": row[0], "name": row[1], "email": row[2]}


@app.post("/login")
def login(user: LoginRequest, connection=Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, password_hash FROM users WHERE email = %s",
            (user.email,),
        )
        row = cursor.fetchone()

    if not row or not bcrypt.checkpw(user.password.encode(), row[1].encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode(
        {
            "sub": str(row[0]),
            "exp": datetime.now(timezone.utc) + timedelta(hours=8),
        },
        JWT_SECRET,
        algorithm="HS256",
    )
    return {"access_token": token, "token_type": "bearer"}

class TaskCreateRequest(BaseModel):
    title: str
    description: str

class TaskUpdateRequest(BaseModel):
    title: str
    description: str


@app.post("/tasks")
def create_task(task: TaskCreateRequest, user_id: int = Depends(get_current_user), connection=Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO tasks (user_id, title, description)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, title, description
            """,
            (user_id, task.title, task.description),
        )
        row = cursor.fetchone()
        connection.commit()

    return {
        "id": row[0],
        "user_id": row[1],
        "title": row[2],
        "description": row[3],
    }

@app.get("/tasks")
def get_tasks(
    user_id: int = Depends(get_current_user),
    connection=Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, user_id, title, description
            FROM tasks
            WHERE user_id = %s
            ORDER BY id
            """,
            (user_id,),
        )
        rows = cursor.fetchall()

    return [
        {
            "id": row[0],
            "user_id": row[1],
            "title": row[2],
            "description": row[3],
        }
        for row in rows
    ]

@app.patch("/tasks/{task_id}")
def update_task(
    task_id: int,
    task: TaskUpdateRequest,
    user_id: int = Depends(get_current_user),
    connection=Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE tasks
            SET title = %s, description = %s
            WHERE id = %s AND user_id = %s
            RETURNING id, user_id, title, description
            """,
            (task.title, task.description, task_id, user_id),
        )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")
        connection.commit()

    return {
        "id": row[0],
        "user_id": row[1],
        "title": row[2],
        "description": row[3],
    }

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user),
    connection=Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM tasks WHERE id = %s AND user_id = %s",
            (task_id, user_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        connection.commit()


