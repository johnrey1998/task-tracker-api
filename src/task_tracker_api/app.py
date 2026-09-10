import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
import psycopg
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "task_tracker_api")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "change-this-secret")


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


@app.post("/register", status_code=201)
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
def create_task():
    pass

@app.get("/tasks")
def get_tasks():
    pass

@app.patch("/tasks/{task_id}")
def update_task(task_id: int):
    pass

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    pass


