
from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.deps import get_current_user_id
from app.database import Base, get_database
from app.tasks.models import Task
from app.users.models import User
from app.main import app

from alembic import command
from alembic.config import Config

from fastapi.testclient import TestClient

TEST_DATABASE_URL = "postgresql+psycopg://admin:password@localhost:5433/task_tracker_test"



@pytest.fixture
def database_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    try:
        with Session(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        ) as session:
            yield session
            session.rollback()
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture
def api_client() -> Iterator[TestClient]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_database() -> Iterator[Session]:
        with Session(bind=engine, autoflush=False, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_database] = override_get_database

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()

@pytest.fixture
def authenticated_api_client(api_client: TestClient) -> Iterator[TestClient]:
    app.dependency_overrides[get_current_user_id] = lambda: 1

    try:
        yield api_client
    finally:
        app.dependency_overrides.pop(get_current_user_id, None)

@pytest.fixture(scope="session")
def postgres_engine():
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url",
        TEST_DATABASE_URL
    )
    command.upgrade(alembic_config, "head")

    engine = create_engine(
        TEST_DATABASE_URL,
        pool_pre_ping=True
    )

    yield engine
    engine.dispose()



@pytest.fixture
def postgres_session(postgres_engine) -> Iterator[Session]:
    try:
        with Session(
            bind=postgres_engine,
            autoflush=False,
            expire_on_commit=False
        ) as session:
            yield session
    finally:
        with postgres_engine.begin() as connection:
            connection.execute(
                text("TRUNCATE TABLE tasks, users RESTART IDENTITY CASCADE")
            )





        

