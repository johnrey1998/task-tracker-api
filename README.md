# Task Tracker API

A task-tracking API.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- pytest

## Completed

The users domain currently includes:

- A SQLAlchemy `User` model
- Pydantic request and response schemas
- User creation and lookup services
- Password hashing, email handling, and duplicate-email handling
- Isolated SQLite tests for user services

The users domain includes API validation (Pydantic), operations/logic, ORM models (SQLAlchemy), and database persistence.

## Status

The users foundation is implemented.

Authentication and task features are still to be implemented. Alembic migrations and Docker support are planned for later.
