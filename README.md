# Task Tracker API

## Technology Stack

- **FastAPI**: Web framework for the REST API
- **PostgreSQL**: Relational database for users and tasks

## Setup on Ubuntu

Install PostgreSQL:

```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

Install `uv`:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source "$HOME/.local/bin/env" # or restart your terminal
```

Create the PostgreSQL user and application database:

```bash
sudo -u postgres psql
```

```sql
CREATE USER admin WITH PASSWORD 'password';
CREATE DATABASE task_tracker_api OWNER admin;
\q
```

Create the test database (for integration tests):

```bash
sudo -u postgres psql -c "CREATE DATABASE task_tracker_api_test OWNER admin;"
```

Install the project dependencies from the project root:

```bash
uv sync
```

Initialize the application database:

```bash
uv run python -m task_tracker_api.db_init
```

Run the API:

```bash
uv run uvicorn task_tracker_api.app:app --reload
```

Run the tests:

```bash
uv run pytest -v
```

## Database Defaults

| Setting | Environment variable | Default value |
| --- | --- | --- |
| Host | `DB_HOST` | `localhost` |
| Database | `DB_NAME` | `task_tracker_api` |
| User | `DB_USER` | `admin` |
| Password | `DB_PASSWORD` | `password` |
| JWT | `JWT_SECRET_KEY` | `change-this-secret` |

## JWT (JSON Web Token)

After a successful log in, the API creates a JWT containing the user's
ID and signs it with `JWT_SECRET_KEY`. The user sends this token with requests
to protected endpoints. The API verifies the signature before authorizing the
user's actions like modifying or reading tasks.

## Todo

- create a frontend to complete MVP





