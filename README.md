# Task Tracker API

A RESTful task-tracking API.

## Stack

- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- pytest
- Alembic
- Docker

## Prerequisites

Install:
- Python 3.14+
- Docker and Docker Compose
- uv

## Documentation

- [HTTP status code guide](docs/http-status-codes.md)
- [ReDoc](http://localhost:8000/redoc) (when the API is running)

## Overview

Task Tracker API is a RESTful API for registering users, authenticating with JWTs, and managing tasks. The API uses PostgreSQL for persistence and Alembic for database migrations.

## Project Structure

```text
app/
├── auth/       # Authentication routes, schemas, and services
├── tasks/      # Task routes, models, schemas, and services
├── users/      # User routes, models, schemas, and services
├── config.py   # Environment-based configuration
├── database.py # SQLAlchemy engine and sessions
├── deps.py     # FastAPI dependencies
└── main.py     # FastAPI application

migrations/     # Alembic migrations
tests/          # Database, API and service tests
```

## Configuration

For local development, create `.env`:

```env
DATABASE_URL=postgresql+psycopg://admin:password@localhost:5432/task_tracker
JWT_SECRET=replace-this-with-a-long-random-secret
```

## Run With Docker

The API container receives these settings from `docker-compose.yml`:

```env
DATABASE_URL=postgresql+psycopg://admin:password@db:5432/task_tracker
JWT_SECRET=change-this-in-prod
```

Use `db` as the database hostname inside Docker. Do not use `localhost` for the container's `DATABASE_URL`; inside the API container, `localhost` refers to the API container itself.

Start the API and PostgreSQL database:

```bash
docker compose up --build
```

The API container runs the latest Alembic migrations before starting the server. The API is available at:

- API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Run the services in the background:

```bash
docker compose up --build -d
```

Stop the containers while preserving database data:

```bash
docker compose down
```

Stop the containers and delete the PostgreSQL volume and all database data:

```bash
docker compose down -v
```

Within Docker, the API connects to PostgreSQL using the hostname `db`. Tools running on the host, such as DBeaver, connect using `localhost:5432`.

## Run Locally

Start only PostgreSQL with Docker:

```bash
docker compose up -d db
```

Install Python dependencies:

```bash
uv sync
```

Apply database migrations:

```bash
uv run alembic upgrade head
```

Start the development server:

```bash
uv run uvicorn app.main:app --reload
```

## Database Migrations

Apply migrations:

```bash
uv run alembic upgrade head
```

Roll back the most recent migration:

```bash
uv run alembic downgrade -1
```

Create a migration after changing the SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "describe the change"
```

## API Routes

The API prefix is `/api/v1`.

| Method | Route | Purpose |
| --- | --- | --- |
| `POST` | `/api/v1/users/` | Register a user |
| `POST` | `/api/v1/auth/login` | Login and receive a JWT |
| `GET` | `/api/v1/tasks/` | List the authenticated user's tasks |
| `POST` | `/api/v1/tasks/` | Create a task |
| `GET` | `/api/v1/tasks/{task_id}` | Get a task |
| `PATCH` | `/api/v1/tasks/{task_id}` | Update a task |
| `DELETE` | `/api/v1/tasks/{task_id}` | Delete a task |

Authenticated requests use this header:

```http
Authorization: Bearer <access-token>
```

## Testing

Run the test suite:

```bash
uv run pytest
```

The PostgreSQL integration tests use a separate database exposed on port `5433`. Start it with:

```bash
docker compose -f docker-compose.test.yml up -d
```

The test database connection is:

```text
Host: localhost
Port: 5433
Database: task_tracker_test
Username: admin
Password: password
```

Stop the test database and remove its data:

```bash
docker compose -f docker-compose.test.yml down -v
```

## Frontend Integration

A frontend running on the host can use this base URL:

```text
http://localhost:8000/api/v1
```

Frontend repository: [Task Tracker Frontend](https://github.com/johnrey1998/task-tracker-frontend)
