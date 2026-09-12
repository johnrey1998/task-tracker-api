from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.tasks.models import Task
from app.users.models import User

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

        

