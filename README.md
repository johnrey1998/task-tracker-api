# Task Tracker API

A production-ready RESTful task-tracking backend built with FastAPI, SQLAlchemy, and PostgreSQL.

## Frontend & Demo
- **Live Demo:** [Task Tracker Demo](https://task-tracker-frontend-three-gamma.vercel.app/)
- **Frontend Repository:** [Task Tracker Frontend](https://github.com/johnrey1998/task-tracker-frontend)

---

## Tech Stack
- **Framework:** FastAPI
- **Database / ORM:** PostgreSQL, SQLAlchemy, Alembic
- **Package Manager:** `uv`
- **Testing:** Pytest

---

## Getting Started

### 1. Environment Setup
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 2. Running with Docker
```bash
docker compose up --build
```
- API available at `http://localhost:8000/api/v1` (Swagger Docs at `/docs`)
- Stop containers: `docker compose down`
- Stop & wipe data: `docker compose down -v`

### 3. Running Locally
Start PostgreSQL and start the dev server:
```bash
docker compose up -d db
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload
```

---

## Database Migrations
- **Apply migrations:** `uv run alembic upgrade head`
- **Roll back:** `uv run alembic downgrade -1`
- **Create migration:** `uv run alembic revision --autogenerate -m "description"`

---

## API Endpoints (`/api/v1`)

| Method | Route | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `POST` | `/users/` | Register a user | No |
| `POST` | `/auth/login` | Login & receive JWT | No |
| `GET` | `/tasks/` | List user tasks | Yes |
| `POST` | `/tasks/` | Create a task | Yes |
| `PATCH` | `/tasks/{id}` | Update a task | Yes |
| `DELETE` | `/tasks/{id}` | Delete a task | Yes |

*Auth header format:* `Authorization: Bearer <token>`

---

## Testing

Run unit & integration tests:
```bash
uv run pytest
```

To run tests against the separate test database (`port 5433`):
```bash
docker compose -f docker-compose.test.yml up -d
uv run pytest
docker compose -f docker-compose.test.yml down -v
```


